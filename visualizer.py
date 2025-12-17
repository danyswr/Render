import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Optional, Dict

class Visualizer:
    """Handles all visualization using Matplotlib - Clean dual view (3D Scene + 2D Camera POV)"""
    
    def __init__(self):
        plt.ion()
        self.fig = None
        self.ax_scene = None
        self.ax_camera = None
        
        self.camera_position = np.array([0.0, 0.0, -150.0])
        self.camera_rotation = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.camera_target = np.array([0.0, 0.0, 0.0])
        self.fov = 60
    
    def _ensure_figure(self):
        """Ensure dual figure exists: 3D scene (left) + 2D camera POV (right)"""
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.fig = plt.figure(figsize=(14, 6))
            self.ax_scene = self.fig.add_subplot(121, projection='3d')
            self.ax_camera = self.fig.add_subplot(122)
            self.fig.tight_layout(pad=3.0)
        else:
            self.ax_scene.clear()
            self.ax_camera.clear()
    
    def set_camera_position(self, x: float, y: float, z: float):
        self.camera_position = np.array([x, y, z])
    
    def set_camera_rotation(self, rot_x: float, rot_y: float, rot_z: float):
        self.camera_rotation = {"x": rot_x, "y": rot_y, "z": rot_z}
    
    def set_camera_target(self, x: float, y: float, z: float):
        self.camera_target = np.array([x, y, z])
    
    def _add_grid_3d(self, ax, limit=50):
        """Add simple grid to 3D axis"""
        ax.set_xlabel('X', fontsize=10, color='red')
        ax.set_ylabel('Y', fontsize=10, color='green')
        ax.set_zlabel('Z', fontsize=10, color='blue')
        ax.grid(True, alpha=0.3, linestyle='-')
        
        ax.set_xlim([-limit, limit])
        ax.set_ylim([-limit, limit])
        ax.set_zlim([-limit, limit])
    
    def _draw_camera_indicator(self, ax, limit=50):
        """Draw camera as simple pyramid/cone shape"""
        cam_x, cam_y, cam_z = self.camera_position
        
        ax.scatter([cam_x], [cam_y], [cam_z], c='purple', s=100, marker='s', label='Kamera')
        
        forward = np.array([0, 0, 1])
        rx = np.radians(self.camera_rotation['x'])
        ry = np.radians(self.camera_rotation['y'])
        rz = np.radians(self.camera_rotation['z'])
        
        Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
        Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
        Rz = np.array([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]])
        R = Rz @ Ry @ Rx
        
        forward = R @ forward
        arrow_len = min(limit * 0.3, 25)
        
        ax.quiver(cam_x, cam_y, cam_z, 
                  forward[0]*arrow_len, forward[1]*arrow_len, forward[2]*arrow_len,
                  color='purple', arrow_length_ratio=0.2, linewidth=2)
    
    def _get_camera_transform(self):
        """Get camera transformation matrix"""
        cam_pos = self.camera_position
        cam_rot = self.camera_rotation
        
        rx_rad = np.radians(cam_rot['x'])
        ry_rad = np.radians(cam_rot['y'])
        rz_rad = np.radians(cam_rot['z'])
        
        Rx = np.array([[1,0,0],[0,np.cos(rx_rad),-np.sin(rx_rad)],[0,np.sin(rx_rad),np.cos(rx_rad)]])
        Ry = np.array([[np.cos(ry_rad),0,np.sin(ry_rad)],[0,1,0],[-np.sin(ry_rad),0,np.cos(ry_rad)]])
        Rz = np.array([[np.cos(rz_rad),-np.sin(rz_rad),0],[np.sin(rz_rad),np.cos(rz_rad),0],[0,0,1]])
        R_cam = Rz @ Ry @ Rx
        R_cam_inv = R_cam.T
        
        return R_cam_inv, cam_pos
    
    def _project_to_2d(self, world_point, R_cam_inv, cam_pos):
        """Project 3D world point to 2D camera view"""
        translated = np.array(world_point) - cam_pos
        cam_space = R_cam_inv @ translated
        
        z = cam_space[2]
        if z <= 0.1:
            return None, None, False
        
        fov_rad = np.radians(self.fov)
        f = 1.0 / np.tan(fov_rad / 2)
        
        x_2d = (cam_space[0] / z) * f
        y_2d = (cam_space[1] / z) * f
        
        return x_2d, y_2d, True
    
    def _draw_camera_pov_2d(self, ax, objects_positions: List[List[float]], rotations: List[Dict] = None):
        """Draw clean 2D camera POV with white background and simple grid"""
        R_cam_inv, cam_pos = self._get_camera_transform()
        
        ax.set_facecolor('white')
        ax.set_xlim([-2, 2])
        ax.set_ylim([-1.5, 1.5])
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, linestyle='-', color='gray')
        ax.axhline(y=0, color='gray', linewidth=0.5, alpha=0.5)
        ax.axvline(x=0, color='gray', linewidth=0.5, alpha=0.5)
        
        ax.set_xlabel('X', fontsize=9)
        ax.set_ylabel('Y', fontsize=9)
        
        if len(objects_positions) > 0:
            projected = []
            for i, point in enumerate(objects_positions):
                x_2d, y_2d, visible = self._project_to_2d(point, R_cam_inv, cam_pos)
                if visible:
                    rot = rotations[i] if rotations and i < len(rotations) else {"x": 0, "y": 0, "z": 0}
                    projected.append((x_2d, y_2d, i, point, rot))
            
            if len(projected) > 1:
                xs = [p[0] for p in projected]
                ys = [p[1] for p in projected]
                ax.plot(xs, ys, 'k-', linewidth=1, alpha=0.5)
            
            for x_2d, y_2d, idx, world_pt, rot in projected:
                self._draw_oriented_circle_2d(ax, x_2d, y_2d, 0.15, rot)
                
                if idx == 0:
                    label = "START"
                elif idx == len(objects_positions) - 1 and len(objects_positions) > 1:
                    label = "END"
                else:
                    label = f"P{idx}"
                ax.annotate(label, (x_2d, y_2d), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8, fontweight='bold')
        
        origin_x, origin_y, visible = self._project_to_2d([0, 0, 0], R_cam_inv, cam_pos)
        if visible:
            ax.plot(origin_x, origin_y, 'k+', markersize=10, markeredgewidth=2)
            ax.annotate('O', (origin_x, origin_y), xytext=(-10, -10), 
                       textcoords='offset points', fontsize=8, color='gray')
        
        cam_rot = self.camera_rotation
        title = f'Sudut Pandang Kamera (2D)\n'
        title += f'Pos: ({self.camera_position[0]:.0f}, {self.camera_position[1]:.0f}, {self.camera_position[2]:.0f}) | '
        title += f'Rot: ({cam_rot["x"]:.0f}, {cam_rot["y"]:.0f}, {cam_rot["z"]:.0f})'
        ax.set_title(title, fontsize=10)
    
    def _draw_oriented_circle_2d(self, ax, cx, cy, radius, rotation):
        """Draw a simple oriented circle in 2D with color sections"""
        theta = np.linspace(0, 2*np.pi, 100)
        
        rot_z = np.radians(rotation.get('z', 0) + rotation.get('y', 0))
        
        for i, angle in enumerate(theta[:-1]):
            x1 = cx + radius * np.cos(angle + rot_z)
            y1 = cy + radius * np.sin(angle + rot_z)
            x2 = cx + radius * np.cos(theta[i+1] + rot_z)
            y2 = cy + radius * np.sin(theta[i+1] + rot_z)
            
            base_angle = angle
            if -np.pi/4 <= base_angle <= np.pi/4:
                color = 'red'
            elif np.pi/4 < base_angle <= 3*np.pi/4:
                color = 'green'
            elif -3*np.pi/4 <= base_angle < -np.pi/4:
                color = 'blue'
            else:
                color = 'yellow'
            
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=3)
        
        front_x = cx + radius * 1.3 * np.cos(rot_z)
        front_y = cy + radius * 1.3 * np.sin(rot_z)
        ax.plot([cx, front_x], [cy, front_y], 'r-', linewidth=2)
    
    def _draw_oriented_sphere(self, ax, position: List[float], radius: float, rotation: Dict):
        """Draw colored sphere showing orientation - DEPAN(merah) BELAKANG(kuning) KIRI(biru) KANAN(hijau)"""
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        
        x_sphere = radius * np.outer(np.cos(u), np.sin(v))
        y_sphere = radius * np.outer(np.sin(u), np.sin(v))
        z_sphere = radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        rx = np.radians(rotation.get('x', 0))
        ry = np.radians(rotation.get('y', 0))
        rz = np.radians(rotation.get('z', 0))
        
        Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
        Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
        Rz = np.array([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]])
        R = Rz @ Ry @ Rx
        
        points = np.stack([x_sphere.flatten(), y_sphere.flatten(), z_sphere.flatten()])
        rotated = R @ points
        x_rot = position[0] + rotated[0].reshape(x_sphere.shape)
        y_rot = position[1] + rotated[1].reshape(y_sphere.shape)
        z_rot = position[2] + rotated[2].reshape(z_sphere.shape)
        
        colors = np.zeros(x_sphere.shape + (4,))
        for i in range(len(u)):
            angle = u[i]
            if -np.pi/4 <= angle <= np.pi/4:
                colors[i, :] = [1.0, 0.2, 0.2, 0.9]
            elif np.pi/4 < angle <= 3*np.pi/4:
                colors[i, :] = [0.2, 0.8, 0.2, 0.9]
            elif -3*np.pi/4 <= angle < -np.pi/4:
                colors[i, :] = [0.2, 0.2, 1.0, 0.9]
            else:
                colors[i, :] = [1.0, 0.9, 0.2, 0.9]
        
        ax.plot_surface(x_rot, y_rot, z_rot, facecolors=colors, shade=True)
    
    def show_translation_with_sphere(self, points: List[List[float]], current_point: Optional[List[float]] = None, rotations: List[Dict] = None):
        """Show translation path with oriented spheres - clean view"""
        self._ensure_figure()
        
        all_coords = []
        if len(points) > 0:
            all_coords.extend(points)
        if current_point is not None:
            all_coords.append(current_point)
        all_coords.append(self.camera_position.tolist())
        
        if len(all_coords) > 0:
            coords_array = np.array(all_coords)
            max_coord = max(np.abs(coords_array).max() + 20, 50)
        else:
            max_coord = 50
        
        limit = int(max_coord)
        
        self._add_grid_3d(self.ax_scene, limit)
        
        if rotations is None:
            rotations = [{"x": 0, "y": 0, "z": 0} for _ in range(len(points) + (1 if current_point else 0))]
        
        if len(points) > 0:
            for i, point in enumerate(points):
                rot = rotations[i] if i < len(rotations) else {"x": 0, "y": 0, "z": 0}
                self._draw_oriented_sphere(self.ax_scene, point, 5, rot)
                
                if i == 0:
                    label = "START"
                elif i == len(points) - 1 and len(points) > 1:
                    label = "END"
                else:
                    label = f"P{i}"
                self.ax_scene.text(point[0]+3, point[1]+3, point[2]+3, label, fontsize=9, fontweight='bold')
            
            if len(points) > 1:
                pts = np.array(points)
                self.ax_scene.plot(pts[:, 0], pts[:, 1], pts[:, 2], 'k-', linewidth=1, alpha=0.5)
        
        if current_point is not None:
            rot = rotations[len(points)] if len(points) < len(rotations) else {"x": 0, "y": 0, "z": 0}
            self._draw_oriented_sphere(self.ax_scene, current_point, 6, rot)
            self.ax_scene.text(current_point[0]+3, current_point[1]+3, current_point[2]+3, 
                              'BARU', fontsize=9, fontweight='bold', color='orange')
            
            if len(points) > 0:
                last = points[-1]
                self.ax_scene.plot([last[0], current_point[0]], 
                                   [last[1], current_point[1]], 
                                   [last[2], current_point[2]], 
                                   'k--', linewidth=1, alpha=0.5)
        
        self._draw_camera_indicator(self.ax_scene, limit)
        
        self.ax_scene.set_title('Scene 3D\nMERAH=Depan, HIJAU=Kanan, BIRU=Kiri, KUNING=Belakang', fontsize=10)
        
        self._draw_camera_pov_2d(self.ax_camera, points + ([current_point] if current_point else []), rotations)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_translation_path(self, points: List[List[float]]):
        self.show_translation_with_sphere(points, None)
    
    def show_scale_preview(self, position: List[float], scale: float, rotation: Dict = None):
        """Show scale preview with oriented sphere"""
        self._ensure_figure()
        
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}
        
        radius = max(scale * 6, 3)
        self._draw_oriented_sphere(self.ax_scene, position, radius, rotation)
        
        max_range = max(np.abs(position).max() + radius * 2, np.abs(self.camera_position).max(), 50)
        self._add_grid_3d(self.ax_scene, int(max_range))
        self._draw_camera_indicator(self.ax_scene, int(max_range))
        
        title = f'Preview Skala: {scale:.2f}x\n'
        title += f'Posisi: ({position[0]:.0f}, {position[1]:.0f}, {position[2]:.0f})'
        self.ax_scene.set_title(title, fontsize=10)
        
        self._draw_camera_pov_2d(self.ax_camera, [position], [rotation])
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_rotation_at_position(self, position: List[float], rot_x: float, rot_y: float, rot_z: float, point_label: str = ""):
        """Show rotation preview with oriented sphere"""
        self._ensure_figure()
        
        rotation = {"x": rot_x, "y": rot_y, "z": rot_z}
        self._draw_oriented_sphere(self.ax_scene, position, 8, rotation)
        
        max_range = max(np.abs(position).max() + 20, np.abs(self.camera_position).max(), 50)
        self._add_grid_3d(self.ax_scene, int(max_range))
        self._draw_camera_indicator(self.ax_scene, int(max_range))
        
        title = f'Preview Rotasi - {point_label}\n'
        title += f'X:{rot_x:.0f}° Y:{rot_y:.0f}° Z:{rot_z:.0f}°'
        self.ax_scene.set_title(title, fontsize=10)
        
        self._draw_camera_pov_2d(self.ax_camera, [position], [rotation])
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_rotation_preview(self, rot_x: float, rot_y: float, rot_z: float):
        """Show rotation preview at origin"""
        self.show_rotation_at_position([0, 0, 0], rot_x, rot_y, rot_z, "Origin")
    
    def show_camera_setup(self, object_positions: List[List[float]]):
        """Show camera setup view"""
        self._ensure_figure()
        
        all_coords = object_positions.copy() if object_positions else []
        all_coords.append(self.camera_position.tolist())
        
        coords_array = np.array(all_coords)
        max_coord = max(np.abs(coords_array).max() + 30, 50)
        limit = int(max_coord)
        
        self._add_grid_3d(self.ax_scene, limit)
        
        rotations = [{"x": 0, "y": 0, "z": 0} for _ in object_positions]
        for i, pos in enumerate(object_positions):
            self._draw_oriented_sphere(self.ax_scene, pos, 5, rotations[i])
            self.ax_scene.text(pos[0]+3, pos[1]+3, pos[2]+3, f'P{i}', fontsize=9)
        
        self._draw_camera_indicator(self.ax_scene, limit)
        
        self.ax_scene.set_title('Pengaturan Kamera\nMERAH=Depan, HIJAU=Kanan, BIRU=Kiri, KUNING=Belakang', fontsize=10)
        
        self._draw_camera_pov_2d(self.ax_camera, object_positions, rotations)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def save_current(self, filename: str):
        if self.fig is not None:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
    
    def close(self):
        plt.ioff()
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax_scene = None
            self.ax_camera = None

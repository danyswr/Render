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
        """Draw camera as bigger sphere with direction arrow"""
        cam_x, cam_y, cam_z = self.camera_position
        
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 15)
        cam_radius = max(limit * 0.12, 12)
        sphere_x = cam_x + cam_radius * np.outer(np.cos(u), np.sin(v))
        sphere_y = cam_y + cam_radius * np.outer(np.sin(u), np.sin(v))
        sphere_z = cam_z + cam_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(sphere_x, sphere_y, sphere_z, color='purple', alpha=0.8)
        
        forward = np.array([0, 0, 1])
        rx = np.radians(self.camera_rotation['x'])
        ry = np.radians(self.camera_rotation['y'])
        rz = np.radians(self.camera_rotation['z'])
        
        Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
        Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
        Rz = np.array([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]])
        R = Rz @ Ry @ Rx
        
        forward = R @ forward
        arrow_len = max(limit * 0.25, 20)
        
        ax.quiver(cam_x, cam_y, cam_z, 
                  forward[0]*arrow_len, forward[1]*arrow_len, forward[2]*arrow_len,
                  color='purple', arrow_length_ratio=0.15, linewidth=3)
        
        ax.text(cam_x, cam_y, cam_z + cam_radius + 5, 'KAMERA', fontsize=9, 
                fontweight='bold', color='purple', ha='center')
    
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
            return None, None, None, False
        
        fov_rad = np.radians(self.fov)
        f = 1.0 / np.tan(fov_rad / 2)
        
        x_2d = (cam_space[0] / z) * f
        y_2d = (cam_space[1] / z) * f
        
        return x_2d, y_2d, cam_space, True
    
    def _get_visible_color_from_camera(self, world_pos, rotation, R_cam_inv, cam_pos):
        """Determine which color of the sphere is visible from camera perspective
        Colors match 3D sphere: DEPAN=Kuning(+Z), BELAKANG=Merah(-Z), KANAN=Hijau(+X), KIRI=Biru(-X)
        """
        translated = np.array(world_pos) - cam_pos
        cam_space = R_cam_inv @ translated
        
        if cam_space[2] <= 0:
            return 'gray'
        
        view_dir = -cam_space / np.linalg.norm(cam_space)
        
        rx = np.radians(rotation.get('x', 0))
        ry = np.radians(rotation.get('y', 0))
        rz = np.radians(rotation.get('z', 0))
        
        Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
        Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
        Rz = np.array([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]])
        R_obj = Rz @ Ry @ Rx
        
        front = R_obj @ np.array([0, 0, 1])
        back = R_obj @ np.array([0, 0, -1])
        right = R_obj @ np.array([1, 0, 0])
        left = R_obj @ np.array([-1, 0, 0])
        
        front_cam = R_cam_inv @ front
        back_cam = R_cam_inv @ back
        right_cam = R_cam_inv @ right
        left_cam = R_cam_inv @ left
        
        dots = {
            'yellow': np.dot(front_cam, view_dir),
            'red': np.dot(back_cam, view_dir),
            'green': np.dot(right_cam, view_dir),
            'blue': np.dot(left_cam, view_dir)
        }
        
        return max(dots, key=dots.get)
    
    def _draw_camera_pov_2d(self, ax, objects_positions: List[List[float]], rotations: List[Dict] = None):
        """Draw clean 2D camera POV - shows what camera sees with correct colors"""
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
                x_2d, y_2d, cam_space, visible = self._project_to_2d(point, R_cam_inv, cam_pos)
                if visible:
                    rot = rotations[i] if rotations and i < len(rotations) else {"x": 0, "y": 0, "z": 0}
                    visible_color = self._get_visible_color_from_camera(point, rot, R_cam_inv, cam_pos)
                    distance = np.linalg.norm(cam_space)
                    projected.append((x_2d, y_2d, i, point, rot, visible_color, distance))
            
            if len(projected) > 1:
                xs = [p[0] for p in projected]
                ys = [p[1] for p in projected]
                ax.plot(xs, ys, 'k-', linewidth=1, alpha=0.5)
            
            for x_2d, y_2d, idx, world_pt, rot, visible_color, distance in projected:
                size = max(0.3, 1.5 - distance / 200)
                
                circle = plt.Circle((x_2d, y_2d), size * 0.2, color=visible_color, alpha=0.9)
                ax.add_patch(circle)
                
                edge = plt.Circle((x_2d, y_2d), size * 0.2, fill=False, 
                                  edgecolor='black', linewidth=2)
                ax.add_patch(edge)
                
                if idx == 0:
                    label = "START"
                elif idx == len(objects_positions) - 1 and len(objects_positions) > 1:
                    label = "END"
                else:
                    label = f"P{idx}"
                ax.annotate(label, (x_2d, y_2d), xytext=(8, 8), 
                           textcoords='offset points', fontsize=9, fontweight='bold')
        
        
        cam_rot = self.camera_rotation
        title = f'Sudut Pandang Kamera (2D)\n'
        title += f'Pos: ({self.camera_position[0]:.0f}, {self.camera_position[1]:.0f}, {self.camera_position[2]:.0f}) | '
        title += f'Rot: ({cam_rot["x"]:.0f}, {cam_rot["y"]:.0f}, {cam_rot["z"]:.0f})'
        ax.set_title(title, fontsize=10)
    
    def _draw_oriented_sphere(self, ax, position: List[float], radius: float, rotation: Dict):
        """Draw colored sphere showing orientation
        DEPAN(+Z)=Kuning, BELAKANG(-Z)=Merah, KANAN(+X)=Hijau, KIRI(-X)=Biru
        Object faces camera (+Z direction) by default so camera sees KUNING (front)
        """
        phi = np.linspace(0, 2 * np.pi, 40)
        theta = np.linspace(0, np.pi, 30)
        
        x_sphere = radius * np.outer(np.sin(theta), np.cos(phi)).T
        y_sphere = radius * np.outer(np.sin(theta), np.sin(phi)).T
        z_sphere = radius * np.outer(np.cos(theta), np.ones(len(phi))).T
        
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
        for i in range(len(phi)):
            for j in range(len(theta)):
                local_x = x_sphere[i, j]
                local_y = y_sphere[i, j]
                local_z = z_sphere[i, j]
                
                if abs(local_z) >= abs(local_x) and abs(local_z) >= abs(local_y):
                    if local_z > 0:
                        colors[i, j] = [1.0, 0.9, 0.2, 0.9]
                    else:
                        colors[i, j] = [1.0, 0.2, 0.2, 0.9]
                elif abs(local_x) >= abs(local_y):
                    if local_x > 0:
                        colors[i, j] = [0.2, 0.8, 0.2, 0.9]
                    else:
                        colors[i, j] = [0.2, 0.2, 1.0, 0.9]
                else:
                    if local_y > 0:
                        colors[i, j] = [0.8, 0.8, 0.8, 0.9]
                    else:
                        colors[i, j] = [0.5, 0.5, 0.5, 0.9]
        
        ax.plot_surface(x_rot, y_rot, z_rot, facecolors=colors, shade=True)
    
    def show_translation_with_sphere(self, points: List[List[float]], current_point: Optional[List[float]] = None, rotations: List[Dict] = None):
        """Show translation path with oriented spheres - bigger spheres"""
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
        sphere_radius = max(limit * 0.12, 12)
        
        self._add_grid_3d(self.ax_scene, limit)
        
        if rotations is None:
            rotations = [{"x": 0, "y": 0, "z": 0} for _ in range(len(points) + (1 if current_point else 0))]
        
        if len(points) > 0:
            for i, point in enumerate(points):
                rot = rotations[i] if i < len(rotations) else {"x": 0, "y": 0, "z": 0}
                self._draw_oriented_sphere(self.ax_scene, point, sphere_radius, rot)
                
                if i == 0:
                    label = "START"
                elif i == len(points) - 1 and len(points) > 1:
                    label = "END"
                else:
                    label = f"P{i}"
                self.ax_scene.text(point[0]+sphere_radius+2, point[1]+sphere_radius+2, 
                                   point[2]+sphere_radius+2, label, fontsize=10, fontweight='bold')
            
            if len(points) > 1:
                pts = np.array(points)
                self.ax_scene.plot(pts[:, 0], pts[:, 1], pts[:, 2], 'k-', linewidth=2, alpha=0.5)
        
        if current_point is not None:
            rot = rotations[len(points)] if len(points) < len(rotations) else {"x": 0, "y": 0, "z": 0}
            self._draw_oriented_sphere(self.ax_scene, current_point, sphere_radius * 1.2, rot)
            self.ax_scene.text(current_point[0]+sphere_radius+2, current_point[1]+sphere_radius+2, 
                              current_point[2]+sphere_radius+2, 
                              'BARU', fontsize=10, fontweight='bold', color='orange')
            
            if len(points) > 0:
                last = points[-1]
                self.ax_scene.plot([last[0], current_point[0]], 
                                   [last[1], current_point[1]], 
                                   [last[2], current_point[2]], 
                                   'k--', linewidth=2, alpha=0.5)
        
        self._draw_camera_indicator(self.ax_scene, limit)
        
        self.ax_scene.set_title('Scene 3D\nKUNING=Depan, MERAH=Belakang, HIJAU=Kanan, BIRU=Kiri', fontsize=10)
        
        self._draw_camera_pov_2d(self.ax_camera, points + ([current_point] if current_point else []), rotations)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)
    
    def show_translation_path(self, points: List[List[float]]):
        self.show_translation_with_sphere(points, None)
    
    def show_scale_preview(self, position: List[float], scale: float, rotation: Dict = None):
        """Show scale preview with oriented sphere"""
        self._ensure_figure()
        
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}
        
        radius = max(scale * 12, 12)
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
        plt.pause(0.01)
    
    def show_rotation_at_position(self, position: List[float], rot_x: float, rot_y: float, rot_z: float, point_label: str = ""):
        """Show rotation preview with oriented sphere"""
        self._ensure_figure()
        
        rotation = {"x": rot_x, "y": rot_y, "z": rot_z}
        
        max_range = max(np.abs(position).max() + 30, np.abs(self.camera_position).max(), 50)
        sphere_radius = max(max_range * 0.15, 15)
        
        self._draw_oriented_sphere(self.ax_scene, position, sphere_radius, rotation)
        
        self._add_grid_3d(self.ax_scene, int(max_range))
        self._draw_camera_indicator(self.ax_scene, int(max_range))
        
        title = f'Preview Rotasi - {point_label}\n'
        title += f'X:{rot_x:.0f}° Y:{rot_y:.0f}° Z:{rot_z:.0f}°'
        self.ax_scene.set_title(title, fontsize=10)
        
        self._draw_camera_pov_2d(self.ax_camera, [position], [rotation])
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)
    
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
        sphere_radius = max(limit * 0.12, 12)
        
        self._add_grid_3d(self.ax_scene, limit)
        
        rotations = [{"x": 0, "y": 0, "z": 0} for _ in object_positions]
        for i, pos in enumerate(object_positions):
            self._draw_oriented_sphere(self.ax_scene, pos, sphere_radius, rotations[i])
            self.ax_scene.text(pos[0]+sphere_radius+2, pos[1]+sphere_radius+2, 
                              pos[2]+sphere_radius+2, f'P{i}', fontsize=10, fontweight='bold')
        
        self._draw_camera_indicator(self.ax_scene, limit)
        
        self.ax_scene.set_title('Pengaturan Kamera\nKUNING=Depan, MERAH=Belakang, HIJAU=Kanan, BIRU=Kiri', fontsize=10)
        
        self._draw_camera_pov_2d(self.ax_camera, object_positions, rotations)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)
    
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

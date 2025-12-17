import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Optional, Dict

class Visualizer:
    """Handles all visualization using Matplotlib with real-time updates - Dual View"""
    
    def __init__(self):
        plt.ion()
        self.fig = None
        self.ax_scene = None
        self.ax_camera = None
        
        self.camera_position = np.array([0.0, 0.0, -150.0])
        self.camera_rotation = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.camera_target = np.array([0.0, 0.0, 0.0])
    
    def _ensure_figure(self):
        """Ensure dual figure exists and is ready"""
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.fig = plt.figure(figsize=(16, 7))
            self.ax_scene = self.fig.add_subplot(121, projection='3d')
            self.ax_camera = self.fig.add_subplot(122, projection='3d')
            self.fig.tight_layout(pad=3.0)
        else:
            self.ax_scene.clear()
            self.ax_camera.clear()
    
    def set_camera_position(self, x: float, y: float, z: float):
        """Set camera position"""
        self.camera_position = np.array([x, y, z])
    
    def set_camera_rotation(self, rot_x: float, rot_y: float, rot_z: float):
        """Set camera rotation in degrees"""
        self.camera_rotation = {"x": rot_x, "y": rot_y, "z": rot_z}
    
    def set_camera_target(self, x: float, y: float, z: float):
        """Set camera target (what camera looks at)"""
        self.camera_target = np.array([x, y, z])
    
    def get_camera_settings(self) -> Dict:
        """Get current camera settings"""
        return {
            "position": self.camera_position.tolist(),
            "rotation": self.camera_rotation.copy(),
            "target": self.camera_target.tolist()
        }
    
    def _add_grid(self, ax, limit=50):
        """Add grid lines to help measure coordinates"""
        ax.set_xlabel('X', fontsize=12, fontweight='bold', color='red')
        ax.set_ylabel('Y', fontsize=12, fontweight='bold', color='green')
        ax.set_zlabel('Z', fontsize=12, fontweight='bold', color='blue')
        ax.grid(True, alpha=0.5, linestyle='--', linewidth=1)
        
        step = max(limit // 5, 10)
        ax.set_xticks(np.arange(-limit, limit+1, step))
        ax.set_yticks(np.arange(-limit, limit+1, step))
        ax.set_zticks(np.arange(-limit, limit+1, step))
        
        ax.set_xlim([-limit, limit])
        ax.set_ylim([-limit, limit])
        ax.set_zlim([-limit, limit])
        
        for i in np.arange(-limit, limit+1, step):
            ax.plot([i, i], [-limit, limit], [0, 0], 'k-', alpha=0.1, linewidth=0.5)
            ax.plot([-limit, limit], [i, i], [0, 0], 'k-', alpha=0.1, linewidth=0.5)
    
    def _draw_camera_outside_grid(self, ax, limit=50, target_position=None):
        """Draw camera indicator OUTSIDE the grid at fixed distance"""
        cam_x, cam_y, cam_z = self.camera_position
        
        if target_position is not None:
            target = np.array(target_position)
        else:
            target = self.camera_target
        
        dir_vec = target - self.camera_position
        dir_len = np.linalg.norm(dir_vec)
        if dir_len > 0:
            dir_vec = dir_vec / dir_len
        arrow_len = min(limit * 0.3, 30)
        
        ax.quiver(cam_x, cam_y, cam_z, 
                  dir_vec[0] * arrow_len, dir_vec[1] * arrow_len, dir_vec[2] * arrow_len,
                  color='purple', arrow_length_ratio=0.2, linewidth=4, alpha=0.95)
        
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 15)
        r = limit * 0.05
        sphere_x = cam_x + r * np.outer(np.cos(u), np.sin(v))
        sphere_y = cam_y + r * np.outer(np.sin(u), np.sin(v))
        sphere_z = cam_z + r * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(sphere_x, sphere_y, sphere_z, color='purple', alpha=0.85)
        
        ax.text(cam_x, cam_y, cam_z + r * 4, 'KAMERA', fontsize=9, fontweight='bold', 
                color='purple', ha='center')
        
        return f"Pos:({cam_x:.0f},{cam_y:.0f},{cam_z:.0f})"
    
    def _draw_camera_pov(self, ax, objects_positions: List[List[float]], limit=50):
        """Draw the camera POV view - what camera sees"""
        cam_pos = self.camera_position
        cam_rot = self.camera_rotation
        
        rx_rad = np.radians(cam_rot['x'])
        ry_rad = np.radians(cam_rot['y'])
        rz_rad = np.radians(cam_rot['z'])
        
        Rx = np.array([[1, 0, 0],
                      [0, np.cos(rx_rad), -np.sin(rx_rad)],
                      [0, np.sin(rx_rad), np.cos(rx_rad)]])
        Ry = np.array([[np.cos(ry_rad), 0, np.sin(ry_rad)],
                      [0, 1, 0],
                      [-np.sin(ry_rad), 0, np.cos(ry_rad)]])
        Rz = np.array([[np.cos(rz_rad), -np.sin(rz_rad), 0],
                      [np.sin(rz_rad), np.cos(rz_rad), 0],
                      [0, 0, 1]])
        R_cam = Rz @ Ry @ Rx
        R_cam_inv = R_cam.T
        
        def world_to_camera(world_point):
            translated = np.array(world_point) - cam_pos
            cam_space = R_cam_inv @ translated
            return cam_space
        
        self._add_grid(ax, limit)
        
        ax.plot([0], [0], [0], 'mo', markersize=10, label='Posisi Kamera')
        
        arrow_len = limit * 0.4
        ax.quiver(0, 0, 0, 0, 0, arrow_len, color='cyan', arrow_length_ratio=0.1, 
                  linewidth=3, label='Arah Pandang')
        
        if len(objects_positions) > 0:
            cam_points = []
            for point in objects_positions:
                cam_point = world_to_camera(point)
                cam_points.append(cam_point)
            
            cam_points = np.array(cam_points)
            ax.scatter(cam_points[:, 0], cam_points[:, 1], cam_points[:, 2],
                      c='red', s=200, marker='o', edgecolors='darkred', linewidths=2,
                      label='Objek (dari kamera)')
            
            if len(cam_points) > 1:
                ax.plot(cam_points[:, 0], cam_points[:, 1], cam_points[:, 2],
                       'r-', linewidth=2, alpha=0.7)
            
            for i, cp in enumerate(cam_points):
                label = "START" if i == 0 else f"P{i}"
                ax.text(cp[0]+2, cp[1]+2, cp[2]+2, label, fontsize=9, color='darkred')
        
        origin_cam = world_to_camera([0, 0, 0])
        ax.scatter([origin_cam[0]], [origin_cam[1]], [origin_cam[2]], 
                  c='yellow', s=100, marker='x', linewidths=2, label='Origin World')
        
        rot_info = f"Rot: X={cam_rot['x']:.0f}° Y={cam_rot['y']:.0f}° Z={cam_rot['z']:.0f}°"
        pos_info = f"Pos: ({cam_pos[0]:.0f}, {cam_pos[1]:.0f}, {cam_pos[2]:.0f})"
        
        title = f'SUDUT PANDANG KAMERA (POV)\n{pos_info}\n{rot_info}'
        ax.set_title(title, fontsize=11, fontweight='bold', color='purple')
        ax.legend(loc='upper right', fontsize=8)
    
    def _draw_orientation_sphere(self, ax, position: List[float], radius: float = 5):
        """Draw a colored sphere showing orientation at position"""
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = position[0] + radius * np.outer(np.cos(u), np.sin(v))
        y = position[1] + radius * np.outer(np.sin(u), np.sin(v))
        z = position[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        colors = np.zeros(x.shape + (4,))
        for i in range(len(u)):
            angle = u[i]
            if -np.pi/4 <= angle <= np.pi/4:
                colors[i, :] = [0.95, 0.2, 0.2, 0.85]
            elif np.pi/4 < angle <= 3*np.pi/4:
                colors[i, :] = [0.2, 0.85, 0.2, 0.85]
            elif -3*np.pi/4 <= angle < -np.pi/4:
                colors[i, :] = [0.3, 0.75, 0.3, 0.85]
            else:
                colors[i, :] = [0.2, 0.2, 0.95, 0.85]
        
        for j in range(len(v)):
            if v[j] < np.pi/6:
                colors[:, j] = [1.0, 0.9, 0.0, 0.9]
        
        ax.plot_surface(x, y, z, facecolors=colors, shade=True)
    
    def show_translation_with_sphere(self, points: List[List[float]], current_point: Optional[List[float]] = None):
        """Show translation path with sphere at current position - DUAL VIEW"""
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
        
        self._add_grid(self.ax_scene, limit)
        
        if len(points) > 0:
            points_array = np.array(points)
            self.ax_scene.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                           c='red', s=200, marker='o', edgecolors='darkred', linewidths=2,
                           label='Titik Dikonfirmasi')
            
            if len(points) > 1:
                self.ax_scene.plot(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                            'r-', linewidth=3, alpha=0.7)
            
            for i, point in enumerate(points):
                label = "START" if i == 0 else f"P{i}"
                self.ax_scene.text(point[0]+2, point[1]+2, point[2]+2, 
                            f'{label}\n({point[0]:.0f},{point[1]:.0f},{point[2]:.0f})', 
                            fontsize=10, fontweight='bold', color='darkred')
        
        if current_point is not None:
            self.ax_scene.scatter([current_point[0]], [current_point[1]], [current_point[2]], 
                           c='orange', s=300, marker='*', edgecolors='darkorange', linewidths=2,
                           label='Posisi Saat Ini')
            
            self._draw_orientation_sphere(self.ax_scene, current_point, radius=8)
            
            if len(points) > 0:
                last_point = points[-1]
                self.ax_scene.plot([last_point[0], current_point[0]], 
                            [last_point[1], current_point[1]], 
                            [last_point[2], current_point[2]], 
                            'orange', linewidth=2, linestyle='--', alpha=0.7)
        
        cam_info = self._draw_camera_outside_grid(self.ax_scene, limit, 
                                                   current_point if current_point else (points[-1] if points else None))
        
        title = 'TAMPILAN SCENE (3D)\n'
        title += 'UNGU = Kamera (di luar grid)\n'
        title += f'Kamera: {cam_info}'
        self.ax_scene.set_title(title, fontsize=11, fontweight='bold')
        self.ax_scene.legend(loc='upper right', fontsize=8)
        
        all_points_for_pov = points.copy() if points else []
        if current_point:
            all_points_for_pov.append(current_point)
        self._draw_camera_pov(self.ax_camera, all_points_for_pov, limit)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_translation_path(self, points: List[List[float]]):
        """Visualize translation path as connected red points with grid"""
        self.show_translation_with_sphere(points, None)
    
    def show_scale_preview(self, position: List[float], scale: float):
        """Visualize scale using colored sphere at position showing orientation - DUAL VIEW"""
        self._ensure_figure()
        
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 30)
        radius = max(scale * 8, 3)
        x = position[0] + radius * np.outer(np.cos(u), np.sin(v))
        y = position[1] + radius * np.outer(np.sin(u), np.sin(v))
        z = position[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        colors = np.zeros(x.shape + (4,))
        for i in range(len(u)):
            angle = u[i]
            if -np.pi/4 <= angle <= np.pi/4:
                colors[i, :] = [0.95, 0.2, 0.2, 0.9]
            elif np.pi/4 < angle <= 3*np.pi/4:
                colors[i, :] = [0.2, 0.85, 0.2, 0.9]
            elif -3*np.pi/4 <= angle < -np.pi/4:
                colors[i, :] = [0.3, 0.75, 0.3, 0.9]
            else:
                colors[i, :] = [0.2, 0.2, 0.95, 0.9]
        
        for j in range(len(v)):
            if v[j] < np.pi/6:
                colors[:, j] = [1.0, 0.9, 0.0, 0.95]
        
        self.ax_scene.plot_surface(x, y, z, facecolors=colors, shade=True)
        
        self.ax_scene.scatter([position[0]], [position[1]], [position[2]], 
                       c='black', s=150, marker='x', linewidths=3)
        
        max_range = max(np.abs(position).max() + radius * 2, 
                       np.abs(self.camera_position).max(), 50)
        self._add_grid(self.ax_scene, int(max_range))
        
        cam_info = self._draw_camera_outside_grid(self.ax_scene, int(max_range), position)
        
        title = f'PREVIEW SKALA: {scale:.2f}x\n'
        title += f'Posisi: ({position[0]:.0f}, {position[1]:.0f}, {position[2]:.0f})\n'
        title += f'Kamera: {cam_info}'
        self.ax_scene.set_title(title, fontsize=11, fontweight='bold')
        
        self._draw_camera_pov(self.ax_camera, [position], int(max_range))
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_rotation_at_position(self, position: List[float], rot_x: float, rot_y: float, rot_z: float, point_label: str = ""):
        """Visualize rotation at a specific position with colored sphere - DUAL VIEW"""
        self._ensure_figure()
        
        def rotation_matrix(rx, ry, rz):
            rx_rad, ry_rad, rz_rad = np.radians([rx, ry, rz])
            Rx = np.array([[1, 0, 0],
                          [0, np.cos(rx_rad), -np.sin(rx_rad)],
                          [0, np.sin(rx_rad), np.cos(rx_rad)]])
            Ry = np.array([[np.cos(ry_rad), 0, np.sin(ry_rad)],
                          [0, 1, 0],
                          [-np.sin(ry_rad), 0, np.cos(ry_rad)]])
            Rz = np.array([[np.cos(rz_rad), -np.sin(rz_rad), 0],
                          [np.sin(rz_rad), np.cos(rz_rad), 0],
                          [0, 0, 1]])
            return Rz @ Ry @ Rx
        
        R = rotation_matrix(rot_x, rot_y, rot_z)
        
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 30)
        radius = 8
        x_sphere = radius * np.outer(np.cos(u), np.sin(v))
        y_sphere = radius * np.outer(np.sin(u), np.sin(v))
        z_sphere = radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        points_flat = np.stack([x_sphere.flatten(), y_sphere.flatten(), z_sphere.flatten()])
        rotated_points = R @ points_flat
        x_rot = position[0] + rotated_points[0].reshape(x_sphere.shape)
        y_rot = position[1] + rotated_points[1].reshape(y_sphere.shape)
        z_rot = position[2] + rotated_points[2].reshape(z_sphere.shape)
        
        colors = np.zeros(x_sphere.shape + (4,))
        for i in range(len(u)):
            angle = u[i]
            if -np.pi/4 <= angle <= np.pi/4:
                colors[i, :] = [0.95, 0.2, 0.2, 0.95]
            elif np.pi/4 < angle <= 3*np.pi/4:
                colors[i, :] = [0.2, 0.85, 0.2, 0.95]
            elif -3*np.pi/4 <= angle < -np.pi/4:
                colors[i, :] = [0.3, 0.7, 0.3, 0.95]
            else:
                colors[i, :] = [0.2, 0.2, 0.95, 0.95]
        
        for j in range(len(v)):
            if v[j] < np.pi/6:
                colors[:, j] = [1.0, 0.9, 0.0, 0.95]
        
        self.ax_scene.plot_surface(x_rot, y_rot, z_rot, facecolors=colors, shade=True)
        
        arrow_length = 12
        x_end = R @ np.array([arrow_length, 0, 0])
        self.ax_scene.quiver(position[0], position[1], position[2], x_end[0], x_end[1], x_end[2], 
                      color='red', arrow_length_ratio=0.15, linewidth=3)
        
        y_end = R @ np.array([0, arrow_length, 0])
        self.ax_scene.quiver(position[0], position[1], position[2], y_end[0], y_end[1], y_end[2], 
                      color='green', arrow_length_ratio=0.15, linewidth=3)
        
        z_end = R @ np.array([0, 0, arrow_length])
        self.ax_scene.quiver(position[0], position[1], position[2], z_end[0], z_end[1], z_end[2], 
                      color='blue', arrow_length_ratio=0.15, linewidth=3)
        
        self.ax_scene.scatter([position[0]], [position[1]], [position[2]], 
                       c='black', s=100, marker='x', linewidths=2)
        
        max_range = max(np.abs(position).max() + radius * 2 + arrow_length, 
                       np.abs(self.camera_position).max(), 50)
        self._add_grid(self.ax_scene, int(max_range))
        
        cam_info = self._draw_camera_outside_grid(self.ax_scene, int(max_range), position)
        
        title = f'PREVIEW ROTASI - {point_label}\n'
        title += f'Posisi: ({position[0]:.0f}, {position[1]:.0f}, {position[2]:.0f})\n'
        title += f'X:{rot_x}° Y:{rot_y}° Z:{rot_z}° | Kamera: {cam_info}'
        self.ax_scene.set_title(title, fontsize=10, fontweight='bold')
        
        self._draw_camera_pov(self.ax_camera, [position], int(max_range))
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_rotation_preview(self, rot_x: float, rot_y: float, rot_z: float):
        """Visualize rotation using colored sphere with orientation markers - DUAL VIEW"""
        self._ensure_figure()
        
        def rotation_matrix(rx, ry, rz):
            rx_rad, ry_rad, rz_rad = np.radians([rx, ry, rz])
            
            Rx = np.array([[1, 0, 0],
                          [0, np.cos(rx_rad), -np.sin(rx_rad)],
                          [0, np.sin(rx_rad), np.cos(rx_rad)]])
            
            Ry = np.array([[np.cos(ry_rad), 0, np.sin(ry_rad)],
                          [0, 1, 0],
                          [-np.sin(ry_rad), 0, np.cos(ry_rad)]])
            
            Rz = np.array([[np.cos(rz_rad), -np.sin(rz_rad), 0],
                          [np.sin(rz_rad), np.cos(rz_rad), 0],
                          [0, 0, 1]])
            
            return Rz @ Ry @ Rx
        
        R = rotation_matrix(rot_x, rot_y, rot_z)
        
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 30)
        radius = 10
        x_sphere = radius * np.outer(np.cos(u), np.sin(v))
        y_sphere = radius * np.outer(np.sin(u), np.sin(v))
        z_sphere = radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        points = np.stack([x_sphere.flatten(), y_sphere.flatten(), z_sphere.flatten()])
        rotated_points = R @ points
        x_rot = rotated_points[0].reshape(x_sphere.shape)
        y_rot = rotated_points[1].reshape(y_sphere.shape)
        z_rot = rotated_points[2].reshape(z_sphere.shape)
        
        colors = np.zeros(x_sphere.shape + (4,))
        for i in range(len(u)):
            angle = u[i]
            if -np.pi/4 <= angle <= np.pi/4:
                colors[i, :] = [0.95, 0.2, 0.2, 0.95]
            elif np.pi/4 < angle <= 3*np.pi/4:
                colors[i, :] = [0.2, 0.85, 0.2, 0.95]
            elif -3*np.pi/4 <= angle < -np.pi/4:
                colors[i, :] = [0.3, 0.7, 0.3, 0.95]
            else:
                colors[i, :] = [0.2, 0.2, 0.95, 0.95]
        
        for j in range(len(v)):
            if v[j] < np.pi/6:
                colors[:, j] = [1.0, 0.9, 0.0, 0.95]
        
        self.ax_scene.plot_surface(x_rot, y_rot, z_rot, facecolors=colors, shade=True)
        
        arrow_length = 15
        x_end = R @ np.array([arrow_length, 0, 0])
        self.ax_scene.quiver(0, 0, 0, x_end[0], x_end[1], x_end[2], 
                      color='red', arrow_length_ratio=0.15, linewidth=4, label='Sumbu X')
        
        y_end = R @ np.array([0, arrow_length, 0])
        self.ax_scene.quiver(0, 0, 0, y_end[0], y_end[1], y_end[2], 
                      color='green', arrow_length_ratio=0.15, linewidth=4, label='Sumbu Y')
        
        z_end = R @ np.array([0, 0, arrow_length])
        self.ax_scene.quiver(0, 0, 0, z_end[0], z_end[1], z_end[2], 
                      color='blue', arrow_length_ratio=0.15, linewidth=4, label='Sumbu Z')
        
        limit = max(30, int(np.abs(self.camera_position).max()) + 20)
        self._add_grid(self.ax_scene, limit)
        
        cam_info = self._draw_camera_outside_grid(self.ax_scene, limit, [0, 0, 0])
        
        title = f'PREVIEW ROTASI\n'
        title += f'X(Pitch): {rot_x}° | Y(Yaw): {rot_y}° | Z(Roll): {rot_z}°\n'
        title += f'Kamera: {cam_info}'
        self.ax_scene.set_title(title, fontsize=11, fontweight='bold')
        self.ax_scene.legend(loc='upper right', fontsize=8)
        
        self._draw_camera_pov(self.ax_camera, [[0, 0, 0]], limit)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_camera_setup(self, object_positions: List[List[float]]):
        """Show camera setup view for adjusting camera position and rotation"""
        self._ensure_figure()
        
        all_coords = object_positions.copy() if object_positions else []
        all_coords.append(self.camera_position.tolist())
        
        coords_array = np.array(all_coords)
        max_coord = max(np.abs(coords_array).max() + 30, 50)
        limit = int(max_coord)
        
        self._add_grid(self.ax_scene, limit)
        
        if len(object_positions) > 0:
            points_array = np.array(object_positions)
            self.ax_scene.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                           c='red', s=200, marker='o', edgecolors='darkred', linewidths=2,
                           label='Titik Objek')
            
            if len(object_positions) > 1:
                self.ax_scene.plot(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                            'r-', linewidth=2, alpha=0.7)
        
        target = object_positions[0] if object_positions else [0, 0, 0]
        cam_info = self._draw_camera_outside_grid(self.ax_scene, limit, target)
        
        title = 'PENGATURAN KAMERA\n'
        title += f'Kamera: {cam_info}\n'
        title += 'Kamera UNGU di luar grid'
        self.ax_scene.set_title(title, fontsize=11, fontweight='bold')
        self.ax_scene.legend(loc='upper right', fontsize=8)
        
        self._draw_camera_pov(self.ax_camera, object_positions, limit)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def save_current(self, filename: str):
        """Save current figure to file"""
        if self.fig is not None:
            self.fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Saved visualization to: {filename}")
    
    def close(self):
        """Close the visualization window"""
        plt.ioff()
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax_scene = None
            self.ax_camera = None

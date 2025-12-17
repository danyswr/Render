import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Optional, Dict

class Visualizer:
    """Handles all visualization using Matplotlib with real-time updates - Dual View (3D Scene + 2D Camera POV)"""
    
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
            self.fig = plt.figure(figsize=(16, 7))
            self.ax_scene = self.fig.add_subplot(121, projection='3d')
            self.ax_camera = self.fig.add_subplot(122)
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
        """Add grid lines to help measure coordinates (for 3D axis)"""
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
    
    def _get_camera_transform(self):
        """Get camera transformation matrix"""
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
        
        return R_cam_inv, cam_pos
    
    def _project_to_2d(self, world_point, R_cam_inv, cam_pos):
        """Project 3D world point to 2D camera view using perspective projection"""
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
    
    def _draw_camera_pov_2d(self, ax, objects_positions: List[List[float]], current_point=None):
        """Draw 2D camera POV - what camera actually sees (like a photo/video frame)"""
        R_cam_inv, cam_pos = self._get_camera_transform()
        
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        ax.set_aspect('equal')
        ax.set_facecolor('#1a1a2e')
        
        frame = plt.Rectangle((-1.2, -0.9), 2.4, 1.8, fill=False, 
                              edgecolor='white', linewidth=3)
        ax.add_patch(frame)
        
        inner_frame = plt.Rectangle((-1.1, -0.8), 2.2, 1.6, fill=True, 
                                    facecolor='#16213e', edgecolor='#4a90d9', linewidth=1)
        ax.add_patch(inner_frame)
        
        for i in range(-10, 11, 2):
            alpha = 0.3 if i % 4 == 0 else 0.1
            ax.axhline(y=i*0.08, color='#4a90d9', alpha=alpha, linewidth=0.5, 
                      xmin=0.04, xmax=0.96)
            ax.axvline(x=i*0.11, color='#4a90d9', alpha=alpha, linewidth=0.5,
                      ymin=0.06, ymax=0.94)
        
        ax.plot([-0.05, 0.05], [0, 0], 'w-', linewidth=1, alpha=0.5)
        ax.plot([0, 0], [-0.05, 0.05], 'w-', linewidth=1, alpha=0.5)
        
        projected_points = []
        if len(objects_positions) > 0:
            for i, point in enumerate(objects_positions):
                x_2d, y_2d, visible = self._project_to_2d(point, R_cam_inv, cam_pos)
                if visible:
                    projected_points.append((x_2d, y_2d, i, point))
        
        if current_point is not None:
            x_2d, y_2d, visible = self._project_to_2d(current_point, R_cam_inv, cam_pos)
            if visible:
                projected_points.append((x_2d, y_2d, -1, current_point))
        
        if len(projected_points) > 1:
            path_points = [(p[0], p[1]) for p in projected_points if p[2] >= 0]
            if len(path_points) > 1:
                xs = [p[0] for p in path_points]
                ys = [p[1] for p in path_points]
                ax.plot(xs, ys, 'r-', linewidth=2, alpha=0.7)
        
        for x_2d, y_2d, idx, world_pt in projected_points:
            if -1.1 <= x_2d <= 1.1 and -0.8 <= y_2d <= 0.8:
                if idx == -1:
                    ax.scatter([x_2d], [y_2d], c='orange', s=250, marker='*', 
                              edgecolors='yellow', linewidths=2, zorder=10)
                    ax.annotate('BARU', (x_2d, y_2d), xytext=(5, 5), 
                               textcoords='offset points', fontsize=8, 
                               color='orange', fontweight='bold')
                elif idx == 0:
                    ax.scatter([x_2d], [y_2d], c='lime', s=200, marker='o', 
                              edgecolors='darkgreen', linewidths=2, zorder=9)
                    ax.annotate('START', (x_2d, y_2d), xytext=(5, 5), 
                               textcoords='offset points', fontsize=8, 
                               color='lime', fontweight='bold')
                else:
                    ax.scatter([x_2d], [y_2d], c='red', s=150, marker='o', 
                              edgecolors='darkred', linewidths=2, zorder=8)
                    label = f'P{idx}'
                    ax.annotate(label, (x_2d, y_2d), xytext=(5, 5), 
                               textcoords='offset points', fontsize=8, 
                               color='white', fontweight='bold')
            else:
                arrow_x = np.clip(x_2d, -1.0, 1.0)
                arrow_y = np.clip(y_2d, -0.7, 0.7)
                ax.annotate('', xy=(arrow_x, arrow_y), 
                           xytext=(0, 0),
                           arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
                ax.text(arrow_x, arrow_y, f'P{idx}(luar)', fontsize=7, color='yellow')
        
        origin_x, origin_y, origin_visible = self._project_to_2d([0, 0, 0], R_cam_inv, cam_pos)
        if origin_visible and -1.1 <= origin_x <= 1.1 and -0.8 <= origin_y <= 0.8:
            ax.scatter([origin_x], [origin_y], c='cyan', s=100, marker='x', 
                      linewidths=2, zorder=5)
            ax.annotate('ORIGIN', (origin_x, origin_y), xytext=(-30, -15), 
                       textcoords='offset points', fontsize=7, color='cyan')
        
        cam_rot = self.camera_rotation
        pos_info = f"Kamera: ({self.camera_position[0]:.0f}, {self.camera_position[1]:.0f}, {self.camera_position[2]:.0f})"
        rot_info = f"Rotasi: X={cam_rot['x']:.0f}° Y={cam_rot['y']:.0f}° Z={cam_rot['z']:.0f}°"
        
        visible_count = len([p for p in projected_points if -1.1 <= p[0] <= 1.1 and -0.8 <= p[1] <= 0.8])
        total_count = len(objects_positions) + (1 if current_point else 0)
        
        ax.text(0, 1.25, 'SUDUT PANDANG KAMERA (2D)', fontsize=12, fontweight='bold', 
               color='white', ha='center')
        ax.text(0, 1.05, pos_info, fontsize=9, color='#4a90d9', ha='center')
        ax.text(0, 0.95, rot_info, fontsize=9, color='#4a90d9', ha='center')
        
        ax.text(-1.1, -1.1, f'Terlihat: {visible_count}/{total_count} titik', 
               fontsize=9, color='lime' if visible_count == total_count else 'orange')
        
        ax.text(0.95, -1.1, f'FOV: {self.fov}°', fontsize=8, color='gray', ha='right')
        
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
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
        """Show translation path with sphere at current position - DUAL VIEW (3D + 2D POV)"""
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
                label = "START" if i == 0 else ("END" if i == len(points)-1 and len(points) > 1 else f"P{i}")
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
        
        self._draw_camera_pov_2d(self.ax_camera, points, current_point)
        
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
        
        self._draw_camera_pov_2d(self.ax_camera, [position])
        
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
        
        self._draw_camera_pov_2d(self.ax_camera, [position])
        
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
        
        self._draw_camera_pov_2d(self.ax_camera, [[0, 0, 0]])
        
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
        
        self._draw_camera_pov_2d(self.ax_camera, object_positions)
        
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

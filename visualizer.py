import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Optional

class Visualizer:
    """Handles all visualization using Matplotlib with real-time updates"""
    
    def __init__(self):
        plt.ion()
        self.fig = None
        self.ax = None
    
    def _ensure_figure(self):
        """Ensure figure exists and is ready"""
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.fig = plt.figure(figsize=(12, 9))
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax.clear()
    
    def _add_grid(self, ax, limit=50):
        """Add grid lines to help measure coordinates"""
        ax.set_xlabel('X', fontsize=14, fontweight='bold', color='red')
        ax.set_ylabel('Y', fontsize=14, fontweight='bold', color='green')
        ax.set_zlabel('Z', fontsize=14, fontweight='bold', color='blue')
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
    
    def _draw_camera_indicator(self, ax, limit=50, target_position=None):
        """Draw camera direction indicator showing where camera is viewing from"""
        elev = ax.elev if hasattr(ax, 'elev') else 30
        azim = ax.azim if hasattr(ax, 'azim') else -60
        
        elev_rad = np.radians(elev)
        azim_rad = np.radians(azim)
        
        distance = limit * 1.8
        cam_x = distance * np.cos(elev_rad) * np.cos(azim_rad)
        cam_y = distance * np.cos(elev_rad) * np.sin(azim_rad)
        cam_z = distance * np.sin(elev_rad)
        
        if target_position is not None:
            cam_x += target_position[0]
            cam_y += target_position[1]
            cam_z += target_position[2]
        
        target = target_position if target_position else [0, 0, 0]
        dir_x = target[0] - cam_x
        dir_y = target[1] - cam_y
        dir_z = target[2] - cam_z
        dir_len = np.sqrt(dir_x**2 + dir_y**2 + dir_z**2)
        arrow_len = limit * 0.4
        dir_x = dir_x / dir_len * arrow_len
        dir_y = dir_y / dir_len * arrow_len
        dir_z = dir_z / dir_len * arrow_len
        
        ax.quiver(cam_x, cam_y, cam_z, dir_x, dir_y, dir_z,
                  color='purple', arrow_length_ratio=0.25, linewidth=4, alpha=0.95)
        
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 15)
        r = limit * 0.06
        sphere_x = cam_x + r * np.outer(np.cos(u), np.sin(v))
        sphere_y = cam_y + r * np.outer(np.sin(u), np.sin(v))
        sphere_z = cam_z + r * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(sphere_x, sphere_y, sphere_z, color='purple', alpha=0.85)
        
        ax.text(cam_x, cam_y, cam_z + r * 3, 'KAMERA', fontsize=9, fontweight='bold', 
                color='purple', ha='center')
        
        self._camera_position = (cam_x, cam_y, cam_z)
        self._camera_target = target
        
        return f"Elev:{elev:.0f}° Azim:{azim:.0f}°"
    
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
        """Show translation path with sphere at current position"""
        self._ensure_figure()
        
        all_coords = []
        if len(points) > 0:
            all_coords.extend(points)
        if current_point is not None:
            all_coords.append(current_point)
        
        if len(all_coords) > 0:
            coords_array = np.array(all_coords)
            max_coord = max(np.abs(coords_array).max() + 20, 50)
        else:
            max_coord = 50
        
        self._add_grid(self.ax, int(max_coord))
        
        if len(points) > 0:
            points_array = np.array(points)
            self.ax.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                           c='red', s=200, marker='o', edgecolors='darkred', linewidths=2,
                           label='Titik Dikonfirmasi')
            
            if len(points) > 1:
                self.ax.plot(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                            'r-', linewidth=3, alpha=0.7)
            
            for i, point in enumerate(points):
                label = "START" if i == 0 else f"P{i}"
                self.ax.text(point[0]+2, point[1]+2, point[2]+2, 
                            f'{label}\n({point[0]:.0f},{point[1]:.0f},{point[2]:.0f})', 
                            fontsize=10, fontweight='bold', color='darkred')
        
        if current_point is not None:
            self.ax.scatter([current_point[0]], [current_point[1]], [current_point[2]], 
                           c='orange', s=300, marker='*', edgecolors='darkorange', linewidths=2,
                           label='Posisi Saat Ini')
            
            self._draw_orientation_sphere(self.ax, current_point, radius=8)
            
            if len(points) > 0:
                last_point = points[-1]
                self.ax.plot([last_point[0], current_point[0]], 
                            [last_point[1], current_point[1]], 
                            [last_point[2], current_point[2]], 
                            'orange', linewidth=2, linestyle='--', alpha=0.7)
        
        cam_info = self._draw_camera_indicator(self.ax, int(max_coord))
        
        title = 'JALUR TRANSLASI\n'
        title += 'Gunakan GRID untuk mengukur koordinat\n'
        title += f'KAMERA: {cam_info} | UNGU=Posisi Kamera'
        self.ax.set_title(title, fontsize=12, fontweight='bold')
        self.ax.legend(loc='upper right')
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_translation_path(self, points: List[List[float]]):
        """Visualize translation path as connected red points with grid"""
        self.show_translation_with_sphere(points, None)
    
    def show_scale_preview(self, position: List[float], scale: float):
        """Visualize scale using colored sphere at position showing orientation"""
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
        
        self.ax.plot_surface(x, y, z, facecolors=colors, shade=True)
        
        self.ax.scatter([position[0]], [position[1]], [position[2]], 
                       c='black', s=150, marker='x', linewidths=3)
        
        max_range = max(np.abs(position).max() + radius * 2, 30)
        self._add_grid(self.ax, int(max_range))
        
        cam_info = self._draw_camera_indicator(self.ax, int(max_range))
        
        title = f'PREVIEW SKALA: {scale:.2f}x\n'
        title += f'Posisi: ({position[0]:.0f}, {position[1]:.0f}, {position[2]:.0f})\n'
        title += f'KAMERA: {cam_info} | UNGU=Posisi Kamera'
        self.ax.set_title(title, fontsize=12, fontweight='bold')
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_rotation_at_position(self, position: List[float], rot_x: float, rot_y: float, rot_z: float, point_label: str = ""):
        """Visualize rotation at a specific position with colored sphere"""
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
        
        self.ax.plot_surface(x_rot, y_rot, z_rot, facecolors=colors, shade=True)
        
        arrow_length = 12
        x_end = R @ np.array([arrow_length, 0, 0])
        self.ax.quiver(position[0], position[1], position[2], x_end[0], x_end[1], x_end[2], 
                      color='red', arrow_length_ratio=0.15, linewidth=3)
        
        y_end = R @ np.array([0, arrow_length, 0])
        self.ax.quiver(position[0], position[1], position[2], y_end[0], y_end[1], y_end[2], 
                      color='green', arrow_length_ratio=0.15, linewidth=3)
        
        z_end = R @ np.array([0, 0, arrow_length])
        self.ax.quiver(position[0], position[1], position[2], z_end[0], z_end[1], z_end[2], 
                      color='blue', arrow_length_ratio=0.15, linewidth=3)
        
        self.ax.scatter([position[0]], [position[1]], [position[2]], 
                       c='black', s=100, marker='x', linewidths=2)
        
        max_range = max(np.abs(position).max() + radius * 2 + arrow_length, 30)
        self._add_grid(self.ax, int(max_range))
        
        cam_info = self._draw_camera_indicator(self.ax, int(max_range))
        
        title = f'PREVIEW ROTASI - {point_label}\n'
        title += f'Posisi: ({position[0]:.0f}, {position[1]:.0f}, {position[2]:.0f})\n'
        title += f'X:{rot_x}° Y:{rot_y}° Z:{rot_z}° | KAMERA: {cam_info}'
        self.ax.set_title(title, fontsize=11, fontweight='bold')
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_rotation_preview(self, rot_x: float, rot_y: float, rot_z: float):
        """Visualize rotation using colored sphere with orientation markers"""
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
        
        self.ax.plot_surface(x_rot, y_rot, z_rot, facecolors=colors, shade=True)
        
        arrow_length = 15
        x_end = R @ np.array([arrow_length, 0, 0])
        self.ax.quiver(0, 0, 0, x_end[0], x_end[1], x_end[2], 
                      color='red', arrow_length_ratio=0.15, linewidth=4, label='Sumbu X')
        
        y_end = R @ np.array([0, arrow_length, 0])
        self.ax.quiver(0, 0, 0, y_end[0], y_end[1], y_end[2], 
                      color='green', arrow_length_ratio=0.15, linewidth=4, label='Sumbu Y')
        
        z_end = R @ np.array([0, 0, arrow_length])
        self.ax.quiver(0, 0, 0, z_end[0], z_end[1], z_end[2], 
                      color='blue', arrow_length_ratio=0.15, linewidth=4, label='Sumbu Z')
        
        self._add_grid(self.ax, 20)
        
        cam_info = self._draw_camera_indicator(self.ax, 20)
        
        title = f'PREVIEW ROTASI\n'
        title += f'X(Pitch): {rot_x}° | Y(Yaw): {rot_y}° | Z(Roll): {rot_z}°\n'
        title += f'KAMERA: {cam_info} | UNGU=Posisi Kamera'
        self.ax.set_title(title, fontsize=12, fontweight='bold')
        self.ax.legend(loc='upper right')
        
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
            self.ax = None

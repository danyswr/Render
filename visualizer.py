import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple

class Visualizer:
    """Handles all visualization using Matplotlib with real-time updates"""
    
    def __init__(self):
        plt.ion()
        self.fig = None
        self.ax = None
    
    def _ensure_figure(self):
        """Ensure figure exists and is ready"""
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.fig = plt.figure(figsize=(10, 8))
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax.clear()
    
    def _add_grid(self, ax, limit=50):
        """Add grid lines to help measure coordinates"""
        ax.set_xlabel('X', fontsize=12, fontweight='bold')
        ax.set_ylabel('Y', fontsize=12, fontweight='bold')
        ax.set_zlabel('Z', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.4, linestyle='--')
        
        step = limit // 5
        ax.set_xticks(np.arange(-limit, limit+1, step))
        ax.set_yticks(np.arange(-limit, limit+1, step))
        ax.set_zticks(np.arange(-limit, limit+1, step))
        
        ax.set_xlim([-limit, limit])
        ax.set_ylim([-limit, limit])
        ax.set_zlim([-limit, limit])
    
    def show_translation_path(self, points: List[List[float]]):
        """Visualize translation path as connected red points with grid"""
        self._ensure_figure()
        
        if len(points) == 0:
            self.ax.text(0, 0, 0, "No points yet", fontsize=12)
            self._add_grid(self.ax)
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            return
        
        points_array = np.array(points)
        
        max_coord = max(np.abs(points_array).max(), 10) * 1.5
        
        self.ax.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                       c='red', s=150, marker='o', label='Path Points', edgecolors='darkred', linewidths=2)
        
        if len(points) > 1:
            self.ax.plot(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                        'r-', linewidth=3, alpha=0.7)
        
        for i, point in enumerate(points):
            label = "START" if i == 0 else f"P{i}"
            self.ax.text(point[0]+1, point[1]+1, point[2]+1, f'  {label}\n  ({point[0]:.0f},{point[1]:.0f},{point[2]:.0f})', 
                        fontsize=9, fontweight='bold')
        
        self._add_grid(self.ax, int(max_coord))
        self.ax.set_title('Translation Path - Red Points Connected by Lines\n(Use grid to measure coordinates)', 
                         fontsize=12, fontweight='bold')
        self.ax.legend(loc='upper right')
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def show_scale_preview(self, position: List[float], scale: float):
        """Visualize scale using colored sphere at position showing orientation"""
        self._ensure_figure()
        
        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 30)
        radius = max(scale * 5, 2)
        x = position[0] + radius * np.outer(np.cos(u), np.sin(v))
        y = position[1] + radius * np.outer(np.sin(u), np.sin(v))
        z = position[2] + radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        colors = np.zeros(x.shape + (4,))
        for i in range(len(u)):
            angle = u[i]
            if -np.pi/4 <= angle <= np.pi/4:
                colors[i, :] = [0.9, 0.2, 0.2, 0.9]
            elif np.pi/4 < angle <= 3*np.pi/4:
                colors[i, :] = [0.2, 0.8, 0.2, 0.9]
            elif -3*np.pi/4 <= angle < -np.pi/4:
                colors[i, :] = [0.3, 0.9, 0.3, 0.9]
            else:
                colors[i, :] = [0.2, 0.2, 0.9, 0.9]
        
        self.ax.plot_surface(x, y, z, facecolors=colors, shade=True)
        
        self.ax.scatter([position[0]], [position[1]], [position[2]], 
                       c='black', s=100, marker='x', linewidths=3)
        
        max_range = max(np.abs(position).max() + radius * 2, 20)
        self._add_grid(self.ax, int(max_range))
        
        self.ax.set_title(f'Scale Preview: {scale:.2f}x at ({position[0]:.0f}, {position[1]:.0f}, {position[2]:.0f})\n'
                         f'RED=Front | GREEN=Sides | BLUE=Back', 
                         fontsize=12, fontweight='bold')
        
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
        radius = 8
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
        
        arrow_length = 12
        x_end = R @ np.array([arrow_length, 0, 0])
        self.ax.quiver(0, 0, 0, x_end[0], x_end[1], x_end[2], 
                      color='red', arrow_length_ratio=0.15, linewidth=3, label='X-axis')
        
        y_end = R @ np.array([0, arrow_length, 0])
        self.ax.quiver(0, 0, 0, y_end[0], y_end[1], y_end[2], 
                      color='green', arrow_length_ratio=0.15, linewidth=3, label='Y-axis')
        
        z_end = R @ np.array([0, 0, arrow_length])
        self.ax.quiver(0, 0, 0, z_end[0], z_end[1], z_end[2], 
                      color='blue', arrow_length_ratio=0.15, linewidth=3, label='Z-axis')
        
        self._add_grid(self.ax, 15)
        self.ax.set_title(f'Rotation Preview\nX(Pitch): {rot_x}° | Y(Yaw): {rot_y}° | Z(Roll): {rot_z}°\n'
                         f'RED=Front | GREEN=Sides | BLUE=Back | YELLOW=Top', 
                         fontsize=11, fontweight='bold')
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

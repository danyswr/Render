import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple

class Visualizer:
    """Handles all visualization using Matplotlib"""
    
    def __init__(self):
        self.fig = None
        self.ax = None
    
    def show_translation_path(self, points: List[List[float]]):
        """Visualize translation path as connected red points"""
        if self.fig is None:
            self.fig = plt.figure(figsize=(12, 10))
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax.clear()
        
        if len(points) == 0:
            self.ax.text(0, 0, 0, "No points yet", fontsize=12)
            return
        
        points_array = np.array(points)
        
        # Plot points
        self.ax.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                       c='red', s=100, marker='o', label='Path Points')
        
        # Connect points with lines
        if len(points) > 1:
            self.ax.plot(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                        'r-', linewidth=2, alpha=0.6)
        
        # Label each point
        for i, point in enumerate(points):
            self.ax.text(point[0], point[1], point[2], f'  P{i}', fontsize=10)
        
        # Set labels and grid
        self.ax.set_xlabel('X', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Y', fontsize=12, fontweight='bold')
        self.ax.set_zlabel('Z', fontsize=12, fontweight='bold')
        self.ax.set_title('Translation Path', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        plt.draw()
        plt.pause(0.1)
    
    def show_scale_preview(self, position: List[float], scale: float):
        """Visualize scale using colored sphere at position"""
        if self.fig is None:
            self.fig = plt.figure(figsize=(12, 10))
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax.clear()
        
        # Create sphere
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x = position[0] + scale * np.outer(np.cos(u), np.sin(v))
        y = position[1] + scale * np.outer(np.sin(u), np.sin(v))
        z = position[2] + scale * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # Color mapping: front (red), side (green), back (blue)
        colors = np.zeros(x.shape + (3,))
        for i in range(len(u)):
            angle = u[i]
            if -np.pi/4 <= angle <= np.pi/4:  # Front
                colors[i, :, 0] = 0.8  # Red
            elif np.pi/4 < angle <= 3*np.pi/4:  # Right side
                colors[i, :, 1] = 0.8  # Green
            elif -3*np.pi/4 <= angle < -np.pi/4:  # Left side
                colors[i, :, 1] = 0.6  # Light green
            else:  # Back
                colors[i, :, 2] = 0.8  # Blue
        
        # Plot sphere with colors
        self.ax.plot_surface(x, y, z, facecolors=colors, alpha=0.8, shade=True)
        
        # Add position marker
        self.ax.scatter([position[0]], [position[1]], [position[2]], 
                       c='black', s=50, marker='x')
        
        # Set labels and grid
        self.ax.set_xlabel('X', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Y', fontsize=12, fontweight='bold')
        self.ax.set_zlabel('Z', fontsize=12, fontweight='bold')
        self.ax.set_title(f'Scale Preview: {scale:.2f}x\n(Red=Front, Green=Side, Blue=Back)', 
                         fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # Set equal aspect ratio
        max_range = scale * 1.5
        self.ax.set_xlim([position[0]-max_range, position[0]+max_range])
        self.ax.set_ylim([position[1]-max_range, position[1]+max_range])
        self.ax.set_zlim([position[2]-max_range, position[2]+max_range])
        
        plt.draw()
        plt.pause(0.1)
    
    def show_rotation_preview(self, rot_x: float, rot_y: float, rot_z: float):
        """Visualize rotation using colored sphere with orientation markers"""
        if self.fig is None:
            self.fig = plt.figure(figsize=(14, 10))
            self.ax = self.fig.add_subplot(111, projection='3d')
        else:
            self.ax.clear()
        
        # Create rotation matrices
        def rotation_matrix(rx, ry, rz):
            # Convert to radians
            rx_rad, ry_rad, rz_rad = np.radians([rx, ry, rz])
            
            # Rotation around X
            Rx = np.array([[1, 0, 0],
                          [0, np.cos(rx_rad), -np.sin(rx_rad)],
                          [0, np.sin(rx_rad), np.cos(rx_rad)]])
            
            # Rotation around Y
            Ry = np.array([[np.cos(ry_rad), 0, np.sin(ry_rad)],
                          [0, 1, 0],
                          [-np.sin(ry_rad), 0, np.cos(ry_rad)]])
            
            # Rotation around Z
            Rz = np.array([[np.cos(rz_rad), -np.sin(rz_rad), 0],
                          [np.sin(rz_rad), np.cos(rz_rad), 0],
                          [0, 0, 1]])
            
            return Rz @ Ry @ Rx
        
        R = rotation_matrix(rot_x, rot_y, rot_z)
        
        # Create sphere
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 20)
        x_sphere = 5 * np.outer(np.cos(u), np.sin(v))
        y_sphere = 5 * np.outer(np.sin(u), np.sin(v))
        z_sphere = 5 * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # Apply rotation to sphere
        points = np.stack([x_sphere.flatten(), y_sphere.flatten(), z_sphere.flatten()])
        rotated_points = R @ points
        x_rot = rotated_points[0].reshape(x_sphere.shape)
        y_rot = rotated_points[1].reshape(y_sphere.shape)
        z_rot = rotated_points[2].reshape(z_sphere.shape)
        
        # Color mapping with rotation
        colors = np.zeros(x_sphere.shape + (3,))
        for i in range(len(u)):
            angle = u[i]
            if -np.pi/4 <= angle <= np.pi/4:
                colors[i, :, 0] = 0.9  # Front - Red
            elif np.pi/4 < angle <= 3*np.pi/4:
                colors[i, :, 1] = 0.9  # Right - Green
            elif -3*np.pi/4 <= angle < -np.pi/4:
                colors[i, :, 1] = 0.6  # Left - Light Green
            else:
                colors[i, :, 2] = 0.9  # Back - Blue
        
        # Add top marker (yellow)
        for j in range(len(v)):
            if v[j] < np.pi/6:  # Top 30 degrees
                colors[:, j, :] = [1.0, 1.0, 0.0]  # Yellow
        
        # Plot rotated sphere
        self.ax.plot_surface(x_rot, y_rot, z_rot, facecolors=colors, alpha=0.8, shade=True)
        
        # Add axis arrows
        arrow_length = 8
        # X axis - Red
        x_end = R @ np.array([arrow_length, 0, 0])
        self.ax.quiver(0, 0, 0, x_end[0], x_end[1], x_end[2], 
                      color='red', arrow_length_ratio=0.15, linewidth=3, label='X-axis')
        
        # Y axis - Green
        y_end = R @ np.array([0, arrow_length, 0])
        self.ax.quiver(0, 0, 0, y_end[0], y_end[1], y_end[2], 
                      color='green', arrow_length_ratio=0.15, linewidth=3, label='Y-axis')
        
        # Z axis - Blue
        z_end = R @ np.array([0, 0, arrow_length])
        self.ax.quiver(0, 0, 0, z_end[0], z_end[1], z_end[2], 
                      color='blue', arrow_length_ratio=0.15, linewidth=3, label='Z-axis')
        
        # Set labels and grid
        self.ax.set_xlabel('X', fontsize=12, fontweight='bold')
        self.ax.set_ylabel('Y', fontsize=12, fontweight='bold')
        self.ax.set_zlabel('Z', fontsize=12, fontweight='bold')
        self.ax.set_title(f'Rotation Preview\nX:{rot_x}° Y:{rot_y}° Z:{rot_z}°\n(Red=Front, Green=Side, Blue=Back, Yellow=Top)', 
                         fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right')
        
        # Set equal aspect ratio
        limit = 10
        self.ax.set_xlim([-limit, limit])
        self.ax.set_ylim([-limit, limit])
        self.ax.set_zlim([-limit, limit])
        
        plt.draw()
        plt.pause(0.1)
    
    def close(self):
        """Close the visualization window"""
        if self.fig is not None:
            plt.close(self.fig)

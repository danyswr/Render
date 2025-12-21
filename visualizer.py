import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Optional, Dict
from rocket_model import RocketModel
from transform import Transform

class Visualizer:
    """Handles visualization with real rocket model rendering"""
    
    def __init__(self):
        plt.ion()
        self.fig = None
        self.ax_scene = None
        self.ax_camera = None
        
        self.camera_position = np.array([0.0, 0.0, -150.0])
        self.camera_rotation = {"x": 0.0, "y": 0.0}
        self.fov = 60
        
        # Build rocket model once
        self.rocket_model = RocketModel(col=320, row=450, length=320)
        self.voxel_data = self.rocket_model.build()
        self.rocket_centroid = self.rocket_model.get_centroid()
    
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
    
    def set_camera_rotation(self, rot_x: float, rot_y: float):
        self.camera_rotation = {"x": rot_x, "y": rot_y}
    
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
        """Draw camera as sphere with direction arrow"""
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
        
        Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
        Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
        R = Ry @ Rx
        
        forward = R @ forward
        arrow_len = max(limit * 0.25, 20)
        
        ax.quiver(cam_x, cam_y, cam_z, 
                  forward[0]*arrow_len, forward[1]*arrow_len, forward[2]*arrow_len,
                  color='purple', arrow_length_ratio=0.15, linewidth=3)
        
        ax.text(cam_x, cam_y, cam_z + cam_radius + 5, 'KAMERA', fontsize=9, 
                fontweight='bold', color='purple', ha='center')
    
    def _draw_rocket_3d(self, ax, position: List[float], rotation: Dict, quality: str = "fast"):
        """Draw rocket model in 3D space - fast for preview, full for final"""
        # Get voxel indices
        y_i, x_i, z_i = np.where(np.sum(self.voxel_data, axis=3) > 10)
        
        if len(y_i) == 0:
            return
        
        # Use different sampling based on quality mode
        total_voxels = len(y_i)
        if quality == "fast":
            sample_size = min(total_voxels, 3000)  # Fast preview: 3000 voxels
        else:
            sample_size = min(total_voxels, 15000)  # Final: 15000 voxels
        
        sample_indices = np.random.choice(total_voxels, size=sample_size, replace=False)
        
        # Collect points and colors for batch scatter
        points_3d = []
        colors = []
        
        for idx in sample_indices:
            y, x, z = y_i[idx], x_i[idx], z_i[idx]
            voxel_color = self.voxel_data[y, x, z].astype(float) / 255.0
            
            # Transform point
            x_local = x - self.rocket_centroid[0]
            y_local = y - self.rocket_centroid[1]
            z_local = z - self.rocket_centroid[2]
            
            # Apply rotation
            rx = np.radians(rotation.get('x', 0))
            ry = np.radians(rotation.get('y', 0))
            
            Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
            Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
            R = Ry @ Rx
            
            point = R @ np.array([x_local, y_local, z_local])
            
            # Apply translation
            world_x = position[0] + point[0]
            world_y = position[1] + point[1]
            world_z = position[2] + point[2]
            
            points_3d.append([world_x, world_y, world_z])
            colors.append(voxel_color)
        
        if len(points_3d) > 0:
            points_array = np.array(points_3d)
            colors_array = np.array(colors)
            point_size = 5 if quality == "fast" else 8
            ax.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                      c=colors_array, cmap='gray', s=point_size, alpha=0.7, depthshade=True)
    
    def _get_camera_transform(self):
        """Get camera transformation matrix based on view direction and rotation"""
        cam_pos = self.camera_position
        cam_rot = self.camera_rotation
        cam_target = np.array([0.0, 0.0, 0.0])  # Looking at origin
        
        # Calculate forward direction (from camera to target)
        forward = cam_target - cam_pos
        forward_len = np.linalg.norm(forward)
        if forward_len > 0:
            forward = forward / forward_len
        else:
            forward = np.array([0, 0, 1])
        
        # Calculate right and up vectors using forward direction
        world_up = np.array([0, 1, 0])
        right = np.cross(forward, world_up)
        right_len = np.linalg.norm(right)
        if right_len > 0:
            right = right / right_len
        else:
            right = np.array([1, 0, 0])
        
        up = np.cross(right, forward)
        
        # Apply camera rotation to the basis vectors
        rx_rad = np.radians(cam_rot['x'])
        ry_rad = np.radians(cam_rot['y'])
        
        Rx = np.array([[1,0,0],[0,np.cos(rx_rad),-np.sin(rx_rad)],[0,np.sin(rx_rad),np.cos(rx_rad)]])
        Ry = np.array([[np.cos(ry_rad),0,np.sin(ry_rad)],[0,1,0],[-np.sin(ry_rad),0,np.cos(ry_rad)]])
        R_rot = Ry @ Rx
        
        forward = R_rot @ forward
        right = R_rot @ right
        up = R_rot @ up
        
        # Build camera-to-world matrix and invert it
        # Camera space: X = right, Y = up, Z = forward
        R_cam = np.array([right, up, forward]).T
        R_cam_inv = R_cam.T  # Inverse of rotation is transpose
        
        return R_cam_inv, cam_pos
    
    def _render_rocket_to_camera_view(self, ax, position: List[float], rotation: Dict, quality: str = "fast"):
        """Render actual rocket as seen from camera"""
        R_cam_inv, cam_pos = self._get_camera_transform()
        
        # Get voxel indices
        y_i, x_i, z_i = np.where(np.sum(self.voxel_data, axis=3) > 10)
        
        if len(y_i) == 0:
            return
        
        pixels_2d = {}
        depth_buffer = {}
        
        # Sample voxels based on quality - use systematic sampling for better coverage
        total_voxels = len(y_i)
        if quality == "fast":
            sample_size = min(total_voxels, 8000)  # Fast preview: 8000 voxels for better coverage
        else:
            sample_size = min(total_voxels, 20000)  # Final: 20000 voxels
        
        # Use systematic sampling to ensure we get voxels from all parts
        step = max(1, total_voxels // sample_size)
        sample_indices = np.arange(0, total_voxels, step)[:sample_size]
        
        for idx in sample_indices:
            y, x, z = y_i[idx], x_i[idx], z_i[idx]
            color = self.voxel_data[y, x, z] / 255.0
            
            # Transform to world space
            x_local = x - self.rocket_centroid[0]
            y_local = y - self.rocket_centroid[1]
            z_local = z - self.rocket_centroid[2]
            
            rx = np.radians(rotation.get('x', 0))
            ry = np.radians(rotation.get('y', 0))
            
            Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
            Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
            R = Ry @ Rx
            
            point = R @ np.array([x_local, y_local, z_local])
            world_x = position[0] + point[0]
            world_y = position[1] + point[1]
            world_z = position[2] + point[2]
            
            # Transform to camera space
            translated = np.array([world_x, world_y, world_z]) - cam_pos
            cam_space = R_cam_inv @ translated
            
            cam_z = cam_space[2]
            if cam_z <= 0.1:
                continue
            
            # Project to 2D
            fov_rad = np.radians(self.fov)
            f = 1.0 / np.tan(fov_rad / 2)
            x_2d = (cam_space[0] / cam_z) * f
            y_2d = (cam_space[1] / cam_z) * f
            
            # Round to pixel with finer precision
            px = int(x_2d * 50)
            py = int(y_2d * 50)
            
            # Depth test
            if (px, py) not in depth_buffer or cam_z < depth_buffer[(px, py)]:
                pixels_2d[(px, py)] = color
                depth_buffer[(px, py)] = cam_z
        
        # Draw pixels with larger size
        if len(pixels_2d) > 0:
            px_array = np.array([k[0] for k in pixels_2d.keys()]) / 50.0
            py_array = np.array([k[1] for k in pixels_2d.keys()]) / 50.0
            colors = np.array(list(pixels_2d.values()))
            ax.scatter(px_array, py_array, c=colors, cmap='gray', s=3, alpha=0.9)
    
    def show_camera_setup_realtime(self, position: List[float], rotation: Dict):
        """Show camera setup with real-time rocket rendering"""
        self._ensure_figure()
        
        limit = 150
        self._add_grid_3d(self.ax_scene, limit)
        
        # Draw rocket at origin (fast mode for real-time)
        self._draw_rocket_3d(self.ax_scene, position, rotation, quality="fast")
        self._draw_camera_indicator(self.ax_scene, limit)
        
        self.ax_scene.set_title('Scene 3D - Object Position & Rotation', fontsize=10)
        
        # Camera view
        self.ax_camera.set_facecolor('white')
        self.ax_camera.set_xlim([-2, 2])
        self.ax_camera.set_ylim([-1.5, 1.5])
        self.ax_camera.set_aspect('equal')
        self.ax_camera.grid(True, alpha=0.3)
        self.ax_camera.set_xlabel('X')
        self.ax_camera.set_ylabel('Y')
        
        self._render_rocket_to_camera_view(self.ax_camera, position, rotation, quality="fast")
        
        cam_rot = self.camera_rotation
        cam_pos = self.camera_position
        title = f'Camera View (2D Projection)\n'
        title += f'Cam Pos: ({cam_pos[0]:.0f}, {cam_pos[1]:.0f}, {cam_pos[2]:.0f}) | '
        title += f'Cam Rot: Pitch={cam_rot["x"]:.0f}° Yaw={cam_rot["y"]:.0f}°'
        self.ax_camera.set_title(title, fontsize=9)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)
    
    def show_translation_with_rocket(self, points: List[List[float]], current_point: Optional[List[float]] = None, rotations: List[Dict] = None):
        """Show translation path with actual rocket models"""
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
            rotations = [{"x": 0, "y": 0} for _ in range(len(points) + (1 if current_point else 0))]
        
        # Draw all rockets (fast mode for real-time)
        if len(points) > 0:
            for i, point in enumerate(points):
                rot = rotations[i] if i < len(rotations) else {"x": 0, "y": 0}
                self._draw_rocket_3d(self.ax_scene, point, rot, quality="fast")
                
                if i == 0:
                    label = "START"
                elif i == len(points) - 1 and len(points) > 1:
                    label = "END"
                else:
                    label = f"P{i}"
                self.ax_scene.text(point[0]+10, point[1]+10, point[2]+10, label, fontsize=10, fontweight='bold')
            
            if len(points) > 1:
                pts = np.array(points)
                self.ax_scene.plot(pts[:, 0], pts[:, 1], pts[:, 2], 'k-', linewidth=2, alpha=0.5)
        
        if current_point is not None:
            rot = rotations[len(points)] if len(points) < len(rotations) else {"x": 0, "y": 0}
            self._draw_rocket_3d(self.ax_scene, current_point, rot, quality="fast")
            self.ax_scene.text(current_point[0]+10, current_point[1]+10, current_point[2]+10, 
                              'NEW', fontsize=10, fontweight='bold', color='orange')
        
        self._draw_camera_indicator(self.ax_scene, limit)
        self.ax_scene.set_title('Scene 3D - Rocket Animation Path', fontsize=10)
        
        # Camera view
        self.ax_camera.set_facecolor('white')
        self.ax_camera.set_xlim([-2, 2])
        self.ax_camera.set_ylim([-1.5, 1.5])
        self.ax_camera.set_aspect('equal')
        self.ax_camera.grid(True, alpha=0.3)
        
        all_display_points = points + ([current_point] if current_point else [])
        all_display_rots = rotations[:len(all_display_points)]
        
        for i, (point, rot) in enumerate(zip(all_display_points, all_display_rots)):
            self._render_rocket_to_camera_view(self.ax_camera, point, rot, quality="fast")
        
        self._draw_camera_indicator(self.ax_scene, limit)
        self.ax_camera.set_title('Camera View - What Kamera Sees', fontsize=9)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.01)
    
    def close(self):
        plt.ioff()
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax_scene = None
            self.ax_camera = None

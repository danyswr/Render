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
    
    def _draw_camera_indicator(self, ax, rocket_position: List[float], limit=50):
        """Draw camera as sphere with fixed viewing direction indicator"""
        cam_x, cam_y, cam_z = self.camera_position
        
        # Draw camera sphere
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 15)
        cam_radius = max(limit * 0.12, 12)
        sphere_x = cam_x + cam_radius * np.outer(np.cos(u), np.sin(v))
        sphere_y = cam_y + cam_radius * np.outer(np.sin(u), np.sin(v))
        sphere_z = cam_z + cam_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(sphere_x, sphere_y, sphere_z, color='purple', alpha=0.8)
        
        cam_target = np.array(rocket_position, dtype=float)
        view_direction = cam_target - self.camera_position
        view_len = np.linalg.norm(view_direction)
        if view_len > 0:
            view_direction = view_direction / view_len
        else:
            view_direction = np.array([0, 0, 1])
        
        arrow_len = max(limit * 0.35, 25)
        ax.quiver(cam_x, cam_y, cam_z, 
                  view_direction[0]*arrow_len, view_direction[1]*arrow_len, view_direction[2]*arrow_len,
                  color='cyan', arrow_length_ratio=0.2, linewidth=3.5, alpha=0.9)
        
        x_center = cam_x + view_direction[0] * arrow_len * 0.8
        y_center = cam_y + view_direction[1] * arrow_len * 0.8
        z_center = cam_z + view_direction[2] * arrow_len * 0.8
        
        # Get perpendicular vectors for the X marker
        world_up = np.array([0, 1, 0])
        right = np.cross(view_direction, world_up)
        right_len = np.linalg.norm(right)
        if right_len > 0:
            right = right / right_len
        else:
            right = np.array([1, 0, 0])
        up = np.cross(right, view_direction)
        
        # Draw X with two diagonal lines
        x_size = cam_radius * 0.6
        
        # First diagonal
        p1_start = np.array([x_center, y_center, z_center]) - right * x_size + up * x_size
        p1_end = np.array([x_center, y_center, z_center]) + right * x_size - up * x_size
        
        ax.plot([p1_start[0], p1_end[0]], [p1_start[1], p1_end[1]], [p1_start[2], p1_end[2]], 
                color='yellow', linewidth=5, alpha=1.0)
        
        # Second diagonal
        p2_start = np.array([x_center, y_center, z_center]) + right * x_size + up * x_size
        p2_end = np.array([x_center, y_center, z_center]) - right * x_size - up * x_size
        
        ax.plot([p2_start[0], p2_end[0]], [p2_start[1], p2_end[1]], [p2_start[2], p2_end[2]], 
                color='yellow', linewidth=5, alpha=1.0)
        
        ax.text(cam_x, cam_y, cam_z + cam_radius + 8, 
                f'CAM\n({cam_x:.0f},{cam_y:.0f},{cam_z:.0f})', 
                fontsize=8, fontweight='bold', color='purple', ha='center')
    
    def _draw_rocket_3d(self, ax, position: List[float], rotation: Dict, quality: str = "fast"):
        """Draw rocket model in 3D space - fast for preview, full for final"""
        # Get voxel indices
        y_i, x_i, z_i = np.where(np.sum(self.voxel_data, axis=3) > 10)
        
        if len(y_i) == 0:
            return
        
        total_voxels = len(y_i)
        if quality == "fast":
            sample_size = min(total_voxels, 2000)  # Reduced from 3000 for speed
        else:
            sample_size = min(total_voxels, 15000)
        
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
            point_size = 4 if quality == "fast" else 8  # Smaller points for speed
            ax.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2], 
                      c=colors_array, cmap='gray', s=point_size, alpha=0.7, depthshade=True)
    
    def _get_camera_transform(self, rocket_position: List[float]):
        """Get camera transformation matrix based on rocket position and camera rotation"""
        cam_pos = self.camera_position
        cam_rot = self.camera_rotation
        
        # Camera looks at the rocket position
        cam_target = np.array(rocket_position, dtype=float)
        
        # Calculate forward direction (from camera to rocket)
        forward = cam_target - cam_pos
        forward_len = np.linalg.norm(forward)
        if forward_len > 0:
            forward = forward / forward_len
        else:
            forward = np.array([0, 0, 1])
        
        # Calculate right and up vectors
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
        
        # Build view matrix
        view_matrix = np.array([
            [right[0], right[1], right[2]],
            [up[0], up[1], up[2]],
            [forward[0], forward[1], forward[2]]
        ])
        
        return view_matrix, cam_pos
    
    def _render_rocket_to_camera_view(self, ax, position: List[float], rotation: Dict, quality: str = "fast"):
        """Render ONLY what camera actually sees - proper projection with depth buffer"""
        view_matrix, cam_pos = self._get_camera_transform(position)
        
        # Get voxel indices
        y_i, x_i, z_i = np.where(np.sum(self.voxel_data, axis=3) > 10)
        
        if len(y_i) == 0:
            return
        
        # Projection parameters
        fov_rad = np.radians(self.fov)
        aspect = 4.0 / 3.0
        f = 1.0 / np.tan(fov_rad / 2)
        
        resolution = 150  # Reduced from 200
        depth_buffer = {}
        pixel_colors = {}
        
        total_voxels = len(y_i)
        if quality == "fast":
            sample_size = min(total_voxels, 5000)  # Reduced from 10000
        else:
            sample_size = min(total_voxels, 25000)
        
        step = max(1, total_voxels // sample_size)
        sample_indices = np.arange(0, total_voxels, step)[:sample_size]
        
        for idx in sample_indices:
            y, x, z = y_i[idx], x_i[idx], z_i[idx]
            color = self.voxel_data[y, x, z] / 255.0
            
            # Transform voxel to world space
            x_local = x - self.rocket_centroid[0]
            y_local = y - self.rocket_centroid[1]
            z_local = z - self.rocket_centroid[2]
            
            rx = np.radians(rotation.get('x', 0))
            ry = np.radians(rotation.get('y', 0))
            
            Rx = np.array([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
            Ry = np.array([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
            R_obj = Ry @ Rx
            
            point_local = np.array([x_local, y_local, z_local])
            point_rotated = R_obj @ point_local
            
            world_pos = np.array([
                position[0] + point_rotated[0],
                position[1] + point_rotated[1],
                position[2] + point_rotated[2]
            ])
            
            # Transform to camera space
            relative_pos = world_pos - cam_pos
            cam_space = view_matrix @ relative_pos
            
            cam_x, cam_y, cam_z = cam_space[0], cam_space[1], cam_space[2]
            
            # Cull voxels behind camera
            if cam_z <= 1.0:
                continue
            
            # Perspective projection
            x_ndc = (f * cam_x) / (cam_z * aspect)
            y_ndc = (f * cam_y) / cam_z
            
            # Cull outside frustum
            if abs(x_ndc) > 1.5 or abs(y_ndc) > 1.5:
                continue
            
            # Map to pixel with depth test
            px = int(x_ndc * resolution)
            py = int(y_ndc * resolution)
            
            pixel_key = (px, py)
            
            if pixel_key not in depth_buffer or cam_z < depth_buffer[pixel_key]:
                depth_buffer[pixel_key] = cam_z
                pixel_colors[pixel_key] = color
        
        # Render pixels
        if len(pixel_colors) > 0:
            px_coords = np.array([k[0] for k in pixel_colors.keys()]) / resolution
            py_coords = np.array([k[1] for k in pixel_colors.keys()]) / resolution
            colors = np.array(list(pixel_colors.values()))
            
            ax.scatter(px_coords, py_coords, c=colors, s=3, alpha=0.95, edgecolors='none')
        else:
            ax.text(0, 0, 'No object in view', ha='center', va='center', 
                   fontsize=12, color='gray', style='italic')
    
    def show_camera_setup_realtime(self, position: List[float], rotation: Dict):
        """Show camera setup with real-time rocket rendering"""
        self._ensure_figure()
        
        limit = 150
        self._add_grid_3d(self.ax_scene, limit)
        
        # Draw rocket
        self._draw_rocket_3d(self.ax_scene, position, rotation, quality="fast")
        self._draw_camera_indicator(self.ax_scene, position, limit)
        
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
        plt.pause(0.001)
    
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
        
        # Draw all rockets
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
        
        rocket_pos = current_point if current_point else (points[-1] if points else [0, 0, 0])
        self._draw_camera_indicator(self.ax_scene, rocket_pos, limit)
        self.ax_scene.set_title('Scene 3D - Rocket Animation Path', fontsize=10)
        
        # Camera view
        self.ax_camera.set_facecolor('white')
        self.ax_camera.set_xlim([-2, 2])
        self.ax_camera.set_ylim([-1.5, 1.5])
        self.ax_camera.set_aspect('equal')
        self.ax_camera.grid(True, alpha=0.3)
        self.ax_camera.set_xlabel('X')
        self.ax_camera.set_ylabel('Y')
        
        all_display_points = points + ([current_point] if current_point else [])
        all_display_rots = rotations[:len(all_display_points)]
        
        for i, (point, rot) in enumerate(zip(all_display_points, all_display_rots)):
            self._render_rocket_to_camera_view(self.ax_camera, point, rot, quality="fast")
        
        self.ax_camera.set_title('Camera View - What Camera Actually Sees', fontsize=9)
        
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.pause(0.001)
    
    def close(self):
        plt.ioff()
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax_scene = None
            self.ax_camera = None

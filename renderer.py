"""
Renderer - Kelas untuk rendering voxel ke 2D image
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
from matplotlib import pyplot as plt


class Renderer:
    """Class untuk rendering voxel 3D ke 2D image"""
    
    def __init__(self, width=640, height=480, fov=50, threshold=10):
        self.width = width
        self.height = height
        self.fov = np.radians(fov)
        self.threshold = threshold
        self.f = 1.0 / np.tan(self.fov / 2)  # Focal length
    
    def render(self, voxel_data, camera, transform, centroid):
        """
        Render voxel dengan transformasi
        
        Args:
            voxel_data: numpy array voxel rocket
            camera: Camera object
            transform: Transform object
            centroid: (cx, cy, cz) centroid rocket
        
        Returns:
            pixel: numpy array (height, width, 3) RGB image
        """
        pixel = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        depth_buffer = np.full((self.height, self.width), 1e9, dtype=float)
        
        # Get bounding box
        y_i, x_i, z_i = np.where(np.sum(voxel_data, axis=3) > self.threshold)
        if len(y_i) == 0:
            return pixel
        
        centroid_x, centroid_y, centroid_z = centroid
        
        # Render setiap voxel
        for i in range(y_i.min(), y_i.max() + 1):
            for j in range(x_i.min(), x_i.max() + 1):
                for k in range(z_i.min(), z_i.max() + 1):
                    if np.sum(voxel_data[i, j, k]) <= self.threshold:
                        continue
                    
                    # 1. Transform point (rotation + translation)
                    world_x, world_y, world_z = transform.transform_point(
                        j, i, k, centroid_x, centroid_y, centroid_z
                    )
                    
                    # 2. World to camera space
                    cam_x, cam_y, cam_z = camera.world_to_camera(world_x, world_y, world_z)
                    
                    # Skip jika di belakang kamera
                    if cam_z <= 10:
                        continue
                    
                    # 3. Perspective projection
                    px = self.f * cam_x / cam_z
                    py = self.f * cam_y / cam_z
                    
                    # 4. Convert to screen coordinates
                    screen_x = int(self.width // 2 + px * self.width // 3)
                    screen_y = int(self.height // 2 - py * self.height // 3)
                    
                    # 5. Draw with depth buffer
                    if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                        if cam_z < depth_buffer[screen_y, screen_x]:
                            pixel[screen_y, screen_x] = voxel_data[i, j, k]
                            depth_buffer[screen_y, screen_x] = cam_z
        
        return pixel
    
    def save_image(self, pixel, filename):
        """Simpan image ke file in result folder"""
        import os
        os.makedirs("result", exist_ok=True)
        filepath = os.path.join("result", filename)
        plt.imsave(filepath, pixel)
        return filepath
    
    def display_images(self, images, titles=None):
        """Display multiple images"""
        n = len(images)
        if n == 0:
            return
        
        plt.figure(figsize=(5 * n, 5))
        for i, img in enumerate(images):
            plt.subplot(1, n, i + 1)
            plt.imshow(img)
            if titles and i < len(titles):
                plt.title(titles[i])
            plt.axis('off')
        plt.tight_layout()
        import os
        os.makedirs("result", exist_ok=True)
        filepath = os.path.join("result", "rocket_display.png")
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"Rendered image saved to: {filepath}")

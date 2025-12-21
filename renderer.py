#ini file renderer.py
"""
Renderer - Kelas untuk rendering voxel ke 2D image
Supports .npy intermediate files and .jpg final output
Fitur Baru: Solid Splatting (mengisi celah antar pixel agar tidak 'bolong-bolong')
"""
import numpy as np
import os


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
        Render voxel dengan transformasi dan Solid Splatting
        
        Args:
            voxel_data: numpy array voxel rocket
            camera: Camera object
            transform: Transform object (with scale support)
            centroid: (cx, cy, cz) centroid rocket
        
        Returns:
            pixel: numpy array (height, width, 3) RGB image
        """
        # Inisialisasi canvas hitam
        pixel = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Depth buffer diisi infinity
        depth_buffer = np.full((self.height, self.width), 1e9, dtype=float)
        
        # Cari koordinat voxel yang ada isinya (optimasi: tidak loop semua koordinat kosong)
        # axis=3 karena shape voxel adalah (Y, X, Z, 3[RGB])
        y_indices, x_indices, z_indices = np.where(np.sum(voxel_data, axis=3) > self.threshold)
        
        if len(y_indices) == 0:
            return pixel
            
        centroid_x, centroid_y, centroid_z = centroid
        
        # Pre-calculation constant untuk proyeksi
        # self.width // 3 adalah faktor scaling viewport yang digunakan
        viewport_scale = self.width // 3
        proj_const = self.f * viewport_scale

        # Loop hanya pada voxel yang aktif (Jauh lebih cepat dari nested loop range)
        for i, j, k in zip(y_indices, x_indices, z_indices):
            
            # 1. Transform point (scale + rotation + translation)
            # Koordinat voxel (j=x, i=y, k=z)
            world_x, world_y, world_z = transform.transform_point(
                j, i, k, centroid_x, centroid_y, centroid_z
            )
            
            # 2. World to camera space
            cam_x, cam_y, cam_z = camera.world_to_camera(world_x, world_y, world_z)
            
            # Skip jika di belakang kamera (clipping plane dekat)
            if cam_z <= 5:
                continue
            
            # 3. Perspective projection
            # Menghitung koordinat layar
            px = proj_const * cam_x / cam_z
            py = proj_const * cam_y / cam_z
            
            center_x = int(self.width // 2 + px)
            center_y = int(self.height // 2 - py)
            
            # --- FITUR ANTI BULET-BULET (SOLID SPLATTING) ---
            # Hitung ukuran voxel di layar berdasarkan jarak (cam_z)
            # Semakin dekat (z kecil), ukuran semakin besar.
            # Ditambah +1 agar overlap menutup celah.
            voxel_size_screen = int(proj_const / cam_z) + 1
            
            # Clamp ukuran agar tidak terlalu gila saat sangat dekat (max 20px)
            # dan minimal 1px saat sangat jauh
            size = max(1, min(voxel_size_screen, 20))
            
            # Hitung bounding box untuk splat (kotak) ini
            half_size = size // 2
            
            # Tentukan range pixel yang akan diwarnai untuk 1 voxel ini
            start_y = max(0, center_y - half_size)
            end_y   = min(self.height, center_y + half_size + 1)
            start_x = max(0, center_x - half_size)
            end_x   = min(self.width, center_x + half_size + 1)
            
            # Skip jika di luar layar
            if start_x >= end_x or start_y >= end_y:
                continue
                
            color = voxel_data[i, j, k]
            
            # 4. Draw Rectangle (Splatting) dengan Depth Test
            # Kita loop area kecil ini (misal 2x2 atau 3x3 pixel)
            for dy in range(start_y, end_y):
                for dx in range(start_x, end_x):
                    # Depth test: hanya gambar jika pixel ini lebih dekat dari yang sudah ada
                    # (Kita gunakan cam_z yang sama untuk satu voxel rata)
                    if cam_z < depth_buffer[dy, dx]:
                        pixel[dy, dx] = color
                        depth_buffer[dy, dx] = cam_z
        
        return pixel
    
    def save_npy(self, pixel, filename):
        """Simpan frame sebagai .npy file"""
        os.makedirs("result/npy_frames", exist_ok=True)
        filepath = os.path.join("result/npy_frames", filename)
        np.save(filepath, pixel)
        return filepath
    
    def npy_to_jpg(self, npy_path, jpg_filename):
        """Convert .npy file ke .jpg"""
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib import pyplot as plt
        
        pixel = np.load(npy_path)
        os.makedirs("result/jpg_frames", exist_ok=True)
        filepath = os.path.join("result/jpg_frames", jpg_filename)
        plt.imsave(filepath, pixel)
        return filepath
    
    def save_image(self, pixel, filename):
        """Simpan image ke file in result folder"""
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib import pyplot as plt
        os.makedirs("result", exist_ok=True)
        filepath = os.path.join("result", filename)
        # Menggunakan format jpg dengan kualitas tinggi
        plt.imsave(filepath, pixel, format='jpg')
        return filepath
    
    def display_images(self, images, titles=None):
        """Display multiple images"""
        import matplotlib
        matplotlib.use('Agg')
        from matplotlib import pyplot as plt
        
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
        os.makedirs("result", exist_ok=True)
        filepath = os.path.join("result", "rocket_display.png")
        plt.savefig(filepath, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"Rendered image saved to: {filepath}")
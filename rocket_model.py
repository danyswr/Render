"""
RocketModel - Kelas untuk membangun model 3D rocket
OBJECT ROCKET TIDAK DIUBAH - 100% SAMA
"""
import numpy as np


class RocketModel:
    """Class untuk membangun dan menyimpan model voxel rocket"""
    
    def __init__(self, col=320, row=450, length=320):
        self.col = col
        self.row = row
        self.length = length
        self.cx = col // 2
        self.cy = row // 2
        self.cz = length // 2
        self.voxel = np.zeros((row, col, length, 3), dtype=np.uint8)
        
        # Warna - TETAP SAMA
        self.C_WHITE_LIT = [250, 250, 252]
        self.C_WHITE_SHADE = [180, 180, 190]
        self.C_BLACK_LIT = [60, 60, 65]
        self.C_BLACK_SHADE = [20, 20, 25]
        self.C_WINDOW_GLINT = [150, 220, 255]
        
    def get_color_shaded(self, x, y, z, nx, ny, nz, c_lit, c_shade):
        """Menghitung warna dengan shading - TIDAK DIUBAH"""
        light_dir = np.array([0.6, 0.4, 0.7])
        light_dir /= np.linalg.norm(light_dir)
        factor = max(0, min(1, np.dot([nx, ny, nz], light_dir) + 0.3))
        return [int(c_shade[i] + (c_lit[i] - c_shade[i]) * factor) for i in range(3)]
    
    def set_vox(self, y, x, z, color):
        """Set voxel dengan boundary check - TIDAK DIUBAH"""
        if 0 <= y < self.row and 0 <= x < self.col and 0 <= z < self.length:
            self.voxel[y, x, z] = color
    
    def build(self):
        """Membangun rocket - OBJECT ROCKET 100% SAMA"""
        cx, cy, cz = self.cx, self.cy, self.cz
        
        # ===== BODY ORBITER - TIDAK DIUBAH =====
        h_orb, r_orb, y_orb, cz_orb = 180, 25, cy + 35, cz - 35
        for y in range(int(y_orb), int(y_orb + h_orb + 25)):
            curr_r = r_orb if y < y_orb + h_orb - 30 else r_orb * (1 - ((y - (y_orb + h_orb - 30)) / 55)**0.9)
            for x in range(int(cx - curr_r - 1), int(cx + curr_r + 2)):
                for z in range(int(cz_orb - curr_r - 1), int(cz_orb + curr_r + 2)):
                    if np.sqrt((x - cx)**2 + (z - cz_orb)**2) <= curr_r:
                        nx, nz = (x - cx) / curr_r, (z - cz_orb) / curr_r
                        ny = 0.2 if y > y_orb + h_orb - 30 else 0
                        is_bottom = z < cz_orb and abs(x - cx) < r_orb * 0.8
                        c_lit = self.C_BLACK_LIT if is_bottom else self.C_WHITE_LIT
                        c_shade = self.C_BLACK_SHADE if is_bottom else self.C_WHITE_SHADE
                        if y > y_orb + h_orb - 10 or z < cz_orb - r_orb + 5:
                            c_lit, c_shade = self.C_BLACK_LIT, self.C_BLACK_SHADE
                        self.set_vox(y, x, z, self.get_color_shaded(x, y, z, nx, ny, nz, c_lit, c_shade))
        
        # ===== COCKPIT WINDOW - TIDAK DIUBAH =====
        y_cock = y_orb + h_orb - 30
        for y in range(int(y_cock), int(y_cock + 12)):
            for x in range(cx - 14, cx + 14):
                if abs(x - cx) < 6 and y > y_cock + 3:
                    color = self.C_WINDOW_GLINT if x > cx + 2 and y > y_cock + 8 else self.C_BLACK_LIT
                    self.set_vox(y, x, cz_orb - r_orb + 3, color)
        
        # ===== SAYAP - TIDAK DIUBAH =====
        y_w_start, y_w_end = y_orb + 5, y_orb + 120
        for y in range(int(y_w_start), int(y_w_end)):
            rel_y = (y_w_end - y) / (y_w_end - y_w_start)
            curr_span = 25 + 80 * rel_y
            z_lead = cz_orb - 25 + 30 * rel_y
            for x in range(int(cx - curr_span), int(cx + curr_span)):
                if abs(x - cx) < 20:
                    continue
                for z in range(int(z_lead), int(cz_orb + 25 - 2)):
                    is_leading = z < z_lead + 6
                    c_lit = self.C_BLACK_LIT if is_leading else self.C_WHITE_LIT
                    c_shade = self.C_BLACK_SHADE if is_leading else self.C_WHITE_SHADE
                    color = self.get_color_shaded(x, y, z, 0, 0.1, 0.9, c_lit, c_shade)
                    self.set_vox(y, x, z, color)
                    self.set_vox(y - 1, x, z, self.C_BLACK_SHADE)
        
        return self.voxel
    
    def get_voxel(self):
        """Mendapatkan voxel data rocket"""
        return self.voxel
    
    def get_centroid(self, threshold=10):
        """Menghitung centroid rocket untuk transformasi"""
        y_i, x_i, z_i = np.where(np.sum(self.voxel, axis=3) > threshold)
        if len(y_i) == 0:
            return self.cx, self.cy, self.cz
        return (x_i.min() + x_i.max()) // 2, (y_i.min() + y_i.max()) // 2, (z_i.min() + z_i.max()) // 2

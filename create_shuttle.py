

"""
Space Shuttle Voxel Creator - OOP Version
==========================================
Build model 3D Space Shuttle menggunakan voxel dengan rotasi dan translasi.
Hanya menggunakan NumPy dan Matplotlib.

Usage:
    python create_shuttle.py
    
Setelah selesai, jalankan render_3D_to_2D.py untuk rendering.
"""

import numpy as np
from matplotlib import pyplot as plt


# =============================================================================
# ========================    SHADER UTILITIES    =============================
# =============================================================================

class ShaderUtils:
    """Static utility methods untuk lighting dan shading."""
    
    LIGHT_DIR = np.array([0.6, 0.4, 0.7])
    LIGHT_DIR = LIGHT_DIR / np.linalg.norm(LIGHT_DIR)
    
    @staticmethod
    def get_shaded_color(nx, ny, nz, c_lit, c_shade, ambient=0.3):
        """Hitung warna dengan diffuse lighting."""
        normal = np.array([nx, ny, nz])
        intensity = np.dot(normal, ShaderUtils.LIGHT_DIR)
        factor = max(0, min(1, intensity + ambient))
        
        r = int(c_shade[0] + (c_lit[0] - c_shade[0]) * factor)
        g = int(c_shade[1] + (c_lit[1] - c_shade[1]) * factor)
        b = int(c_shade[2] + (c_lit[2] - c_shade[2]) * factor)
        return [r, g, b]


# =============================================================================
# ========================    VOXEL MODEL    ==================================
# =============================================================================

class VoxelModel:
    """Container untuk data voxel 3D."""
    
    def __init__(self, cols, rows, length):
        self.cols = cols
        self.rows = rows
        self.length = length
        self.data = np.zeros((rows, cols, length, 3), dtype=np.uint8)
        self.cx = cols // 2
        self.cy = rows // 2
        self.cz = length // 2
    
    def set_voxel(self, y, x, z, color):
        if 0 <= y < self.rows and 0 <= x < self.cols and 0 <= z < self.length:
            self.data[y, x, z] = color
    
    def get_bounds(self, threshold=10):
        try:
            y_i, x_i, z_i = np.where(np.sum(self.data, axis=3) > threshold)
            return (np.min(y_i), np.max(y_i),
                    np.min(x_i), np.max(x_i),
                    np.min(z_i), np.max(z_i))
        except ValueError:
            return (0, self.rows, 0, self.cols, 0, self.length)
    
    def save(self, filepath):
        np.save(filepath, self.data)
        print(f"   Saved: {filepath}")
    
    @classmethod
    def load(cls, filepath):
        data = np.load(filepath)
        rows, cols, length, _ = data.shape
        model = cls(cols, rows, length)
        model.data = data
        return model


# =============================================================================
# ========================    SHUTTLE BUILDER    ==============================
# =============================================================================

class ShuttleBuilder:
    """Builder untuk membuat model Space Shuttle."""
    
    # Palet Warna
    COLORS = {
        'WHITE_LIT':   [250, 250, 252],
        'WHITE_SHADE': [180, 180, 190],
        'BLACK_LIT':   [ 60,  60,  65],
        'BLACK_SHADE': [ 20,  20,  25],
        'ORANGE_LIT':  [240, 140,  50],
        'ORANGE_MID':  [200, 100,  30],
        'ORANGE_DARK': [160,  70,  20],
        'BLUE_NASA':   [ 10,  60, 180],
        'WINDOW_GLINT':[150, 220, 255],
        'GREY_NOZZLE': [100, 100, 100],
    }
    
    def __init__(self, model, include_boosters=True, scale=1.0):
        """
        Args:
            model: VoxelModel instance
            include_boosters: Jika False, hanya build Orbiter (tanpa ET & SRB)
            scale: Scaling factor (e.g. 2.56 for 1024 grid vs 400 grid)
        """
        self.model = model
        self.cx = model.cx
        self.cy = model.cy
        self.cz = model.cz
        self.include_boosters = include_boosters
        self.scale = scale

    def s(self, val):
        """Scale value and return int."""
        return int(val * self.scale)

    def build(self):
        """Bangun model Space Shuttle."""
        if self.include_boosters:
            print(f"1. Building Space Shuttle FULL (Scale: {self.scale:.2f})...")
            self._build_external_tank()
            self._build_solid_rocket_boosters()
        else:
            print(f"1. Building Space Shuttle Orbiter only (Scale: {self.scale:.2f})...")
            self._y_et = self.cy - self.s(100)
            self._r_et = self.s(40)
            self._cz_et = self.cz
        
        self._build_orbiter()
        self._build_cockpit()
        self._build_wings()
        self._build_tail()
        self._build_details()
        
        print("   Model selesai.")
        return self.model
    
    def _set(self, y, x, z, color):
        self.model.set_voxel(y, x, z, color)
    
    def _build_external_tank(self):
        """External Tank (Tangki Oranye)."""
        h_et = self.s(280)
        r_et = self.s(40)
        y_et = self.cy - h_et // 2 + self.s(25)
        cz_et = self.cz + self.s(30)
        C = self.COLORS
        
        # Scaling adjustment for loop bounds and conditions
        taper_len = self.s(50)
        
        for y in range(int(y_et), int(y_et + h_et + self.s(10))):
            dist_from_top = (y_et + h_et - taper_len)
            
            if y < dist_from_top:
                curr_r = r_et
            else:
                # Taper logic scaled
                ratio = (y - dist_from_top) / self.s(60)
                curr_r = r_et * (1 - ratio ** 0.8)
                
            if curr_r <= 0:
                continue
            
            for x in range(int(self.cx - curr_r - 1), int(self.cx + curr_r + 2)):
                for z in range(int(cz_et - curr_r - 1), int(cz_et + curr_r + 2)):
                    dist = np.sqrt((x - self.cx) ** 2 + (z - cz_et) ** 2)
                    if dist <= curr_r:
                        nx = (x - self.cx) / curr_r
                        nz = (z - cz_et) / curr_r
                        ny = 0.2 if y > dist_from_top else 0
                        
                        base = ShaderUtils.get_shaded_color(nx, ny, nz, C['ORANGE_LIT'], C['ORANGE_DARK'])
                        
                        # Detail texturing
                        if (z - cz_et) % self.s(20) < self.s(2) and abs(x - self.cx) < curr_r * 0.8:
                            self._set(y, x, z, C['ORANGE_DARK'])
                        elif (x + y + z) % 7 == 0 or (x * y) % 13 == 0:
                            self._set(y, x, z, C['ORANGE_MID'])
                        else:
                            self._set(y, x, z, base)
        
        self._y_et = y_et
        self._r_et = r_et
        self._cz_et = cz_et
    
    def _build_solid_rocket_boosters(self):
        """SRB (Roket Booster) kiri dan kanan."""
        h_srb = self.s(250)
        r_srb = self.s(18)
        y_srb = self._y_et + self.s(15)
        cz_et = self._cz_et
        dist_srb = self._r_et + r_srb + self.s(10)
        C = self.COLORS
        
        for side in [-1, 1]:
            cx_s = self.cx + side * dist_srb
            
            for y in range(int(y_srb - self.s(40)), int(y_srb + h_srb + self.s(20))):
                if y < y_srb - self.s(10):
                    curr_r = r_srb - self.s(4)
                elif y < y_srb:
                    curr_r = r_srb + self.s(3)
                elif y < y_srb + h_srb - self.s(40):
                    curr_r = r_srb
                else:
                    curr_r = r_srb * (1 - ((y - (y_srb + h_srb - self.s(40))) / self.s(60)))
                
                if curr_r <= 0:
                    continue
                
                for x in range(int(cx_s - curr_r - 1), int(cx_s + curr_r + 2)):
                    for z in range(int(cz_et - curr_r - 1), int(cz_et + curr_r + 2)):
                        dist = np.sqrt((x - cx_s) ** 2 + (z - cz_et) ** 2)
                        if dist <= curr_r:
                            nx = (x - cx_s) / curr_r
                            nz = (z - cz_et) / curr_r
                            ny = 0.3 if y > y_srb + h_srb - self.s(40) else (0.1 if y < y_srb else 0)
                            
                            c_lit, c_shade = C['WHITE_LIT'], C['WHITE_SHADE']
                            
                            if y < y_srb - self.s(10):
                                c_lit, c_shade = C['GREY_NOZZLE'], [60, 60, 60]
                            elif y < y_srb and (y // self.s(4)) % 2 == 0:
                                c_lit, c_shade = C['BLACK_LIT'], C['BLACK_SHADE']
                            elif (y - y_srb) % self.s(60) < self.s(3) and 0 < y - y_srb < h_srb - self.s(50):
                                c_lit, c_shade = C['BLACK_LIT'], C['BLACK_SHADE']
                            
                            color = ShaderUtils.get_shaded_color(nx, ny, nz, c_lit, c_shade)
                            self._set(y, x, z, color)
    
    def _build_orbiter(self):
        """Orbiter (pesawat ulang alik)."""
        h_orb = self.s(180)
        r_orb = self.s(25)
        
        if self.include_boosters:
            y_orb = self._y_et + self.s(35)
            cz_orb = self.cz - self.s(35)
        else:
            y_orb = self.cy - h_orb // 2
            cz_orb = self.cz
        
        C = self.COLORS
        
        for y in range(int(y_orb), int(y_orb + h_orb + self.s(25))):
            taper_start = y_orb + h_orb - self.s(30)
            if y < taper_start:
                curr_r = r_orb
            else:
                curr_r = r_orb * (1 - ((y - taper_start) / self.s(55)) ** 0.9)
            
            if curr_r <= 0:
                continue
            
            for x in range(int(self.cx - curr_r - 1), int(self.cx + curr_r + 2)):
                for z in range(int(cz_orb - curr_r - 1), int(cz_orb + curr_r + 2)):
                    dist = np.sqrt((x - self.cx) ** 2 + (z - cz_orb) ** 2)
                    if dist <= curr_r:
                        nx = (x - self.cx) / curr_r
                        nz = (z - cz_orb) / curr_r
                        ny = 0.2 if y > taper_start else 0
                        
                        is_bottom = z < cz_orb and abs(x - self.cx) < r_orb * 0.8
                        c_lit = C['BLACK_LIT'] if is_bottom else C['WHITE_LIT']
                        c_shade = C['BLACK_SHADE'] if is_bottom else C['WHITE_SHADE']
                        
                        if y > y_orb + h_orb - self.s(10) or z < cz_orb - r_orb + self.s(5):
                            c_lit, c_shade = C['BLACK_LIT'], C['BLACK_SHADE']
                        
                        color = ShaderUtils.get_shaded_color(nx, ny, nz, c_lit, c_shade)
                        self._set(y, x, z, color)
        
        self._y_orb = y_orb
        self._h_orb = h_orb
        self._r_orb = r_orb
        self._cz_orb = cz_orb
    
    def _build_cockpit(self):
        """Kokpit & Jendela."""
        y_cock = self._y_orb + self._h_orb - self.s(30)
        r_orb = self._r_orb
        cz_orb = self._cz_orb
        C = self.COLORS
        
        for y in range(int(y_cock), int(y_cock + self.s(12))):
            for x in range(self.cx - self.s(14), self.cx + self.s(14)):
                z_front = cz_orb - r_orb + self.s(3)
                
                if abs(x - self.cx) < self.s(6) and y > y_cock + self.s(3):
                    color = C['WINDOW_GLINT'] if x > self.cx + self.s(2) and y > y_cock + self.s(8) else C['BLACK_LIT']
                    self._set(y, x, z_front, color)
                elif self.s(7) < abs(x - self.cx) < self.s(12) and y < y_cock + self.s(7):
                    nx = 0.8 if x > self.cx else -0.8
                    color = ShaderUtils.get_shaded_color(nx, 0.2, -0.3, C['BLACK_LIT'], C['BLACK_SHADE'])
                    self._set(y, x, z_front + self.s(3), color)
    
    def _build_wings(self):
        """Sayap Delta Realistis - DARI REFERENSI USER."""
        y_w_start = self._y_orb + self.s(5)
        y_w_end = self._y_orb + self.s(120)
        r_orb = self._r_orb
        cz_orb = self._cz_orb
        span_max = self.s(105)
        C = self.COLORS
        
        for y in range(int(y_w_start), int(y_w_end)):
            rel_y = (y_w_end - y) / (y_w_end - y_w_start)
            curr_span = r_orb + (span_max - r_orb) * rel_y
            z_lead = cz_orb - r_orb + (r_orb * rel_y * 1.2)
            
            for x in range(int(self.cx - curr_span), int(self.cx + curr_span)):
                if abs(x - self.cx) < r_orb * 0.9:
                    continue
                    
                # Tepi depan sayap hitam & tebal
                z_thick = z_lead + self.s(6)
                for z in range(int(z_lead), int(cz_orb + r_orb - self.s(2))):
                    # Shading Normal untuk sayap datar
                    nx, ny, nz = 0, 0.1, 0.9  # Permukaan atas
                    
                    is_leading_edge = z < z_thick
                    is_underside = z > cz_orb - self.s(5)  # Bagian bawah sayap hitam
                    
                    if is_leading_edge or is_underside:
                        color = C['BLACK_LIT']
                        if (x+y+z) % 3 == 0:
                            color = C['BLACK_SHADE']
                    else:
                        color = C['WHITE_LIT']
                        if (x+y) % 8 == 0:
                            color = C['WHITE_SHADE']
                    
                    # Tekstur Heat Shield Tiles
                    if (is_leading_edge or is_underside) and (x+y+z) % 4 == 0:
                        color = C['BLACK_LIT']
                    
                    self._set(y, x, z, color)
                    # Bawah sayap hitam pekat
                    self._set(y-1, x, z, C['BLACK_SHADE'])
        
        self._y_w_end = y_w_end
    
    def _build_tail(self):
        """Ekor vertikal TRIANGULAR (Shark Fin)."""
        y_w_end = self._y_w_end
        r_orb = self._r_orb
        cz_orb = self._cz_orb
        C = self.COLORS
        
        # Shark Fin Tail - Triangular shape
        tail_y_start = int(y_w_end - self.s(35))
        tail_y_end = int(y_w_end + self.s(25))
        tail_height_max = self.s(60)
        
        for y in range(tail_y_start, tail_y_end):
            # Progress along tail length (0 at start, 1 at end)
            progress = (y - tail_y_start) / (tail_y_end - tail_y_start)
            
            # Triangular height taper: tall at start, zero at end
            current_height = int(tail_height_max * (1 - progress))
            if current_height < self.s(3): continue
            
            # Z base position
            z_base = cz_orb + r_orb - self.s(8)
            
            # Width taper: wider at base, thinner at tip
            base_width = self.s(4)
            tip_width = self.s(1)
            
            for z in range(int(z_base), int(z_base + current_height)):
                # Height progress for this slice
                h_progress = (z - z_base) / current_height
                # Width at this height (tapers as we go up)
                current_width = int(base_width - (base_width - tip_width) * h_progress)
                
                for x in range(self.cx - current_width, self.cx + current_width + 1):
                    # Color: edge black, body white
                    is_edge = (z < z_base + self.s(3)) or (z > z_base + current_height - self.s(3))
                    c_lit = C['BLACK_LIT'] if is_edge else C['WHITE_LIT']
                    c_shade = C['BLACK_SHADE'] if is_edge else C['WHITE_SHADE']
                    nx = 0.9 if x > self.cx else -0.9
                    color = ShaderUtils.get_shaded_color(nx, 0, 0, c_lit, c_shade)
                    self._set(y, x, z, color)
        
        # OMS Pods (unchanged)
        for side in [-1, 1]:
            for y in range(int(y_w_end - self.s(20)), int(y_w_end)):
                for x in range(self.cx + side * self.s(10) - self.s(6), self.cx + side * self.s(10) + self.s(7)):
                    for z in range(int(cz_orb + r_orb - self.s(10)), int(cz_orb + r_orb + self.s(5))):
                        if np.sqrt((x - (self.cx + side * self.s(10))) ** 2 + (z - (cz_orb + r_orb)) ** 2) < self.s(8):
                            self._set(y, x, z, C['WHITE_SHADE'])
    
    def _build_details(self):
        """Logo NASA & tulisan."""
        y_w_start = self._y_orb + self.s(5)
        cz_orb = self._cz_orb
        C = self.COLORS
        
        # Logo NASA
        for y in range(int(y_w_start + self.s(50)), int(y_w_start + self.s(60))):
            for x in range(self.cx - self.s(55), self.cx - self.s(45)):
                self._set(y, x, cz_orb - self.s(2), C['BLUE_NASA'])
        
        # Tulisan
        for y in range(int(y_w_start + self.s(50)), int(y_w_start + self.s(55))):
            for x in range(self.cx + self.s(45), self.cx + self.s(65)):
                if (x + y) % 3 > 0:
                    self._set(y, x, cz_orb - self.s(2), C['BLACK_LIT'])


# =============================================================================
# ========================    VOXEL ROTATOR    ================================
# =============================================================================

class VoxelRotator:
    """Generate frame rotasi dan translasi (menjauh dari kamera)."""
    
    def __init__(self, model, num_frames, trans_speed_z=5, roll_speed=360, dimensions_scale=1.0):
        """
        Args:
            model: VoxelModel source
            num_frames: Jumlah frame
            trans_speed_z: Kecepatan translasi Z per frame (positif = menjauh)
            roll_speed: Total rotasi roll dalam derajat (360 = 1 putaran penuh)
            dimensions_scale: Scaling factor untuk trajectory
        """
        self.model = model
        self.num_frames = num_frames
        self.trans_speed_z = trans_speed_z
        self.roll_speed = roll_speed
        self.s = dimensions_scale
    
    @staticmethod
    def _rotation_matrix_x(angle_rad):
        """Rotasi sekitar sumbu X."""
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        return np.array([[1, 0, 0],
                         [0, c, -s],
                         [0, s, c]])
    
    @staticmethod
    def _rotation_matrix_z(angle_rad):
        """Rotasi sekitar sumbu Z (roll)."""
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        return np.array([[c, -s, 0],
                         [s, c, 0],
                         [0, 0, 1]])
    
    @staticmethod
    def _rotation_matrix_y(angle_rad):
        """Rotasi sekitar sumbu Y."""
        c, s = np.cos(angle_rad), np.sin(angle_rad)
        return np.array([[c, 0, s],
                         [0, 1, 0],
                         [-s, 0, c]])
    
    def generate_frames(self, output_prefix, threshold=10):
        """
        Generate semua frame dengan:
        - Roket mulai DEKAT kamera (terlihat BESAR)
        - Roket menjauh dari kamera (terlihat KECIL)
        - Roll rotation sepanjang perjalanan
        """
        print(f"2. Generating {self.num_frames} frames (fly away + roll)...")
        print(f"   Using scale factor: {self.s:.2f} for trajectory")
        
        # Save original
        original_path = f"{output_prefix}0_0.npy"
        self.model.save(original_path)
        
        voxel_ori = self.model.data
        y_min, y_max, x_min, x_max, z_min, z_max = self.model.get_bounds(threshold)
        cx, cy, cz = self.model.cx, self.model.cy, self.model.cz
        length = self.model.length
        
        # ROTASI: PANTAT ROKET menghadap kamera, MONCONG ke bulan (top-left)
        # Roket terbang MENJAUH dari kamera (ke dalam layar) menuju bulan
        # Orientasi: roket "terbang mundur" dari perspektif kamera
        # ROTASI: MONCONG ke arah bulan (Top-Left)
        # Sebelumnya 225 deg -> Kanan. Sekarang coba 135 deg (Top-Left??)
        # Trial error orientasi: Target Top-Left.
        rot_x1 = self._rotation_matrix_x(np.radians(90))   # Wings horizontal
        rot_z_tilt = self._rotation_matrix_z(np.radians(135))  # Arahkan ke kiri-atas?
        initial_rot = rot_z_tilt @ rot_x1
        
        # TRAJECTORY: Hindari Clipping!
        # Max bounds [0, 512]. Center 256.
        # Start Z tidak boleh < -200 (256 - 200 = 56).
        
        # START: Kanan-Bawah
        start_x = 180 * self.s
        start_y = -120 * self.s
        start_z = -180 * self.s  # Reduced from -250 to avoid clipping
        
        # END: Kiri-Atas (Bulan)
        end_x = -120 * self.s
        end_y = 80 * self.s
        end_z = 180 * self.s  # Reduced from 250 to prevent clipping on frames 21-24
        
        # Scaling Note: 
        # Agar terlihat LEBIH BESAR tanpa clipping voxel,
        # kita akan mainkan ZOOM di render script.
        
        total_travel_x = end_x - start_x
        total_travel_y = end_y - start_y
        total_travel_z = end_z - start_z
        
        frame_files = []
        for r in range(1, self.num_frames + 1):
            # Linear Motion (Natural Flyby)
            progress = (r - 1) / (self.num_frames - 1) if self.num_frames > 1 else 0
            
            # BARREL ROLL: Badan muter, MONCONG tetap mengarah ke bulan
            roll_rad = np.radians(progress * self.roll_speed)  # Roll enabled
            roll_mat = self._rotation_matrix_y(roll_rad)  # Y-axis = body axis
            # PENTING: roll dulu (di model space), BARU orient ke arah bulan
            total_mat = initial_rot @ roll_mat  # Order: roll first, then orient
            
            # Translasi
            trans_x = int(start_x + progress * total_travel_x)
            trans_y = int(start_y + progress * total_travel_y)
            trans_z = int(start_z + progress * total_travel_z)
            
            buffer = VoxelModel(self.model.cols, self.model.rows, self.model.length) # Reset buffer
            
            print(f"   Frame {r}/{self.num_frames} (X: {trans_x}, Y: {trans_y}, Z: {trans_z})...")
            
            for i in range(y_min, y_max + 1):
                for j in range(x_min, x_max + 1):
                    for k in range(z_min, z_max + 1):
                        if np.sum(voxel_ori[i, j, k]) > threshold:
                            vec = np.array([j - cx, i - cy, k - cz])
                            new_vec = total_mat @ vec
                            
                            u = int(new_vec[0] + cx) + trans_x
                            v = int(new_vec[1] + cy) + trans_y
                            w = int(new_vec[2] + cz) + trans_z
                            
                            if 0 <= u < self.model.cols and 0 <= v < self.model.rows and 0 <= w < self.model.length:
                                buffer.data[v, u, w, :] = voxel_ori[i, j, k, :]
            
            filepath = f"{output_prefix}frame{r}.npy"
            buffer.save(filepath)
            frame_files.append(filepath)
        
        print("   Done.")
        return frame_files


# =============================================================================
# ========================    SHUTTLE VIEWER    ===============================
# =============================================================================

class ShuttleViewer:
    """Preview model dengan matplotlib."""
    
    def __init__(self, model):
        self.model = model
    
    def preview_slices(self, slice_z=None, slice_x=None):
        """Tampilkan irisan model."""
        print("\n" + "=" * 50)
        print("  PREVIEW MODEL (Tutup window untuk lanjut)")
        print("=" * 50 + "\n")
        
        data = self.model.data
        cz = slice_z if slice_z else self.model.cz
        cx = slice_x if slice_x else self.model.cx
        
        plt.figure(figsize=(10, 6))
        
        plt.subplot(1, 2, 1)
        plt.imshow(data[:, :, cz], origin='lower')
        plt.title("Front View (Z slice)")
        plt.xlabel("X")
        plt.ylabel("Y")
        
        plt.subplot(1, 2, 2)
        plt.imshow(data[:, cx, :], origin='lower')
        plt.title("Side View (X slice)")
        plt.xlabel("Z")
        plt.ylabel("Y")
        
        plt.tight_layout()
        plt.show()


# =============================================================================
# ========================    FRAME RENDERER    ===============================
# =============================================================================

class FrameRenderer:
    """Render voxel frame ke gambar 2D dengan wallpaper background."""
    
    def __init__(self, cam_focal=3000, cam_z=-3500, bg_color=(0, 0, 0), wallpaper_path=None):
        """
        Args:
            cam_focal: Focal length kamera
            cam_z: Posisi Z kamera
            bg_color: Warna background RGB (jika tidak pakai wallpaper)
            wallpaper_path: Path ke file gambar wallpaper (opsional)
        """
        self.cam_focal = cam_focal
        self.cam_z = cam_z
        self.bg_color = bg_color
        self.wallpaper = None
        
        # Load wallpaper jika ada
        if wallpaper_path:
            try:
                self.wallpaper = plt.imread(wallpaper_path)
                print(f"   Wallpaper loaded: {wallpaper_path} ({self.wallpaper.shape})")
            except Exception as e:
                print(f"   Warning: Cannot load wallpaper: {e}")
                self.wallpaper = None
    
    def _project(self, cx, cy, px, py, vz):
        """Proyeksi perspektif."""
        scale = (vz - self.cam_z) / self.cam_focal
        vx = round(cx + (cx - px) * scale)
        vy = round(cy + (cy - py) * scale)
        return vx, vy
    
    def _resize_wallpaper(self, target_rows, target_cols):
        """Resize wallpaper ke ukuran target menggunakan numpy."""
        if self.wallpaper is None:
            return None
        
        wp = self.wallpaper
        h, w = wp.shape[:2]
        
        # Simple resize dengan nearest neighbor
        row_indices = (np.arange(target_rows) * h / target_rows).astype(int)
        col_indices = (np.arange(target_cols) * w / target_cols).astype(int)
        
        row_indices = np.clip(row_indices, 0, h - 1)
        col_indices = np.clip(col_indices, 0, w - 1)
        
        resized = wp[row_indices][:, col_indices]
        
        # Pastikan format uint8
        if resized.dtype != np.uint8:
            if resized.max() <= 1.0:
                resized = (resized * 255).astype(np.uint8)
            else:
                resized = resized.astype(np.uint8)
        
        # Pastikan 3 channel RGB
        if len(resized.shape) == 2:
            resized = np.stack([resized, resized, resized], axis=-1)
        elif resized.shape[2] == 4:
            resized = resized[:, :, :3]
        
        return resized
    
    def render_frame(self, model, threshold=10):
        """Render model ke array pixel 2D dengan wallpaper background."""
        rows, cols, length = model.rows, model.cols, model.length
        col_out = cols * 2
        row_out = rows * 2
        
        # Gunakan wallpaper atau warna solid sebagai background
        if self.wallpaper is not None:
            pixel = self._resize_wallpaper(row_out, col_out)
            if pixel is None:
                pixel = np.zeros((row_out, col_out, 3), dtype=np.uint8)
                pixel[:, :] = self.bg_color
        else:
            pixel = np.zeros((row_out, col_out, 3), dtype=np.uint8)
            pixel[:, :] = self.bg_color
        
        cx, cy = col_out // 4, row_out // 2
        voxel_data = model.data
        
        for px in range(col_out):
            for py in range(row_out):
                for vz in range(0, length, 2):
                    vx, vy = self._project(cx, cy, px, py, vz)
                    
                    if 0 <= vx < cols and 0 <= vy < rows:
                        r, g, b = voxel_data[vy, vx, vz]
                        
                        if int(r) + int(g) + int(b) > threshold:
                            pixel[row_out - py - 1, col_out - px - 1, :] = [r, g, b]
                            break
        
        return pixel
    
    def preview_frames(self, frame_files, output_prefix, threshold=10):
        """
        Render 3 sample frames (awal, tengah, akhir) ke JPG.
        
        Args:
            frame_files: List of .npy frame paths
            output_prefix: Prefix untuk output JPG
            threshold: Threshold warna
        
        Returns:
            list: Paths ke JPG yang dihasilkan
        """
        if not frame_files:
            print("   No frames to preview!")
            return []
        
        total = len(frame_files)
        
        # Pilih 3 frame: awal (0), tengah, akhir
        indices = [0, total // 2, total - 1]
        labels = ["awal", "tengah", "akhir"]
        
        print(f"\n3. Rendering preview frames (awal, tengah, akhir)...")
        
        preview_files = []
        
        for idx, label in zip(indices, labels):
            if idx >= len(frame_files):
                continue
            
            frame_path = frame_files[idx]
            print(f"   Rendering frame {idx + 1} ({label})...")
            
            try:
                model = VoxelModel.load(frame_path)
                pixel = self.render_frame(model, threshold)
                
                # Save ke JPG
                output_path = f"{output_prefix}_preview_{label}.jpg"
                plt.imsave(output_path, pixel)
                print(f"   Saved: {output_path}")
                preview_files.append(output_path)
                
            except Exception as e:
                print(f"   Error rendering {label}: {e}")
        
        return preview_files


# =============================================================================
# ========================    MAIN ENTRY POINT    =============================
# =============================================================================

if __name__ == "__main__":
    print("\033c")  # Clear terminal
    
    # =================== USER CONFIGURATION ===================
    config = {
        # File output
        "filename": "shuttle_realistic_space",
        
        # Folder output untuk .npy files
        "output_folder": "result_npy63",
        
        # Dimensi voxel grid
        "dimensions": (512, 512, 512),  # (cols, rows, length)
        
        # Base dimension for scaling (original design size)
        "base_dimension": 400,
        
        # Threshold untuk deteksi voxel non-kosong
        "threshold": 10,
        
        # Jumlah frame rotasi/animasi
        "num_frames": 24,
        
        # Kecepatan translasi Z per frame (menjauh dari kamera)
        "trans_speed_z": 5,
        
        # Total roll rotation (derajat, 360 = 1 putaran penuh)
        "roll_speed": 360,
        
        # Opsi build
        "include_boosters": False,  # True = full shuttle, False = orbiter only
        
        # Preview slice sebelum generate frames
        "preview_slices": False,  # Disabled untuk auto-run
        
        # Preview render 3 frame (awal, tengah, akhir) ke JPG
        "preview_render_frames": False,
        
        # Kamera untuk rendering (dekat = perspektif dramatis)
        "camera": {
            "focal": 400,   # Focal pendek = perspektif lebih dramatis
            "z": -500,      # Kamera lebih dekat
        },
        
        # Wallpaper background (absolute path)
        "wallpaper": "/home/danyswr/Render/wallpaper/earth & stars 400.jpg",
    }
    
    # =================== BUILD MODEL ===================
    cols, rows, length = config["dimensions"]
    base_dim = config["base_dimension"]
    
    # Calculate scale factor
    scale_factor = cols / base_dim
    print(f"DEBUG: Grid {cols}x{rows}, Base {base_dim}, Scale Factor: {scale_factor}")
    
    model = VoxelModel(cols, rows, length)
    
    builder = ShuttleBuilder(model, include_boosters=config["include_boosters"], scale=scale_factor)
    shuttle = builder.build()
    
    # =================== PREVIEW SLICES ===================
    if config["preview_slices"]:
        viewer = ShuttleViewer(shuttle)
        viewer.preview_slices()
    
    # =================== GENERATE FRAMES ===================
    import os
    output_folder = config["output_folder"]
    os.makedirs(output_folder, exist_ok=True)
    
    # Create generator
    output_prefix = os.path.join(output_folder, config["filename"])
    
    generator = VoxelRotator(model, num_frames=24, roll_speed=config['roll_speed'], dimensions_scale=scale_factor) # BARREL ROLL ENABLED
    frame_files = generator.generate_frames(output_prefix)
    
    print("Done.")
    
    # =================== PREVIEW RENDER (3 FRAMES) ===================
    if config["preview_render_frames"]:
        renderer = FrameRenderer(
            cam_focal=config["camera"]["focal"],
            cam_z=config["camera"]["z"],
            wallpaper_path=config.get("wallpaper")
        )
        preview_jpgs = renderer.preview_frames(
            frame_files, 
            output_prefix,  # Simpan di folder output
            config["threshold"]
        )
        
        print(f"\n📸 Preview JPGs:")
        for jpg in preview_jpgs:
            print(f"   - {jpg}")
    
    print(f"\n✅ SELESAI! {len(frame_files)} frames generated.")
    print(f"   Files: {config['filename']}frame1.npy s/d frame{config['num_frames']}.npy")
    print("\n   Jalankan render_3D_to_2D.py untuk render semua frames.")
import numpy as np

class RocketModel:
    """Class untuk membangun dan menyimpan model voxel rocket lengkap (ET, SRB, dan Orbiter)"""

    def __init__(self, col=320, row=450, length=320):
        # --- KONFIGURASI DIMENSI ---
        # Menerima input dari luar (agar kompatibel dengan visualizer.py), atau pakai default
        self.col = col
        self.row = row
        self.length = length
        self.cx, self.cy, self.cz = self.col // 2, self.row // 2, self.length // 2
        
        # Inisialisasi Voxel Grid (Array 3D)
        self.voxel = np.zeros((self.row, self.col, self.length, 3), dtype=np.uint8)
        
        # --- PALET WARNA REALISTIS (Dengan Shading) ---
        # Putih Orbiter
        self.C_WHITE_LIT    = [250, 250, 252]
        self.C_WHITE_SHADE  = [180, 180, 190]
        # Hitam tiles
        self.C_BLACK_LIT    = [ 60,  60,  65]
        self.C_BLACK_SHADE  = [ 20,  20,  25]
        # Tangki Oranye ET
        self.C_ORANGE_LIT   = [240, 140,  50]
        self.C_ORANGE_MID   = [200, 100,  30]
        self.C_ORANGE_DARK  = [160,  70,  20]
        # Lainnya
        self.C_BLUE_NASA    = [ 10,  60, 180]
        self.C_WINDOW_GLINT = [150, 220, 255]
        self.C_GREY_NOZZLE  = [100, 100, 100]

    def get_centroid(self):
        """Mengembalikan titik pusat roket (untuk keperluan visualisasi/rotasi)"""
        return np.array([self.cx, self.cy, self.cz])

    def get_color_shaded(self, x, y, z, nx, ny, nz, c_lit, c_shade):
        """Menghitung warna berdasarkan pencahayaan (Shading)"""
        # Asumsi cahaya datang dari Kanan-Depan-Atas
        light_dir = np.array([0.6, 0.4, 0.7])
        light_dir = light_dir / np.linalg.norm(light_dir)
        normal = np.array([nx, ny, nz])
        
        # Intensitas cahaya (diffuse)
        intensity = np.dot(normal, light_dir)
        
        # Interpolasi warna berdasarkan intensitas
        factor = max(0, min(1, intensity + 0.3)) # +0.3 untuk ambient light
        
        r = int(c_shade[0] + (c_lit[0] - c_shade[0]) * factor)
        g = int(c_shade[1] + (c_lit[1] - c_shade[1]) * factor)
        b = int(c_shade[2] + (c_lit[2] - c_shade[2]) * factor)
        return [r, g, b]

    def set_vox(self, y, x, z, color):
        """Helper aman untuk set voxel"""
        if 0 <= y < self.row and 0 <= x < self.col and 0 <= z < self.length:
            self.voxel[y, x, z] = color

    def build(self):
        """Fungsi utama untuk merakit model"""
        print("Merakit model Space Shuttle realistis... Mohon tunggu sebentar.")
        
        # Shortcut variable untuk local scope agar kode asli tetap jalan rapi
        cx, cy, cz = self.cx, self.cy, self.cz
        
        # --- 1. EXTERNAL TANK (ET) ---
        h_et = 280; r_et = 40
        y_et = cy - h_et//2 + 25
        cz_et = cz + 30

        for y in range(int(y_et), int(y_et+h_et+10)):
            # Radius: Badan tabung, lalu menajam di atas
            curr_r = r_et if y < y_et + h_et - 50 else r_et * (1 - ((y-(y_et+h_et-50))/60)**0.8)
            
            for x in range(int(cx-curr_r-1), int(cx+curr_r+2)):
                for z in range(int(cz_et-curr_r-1), int(cz_et+curr_r+2)):
                    dist = np.sqrt((x-cx)**2 + (z-cz_et)**2)
                    if dist <= curr_r:
                        nx = (x - cx) / curr_r if curr_r > 0 else 0
                        nz = (z - cz_et) / curr_r if curr_r > 0 else 0
                        ny = 0.2 if y > y_et+h_et-50 else 0
                        
                        base_color = self.get_color_shaded(x,y,z, nx,ny,nz, self.C_ORANGE_LIT, self.C_ORANGE_DARK)
                        
                        # Tekstur Foam & Garis Detail
                        if (z - cz_et) % 20 < 2 and abs(x-cx) < curr_r*0.8:
                             self.set_vox(y,x,z, self.C_ORANGE_DARK)
                        elif (x+y+z)%7 == 0 or (x*y)%13 == 0:
                             self.set_vox(y,x,z, self.C_ORANGE_MID)
                        else:
                             self.set_vox(y,x,z, base_color)

        # --- 2. SOLID ROCKET BOOSTERS (SRB) ---
        h_srb = 250; r_srb = 18
        y_srb = y_et + 15
        dist_srb = r_et + r_srb + 10

        for side in [-1, 1]:
            cx_s = cx + side * dist_srb
            for y in range(int(y_srb-40), int(y_srb+h_srb+20)):
                if y < y_srb-10: curr_r = r_srb - 4 
                elif y < y_srb: curr_r = r_srb + 3 
                elif y < y_srb+h_srb-40: curr_r = r_srb 
                else: curr_r = r_srb * (1 - ((y-(y_srb+h_srb-40))/60))

                for x in range(int(cx_s-curr_r-1), int(cx_s+curr_r+2)):
                    for z in range(int(cz_et-curr_r-1), int(cz_et+curr_r+2)):
                        dist = np.sqrt((x-cx_s)**2 + (z-cz_et)**2)
                        if dist <= curr_r:
                            nx = (x - cx_s) / curr_r if curr_r > 0 else 0
                            nz = (z - cz_et) / curr_r if curr_r > 0 else 0
                            ny = 0.3 if y > y_srb+h_srb-40 else (0.1 if y < y_srb else 0)
                            
                            c_lit = self.C_WHITE_LIT; c_shade = self.C_WHITE_SHADE
                            
                            if y < y_srb-10: 
                                c_lit = self.C_GREY_NOZZLE; c_shade = [60,60,60]
                            elif y < y_srb and (y//4)%2==0: 
                                 c_lit = self.C_BLACK_LIT; c_shade = self.C_BLACK_SHADE
                            elif (y - y_srb) % 60 < 3 and 0 < y-y_srb < h_srb-50:
                                 c_lit = self.C_BLACK_LIT; c_shade = self.C_BLACK_SHADE
                                 
                            color = self.get_color_shaded(x,y,z, nx,ny,nz, c_lit, c_shade)
                            self.set_vox(y,x,z, color)

        # --- 3. ORBITER (PESAWAT ULANG ALIK) ---
        h_orb = 180; r_orb = 25
        y_orb = y_et + 35
        cz_orb = cz - 35

        # A. Badan (Fuselage) & Hidung
        for y in range(int(y_orb), int(y_orb+h_orb+25)):
            if y < y_orb+h_orb-30: curr_r = r_orb 
            else: curr_r = r_orb * (1 - ((y-(y_orb+h_orb-30))/55)**0.9)

            for x in range(int(cx-curr_r-1), int(cx+curr_r+2)):
                for z in range(int(cz_orb-curr_r-1), int(cz_orb+curr_r+2)):
                    dist = np.sqrt((x-cx)**2 + (z-cz_orb)**2)
                    if dist <= curr_r:
                        nx = (x - cx) / curr_r if curr_r > 0 else 0
                        nz = (z - cz_orb) / curr_r if curr_r > 0 else 0
                        ny = 0.2 if y > y_orb+h_orb-30 else 0
                        
                        is_bottom = z < cz_orb and abs(x-cx) < r_orb*0.8
                        c_lit = self.C_BLACK_LIT if is_bottom else self.C_WHITE_LIT
                        c_shade = self.C_BLACK_SHADE if is_bottom else self.C_WHITE_SHADE
                        
                        if y > y_orb+h_orb-10 or z < cz_orb - r_orb + 5:
                             c_lit, c_shade = self.C_BLACK_LIT, self.C_BLACK_SHADE

                        color = self.get_color_shaded(x,y,z, nx,ny,nz, c_lit, c_shade)
                        self.set_vox(y,x,z, color)

        # B. Detail Kokpit & Jendela
        y_cock = y_orb + h_orb - 30
        for y in range(int(y_cock), int(y_cock+12)):
            for x in range(cx-14, cx+14):
                z_front = cz_orb - r_orb + 3
                nx, ny, nz = 0, 0.2, -0.9
                
                if abs(x-cx) < 6 and y > y_cock+3:
                    color = self.C_WINDOW_GLINT if x > cx+2 and y > y_cock+8 else self.C_BLACK_LIT
                    self.set_vox(y,x,z_front, color)
                elif 7 < abs(x-cx) < 12 and y < y_cock+7:
                     nx = 0.8 if x>cx else -0.8; nz = -0.3
                     color = self.get_color_shaded(x,y,z, nx,ny,nz, self.C_BLACK_LIT, self.C_BLACK_SHADE)
                     self.set_vox(y,x,z_front+3, color)

        # C. Sayap Delta
        y_w_start = y_orb + 5; y_w_end = y_orb + 120
        span_max = 105
        for y in range(int(y_w_start), int(y_w_end)):
            rel_y = (y_w_end - y) / (y_w_end - y_w_start)
            curr_span = r_orb + (span_max - r_orb) * rel_y
            z_lead = cz_orb - r_orb + (r_orb * rel_y * 1.2)
            
            for x in range(int(cx-curr_span), int(cx+curr_span)):
                if abs(x-cx) < r_orb*0.9: continue
                z_thick = z_lead + 6 
                for z in range(int(z_lead), int(cz_orb+r_orb-2)):
                    nx, ny, nz = 0, 0.1, 0.9
                    
                    is_leading_edge = z < z_thick
                    is_underside = z > cz_orb - 5
                    
                    c_lit = self.C_BLACK_LIT if is_leading_edge or is_underside else self.C_WHITE_LIT
                    c_shade = self.C_BLACK_SHADE if is_leading_edge or is_underside else self.C_WHITE_SHADE

                    color = self.get_color_shaded(x,y,z, nx,ny,nz, c_lit, c_shade)
                    
                    if (is_leading_edge or is_underside) and (x+y+z)%4 == 0:
                        color = self.C_BLACK_LIT

                    self.set_vox(y,x,z, color)
                    self.set_vox(y-1,x,z, self.C_BLACK_SHADE)

        # D. Ekor Vertikal & Mesin OMS
        for y in range(int(y_w_end-35), int(y_w_end+25)):
            rel_y = (y - (y_w_end-35))/60
            z_pos = cz_orb + r_orb - 8 + (25*rel_y)
            h_tail = 60 * (1-rel_y*0.3)
            for z in range(int(z_pos), int(z_pos+h_tail)):
                for x in range(cx-3, cx+4):
                    nx = 0.9 if x > cx else -0.9; ny, nz = 0, 0
                    is_edge = z < z_pos+4
                    c_lit = self.C_BLACK_LIT if is_edge else self.C_WHITE_LIT
                    c_shade = self.C_BLACK_SHADE if is_edge else self.C_WHITE_SHADE
                    color = self.get_color_shaded(x,y,z, nx,ny,nz, c_lit, c_shade)
                    self.set_vox(y,x,z, color)
        
        # Mesin OMS
        for x_side in [-1, 1]:
            for y in range(int(y_w_end-20), int(y_w_end)):
                for x in range(cx + x_side*10 - 6, cx + x_side*10 + 7):
                    for z in range(int(cz_orb+r_orb-10), int(cz_orb+r_orb+5)):
                         if np.sqrt((x-(cx+x_side*10))**2 + (z-(cz_orb+r_orb))**2) < 8:
                             self.set_vox(y,x,z, self.C_WHITE_SHADE)

        # E. Logo & Tulisan
        for y in range(int(y_w_start+50), int(y_w_start+60)):
            for x in range(cx-55, cx-45):
                self.set_vox(y,x,cz_orb-2, self.C_BLUE_NASA)
        for y in range(int(y_w_start+50), int(y_w_start+55)):
            for x in range(cx+45, cx+65):
                if (x+y)%3 > 0: self.set_vox(y,x,cz_orb-2, self.C_BLACK_LIT)

        print("Model Rocket Selesai Dibangun!")
        return self.voxel

# Cara penggunaan (opsional, agar bisa langsung ditest run)
if __name__ == "__main__":
    model = RocketModel()
    voxels = model.build()
    print(f"Shape akhir voxel: {voxels.shape}")
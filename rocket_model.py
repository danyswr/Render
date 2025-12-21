import numpy as np

class RocketModel:
    """Class untuk membangun dan menyimpan model voxel rocket lengkap (ET, SRB, dan Orbiter)"""
    
    def __init__(self, col=320, row=450, length=320):
        self.col = col
        self.row = row
        self.length = length
        self.cx = col // 2
        self.cy = row // 2
        self.cz = length // 2
        self.voxel = np.zeros((row, col, length, 3), dtype=np.uint8)
        
        # --- Palet Warna Realistis ---
        self.C_WHITE_LIT   = [250, 250, 252]
        self.C_WHITE_SHADE = [180, 180, 190]
        self.C_BLACK_LIT   = [60, 60, 65]
        self.C_BLACK_SHADE = [20, 20, 25]
        self.C_ORANGE_LIT  = [240, 140, 50]
        self.C_ORANGE_MID  = [200, 100, 30]
        self.C_ORANGE_DARK = [160, 70, 20]
        self.C_BLUE_NASA   = [10, 60, 180]
        self.C_WINDOW_GLINT = [150, 220, 255]
        self.C_GREY_NOZZLE = [100, 100, 100]
        
    def get_color_shaded(self, x, y, z, nx, ny, nz, c_lit, c_shade):
        """Menghitung warna dengan shading berdasarkan normal permukaan"""
        light_dir = np.array([0.6, 0.4, 0.7])
        light_dir = light_dir / np.linalg.norm(light_dir)
        normal = np.array([nx, ny, nz])
        intensity = np.dot(normal, light_dir)
        factor = max(0, min(1, intensity + 0.3))
        
        return [
            int(c_shade[0] + (c_lit[0] - c_shade[0]) * factor),
            int(c_shade[1] + (c_lit[1] - c_shade[1]) * factor),
            int(c_shade[2] + (c_lit[2] - c_shade[2]) * factor)
        ]
    
    def set_vox(self, y, x, z, color):
        """Set voxel dengan boundary check"""
        if 0 <= y < self.row and 0 <= x < self.col and 0 <= z < self.length:
            self.voxel[y, x, z] = color
    
    def build(self):
        """Membangun seluruh bagian rocket"""
        cx, cy, cz = self.cx, self.cy, self.cz

        # --- 1. EXTERNAL TANK (ET) ---
        h_et, r_et = 280, 40
        y_et = cy - h_et//2 + 25
        cz_et = cz + 30
        for y in range(int(y_et), int(y_et+h_et+10)):
            curr_r = r_et if y < y_et + h_et - 50 else r_et * (1 - ((y-(y_et+h_et-50))/60)**0.8)
            for x in range(int(cx-curr_r-1), int(cx+curr_r+2)):
                for z in range(int(cz_et-curr_r-1), int(cz_et+curr_r+2)):
                    dist = np.sqrt((x-cx)**2 + (z-cz_et)**2)
                    if dist <= curr_r:
                        nx, nz = (x - cx) / curr_r, (z - cz_et) / curr_r
                        ny = 0.2 if y > y_et+h_et-50 else 0
                        base_color = self.get_color_shaded(x,y,z, nx,ny,nz, self.C_ORANGE_LIT, self.C_ORANGE_DARK)
                        
                        # Tekstur detail foam
                        if (z - cz_et) % 20 < 2 and abs(x-cx) < curr_r*0.8:
                            self.set_vox(y,x,z, self.C_ORANGE_DARK)
                        elif (x+y+z)%7 == 0:
                            self.set_vox(y,x,z, self.C_ORANGE_MID)
                        else:
                            self.set_vox(y,x,z, base_color)

        # --- 2. SOLID ROCKET BOOSTERS (SRB) ---
        h_srb, r_srb = 250, 18
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
                            nx, nz = (x - cx_s) / curr_r, (z - cz_et) / curr_r
                            ny = 0.3 if y > y_srb+h_srb-40 else (0.1 if y < y_srb else 0)
                            c_lit, c_shade = self.C_WHITE_LIT, self.C_WHITE_SHADE
                            if y < y_srb-10: 
                                c_lit, c_shade = self.C_GREY_NOZZLE, [60,60,60]
                            elif (y - y_srb) % 60 < 3 and 0 < y-y_srb < h_srb-50:
                                c_lit, c_shade = self.C_BLACK_LIT, self.C_BLACK_SHADE
                            self.set_vox(y,x,z, self.get_color_shaded(x,y,z, nx,ny,nz, c_lit, c_shade))

        # --- 3. ORBITER (PESAWAT) ---
        h_orb, r_orb = 180, 25
        y_orb = y_et + 35
        cz_orb = cz - 35
        # Badan & Hidung
        for y in range(int(y_orb), int(y_orb+h_orb+25)):
            curr_r = r_orb if y < y_orb+h_orb-30 else r_orb * (1 - ((y-(y_orb+h_orb-30))/55)**0.9)
            for x in range(int(cx-curr_r-1), int(cx+curr_r+2)):
                for z in range(int(cz_orb-curr_r-1), int(cz_orb+curr_r+2)):
                    if np.sqrt((x-cx)**2 + (z-cz_orb)**2) <= curr_r:
                        nx, nz = (x - cx) / curr_r, (z - cz_orb) / curr_r
                        ny = 0.2 if y > y_orb+h_orb-30 else 0
                        is_bottom = z < cz_orb and abs(x-cx) < r_orb*0.8
                        c_lit = self.C_BLACK_LIT if is_bottom else self.C_WHITE_LIT
                        c_shade = self.C_BLACK_SHADE if is_bottom else self.C_WHITE_SHADE
                        if y > y_orb+h_orb-10 or z < cz_orb - r_orb + 5:
                            c_lit, c_shade = self.C_BLACK_LIT, self.C_BLACK_SHADE
                        self.set_vox(y,x,z, self.get_color_shaded(x,y,z, nx,ny,nz, c_lit, c_shade))

        # Jendela Cockpit
        y_cock = y_orb + h_orb - 30
        for y in range(int(y_cock), int(y_cock+12)):
            for x in range(cx-14, cx+14):
                if abs(x-cx) < 6 and y > y_cock+3:
                    color = self.C_WINDOW_GLINT if x > cx+2 and y > y_cock+8 else self.C_BLACK_LIT
                    self.set_vox(y,x,cz_orb - r_orb + 3, color)

        # Sayap Delta
        y_w_start, y_w_end = y_orb + 5, y_orb + 120
        span_max = 105
        for y in range(int(y_w_start), int(y_w_end)):
            rel_y = (y_w_end - y) / (y_w_end - y_w_start)
            curr_span = r_orb + (span_max - r_orb) * rel_y
            z_lead = cz_orb - r_orb + (r_orb * rel_y * 1.2)
            for x in range(int(cx-curr_span), int(cx+curr_span)):
                if abs(x-cx) < r_orb*0.9: continue
                for z in range(int(z_lead), int(cz_orb+r_orb-2)):
                    is_leading = z < z_lead + 6
                    is_underside = z > cz_orb - 5
                    c_lit = self.C_BLACK_LIT if is_leading or is_underside else self.C_WHITE_LIT
                    c_shade = self.C_BLACK_SHADE if is_leading or is_underside else self.C_WHITE_SHADE
                    self.set_vox(y,x,z, self.get_color_shaded(x,y,z, 0,0.1,0.9, c_lit, c_shade))
                    self.set_vox(y-1,x,z, self.C_BLACK_SHADE)

        # Ekor Vertikal
        for y in range(int(y_w_end-35), int(y_w_end+25)):
            rel_y = (y - (y_w_end-35))/60
            z_pos, h_tail = cz_orb + r_orb - 8 + (25*rel_y), 60 * (1-rel_y*0.3)
            for z in range(int(z_pos), int(z_pos+h_tail)):
                for x in range(cx-3, cx+4):
                    self.set_vox(y,x,z, self.get_color_shaded(x,y,z, 1,0,0, self.C_WHITE_LIT, self.C_WHITE_SHADE))

        return self.voxel
    
    def get_voxel(self):
        return self.voxel

    def get_centroid(self, threshold=10):
        y_i, x_i, z_i = np.where(np.sum(self.voxel, axis=3) > threshold)
        if len(y_i) == 0: return self.cx, self.cy, self.cz
        return (x_i.min() + x_i.max()) // 2, (y_i.min() + y_i.max()) // 2, (z_i.min() + z_i.max()) // 2
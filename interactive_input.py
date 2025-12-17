from typing import List, Tuple
from visualizer import Visualizer
from config_manager import ConfigManager

class InteractiveInput:
    """Handles interactive user input with real-time visualization"""
    
    def __init__(self):
        self.visualizer = Visualizer()
        self.config = ConfigManager()
    
    def _get_float_input(self, prompt: str, default: float = 0.0) -> float:
        """Get float input from user with default value"""
        while True:
            try:
                user_input = input(prompt)
                if user_input.strip() == "":
                    return default
                return float(user_input)
            except ValueError:
                print("Input tidak valid. Masukkan angka.")
    
    def _get_yes_no(self, prompt: str) -> bool:
        """Get yes/no input from user"""
        while True:
            response = input(prompt).strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Masukkan 'y' atau 'n'")
    
    def input_translation_stage(self):
        """Stage 1: Input translation path with real-time visualization"""
        print("\n" + "="*60)
        print("TAHAP 1: JALUR TRANSLASI")
        print("="*60)
        print("Tentukan jalur yang akan dilalui roket.")
        print("Gunakan GRID di matplotlib untuk mengukur koordinat.")
        print("Sphere berwarna menunjukkan orientasi objek.")
        print("-"*60)
        
        points = []
        current_point = [0.0, 0.0, 0.0]
        
        print("\n[Matplotlib: Menampilkan grid kosong dengan sphere...]")
        self.visualizer.show_translation_with_sphere(points, current_point)
        
        print("\n--- TITIK AWAL (START) ---")
        print("Masukkan koordinat titik awal:")
        
        print("\nMasukkan X (default 0): ", end="", flush=True)
        current_point[0] = self._get_float_input("", 0.0)
        self.visualizer.show_translation_with_sphere(points, current_point)
        
        print(f"X = {current_point[0]}")
        print("Masukkan Y (default 0): ", end="", flush=True)
        current_point[1] = self._get_float_input("", 0.0)
        self.visualizer.show_translation_with_sphere(points, current_point)
        
        print(f"Y = {current_point[1]}")
        print("Masukkan Z (default 0): ", end="", flush=True)
        current_point[2] = self._get_float_input("", 0.0)
        self.visualizer.show_translation_with_sphere(points, current_point)
        
        print(f"Z = {current_point[2]}")
        print(f"\nTitik Awal: ({current_point[0]}, {current_point[1]}, {current_point[2]})")
        
        if self._get_yes_no("Konfirmasi titik ini? (y/n): "):
            points.append(current_point.copy())
            self.visualizer.show_translation_with_sphere(points, None)
            print("Titik dikonfirmasi!")
        else:
            print("Dibatalkan.")
            return False
        
        while True:
            add_more = self._get_yes_no("\nTambah titik lintasan? (zigzag/jalur bebas) (y/n): ")
            if not add_more:
                break
            
            current_point = points[-1].copy()
            print("\n--- TITIK LINTASAN ---")
            
            print("Masukkan X: ", end="", flush=True)
            current_point[0] = self._get_float_input("", current_point[0])
            self.visualizer.show_translation_with_sphere(points, current_point)
            
            print(f"X = {current_point[0]}")
            print("Masukkan Y: ", end="", flush=True)
            current_point[1] = self._get_float_input("", current_point[1])
            self.visualizer.show_translation_with_sphere(points, current_point)
            
            print(f"Y = {current_point[1]}")
            print("Masukkan Z: ", end="", flush=True)
            current_point[2] = self._get_float_input("", current_point[2])
            self.visualizer.show_translation_with_sphere(points, current_point)
            
            print(f"Z = {current_point[2]}")
            print(f"\nTitik: ({current_point[0]}, {current_point[1]}, {current_point[2]})")
            
            if self._get_yes_no("Konfirmasi titik ini? (y/n): "):
                points.append(current_point.copy())
                self.visualizer.show_translation_with_sphere(points, None)
                print("Titik ditambahkan!")
        
        current_point = points[-1].copy()
        print("\n--- TITIK AKHIR (END) ---")
        
        print("Masukkan X (default 50): ", end="", flush=True)
        current_point[0] = self._get_float_input("", 50.0)
        self.visualizer.show_translation_with_sphere(points, current_point)
        
        print(f"X = {current_point[0]}")
        print("Masukkan Y (default 50): ", end="", flush=True)
        current_point[1] = self._get_float_input("", 50.0)
        self.visualizer.show_translation_with_sphere(points, current_point)
        
        print(f"Y = {current_point[1]}")
        print("Masukkan Z (default 50): ", end="", flush=True)
        current_point[2] = self._get_float_input("", 50.0)
        self.visualizer.show_translation_with_sphere(points, current_point)
        
        print(f"Z = {current_point[2]}")
        
        if self._get_yes_no("Konfirmasi titik akhir? (y/n): "):
            points.append(current_point.copy())
            self.visualizer.show_translation_with_sphere(points, None)
            print("Titik akhir dikonfirmasi!")
        
        print("\n" + "-"*60)
        print("RINGKASAN JALUR TRANSLASI:")
        for i, point in enumerate(points):
            label = "START" if i == 0 else ("END" if i == len(points)-1 else f"P{i}")
            print(f"  {label}: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})")
        
        self.translation_points = points
        return True
    
    def input_scale_stage(self):
        """Stage 2: Input scale per point with sphere visualization"""
        print("\n" + "="*60)
        print("TAHAP 2: SKALA PER TITIK")
        print("="*60)
        print("Atur skala objek di setiap titik.")
        print("Sphere akan berubah ukuran sesuai input.")
        print("Warna: MERAH=Depan, HIJAU=Samping, BIRU=Belakang")
        print("-"*60)
        
        scales = []
        
        for i, point in enumerate(self.translation_points):
            label = "START" if i == 0 else ("END" if i == len(self.translation_points)-1 else f"P{i}")
            print(f"\n--- Titik {label}: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f}) ---")
            
            current_scale = 1.0
            self.visualizer.show_scale_preview(point, current_scale)
            
            print("Masukkan skala (default 1.0): ", end="", flush=True)
            current_scale = self._get_float_input("", 1.0)
            if current_scale <= 0:
                current_scale = 1.0
            
            self.visualizer.show_scale_preview(point, current_scale)
            
            print(f"Skala = {current_scale}x")
            if self._get_yes_no("Konfirmasi skala ini? (y/n): "):
                scales.append(current_scale)
                print(f"Skala {current_scale}x dikonfirmasi!")
            else:
                scales.append(1.0)
                print("Menggunakan skala default 1.0x")
        
        print("\n" + "-"*60)
        print("RINGKASAN SKALA:")
        for i, (point, scale) in enumerate(zip(self.translation_points, scales)):
            label = "START" if i == 0 else ("END" if i == len(self.translation_points)-1 else f"P{i}")
            print(f"  {label}: Skala {scale:.2f}x")
        
        self.scales = scales
        return True
    
    def input_rotation_stage(self):
        """Stage 3: Input rotation with sphere visualization"""
        print("\n" + "="*60)
        print("TAHAP 3: ROTASI")
        print("="*60)
        print("Atur rotasi objek.")
        print("Lihat sphere di matplotlib untuk memahami orientasi:")
        print("  MERAH = Depan")
        print("  HIJAU = Samping")
        print("  BIRU  = Belakang")
        print("  KUNING = Atas")
        print("Panah menunjukkan sumbu X (merah), Y (hijau), Z (biru)")
        print("-"*60)
        
        rot_x, rot_y, rot_z = 0.0, 0.0, 0.0
        
        print("\n[Matplotlib: Menampilkan sphere dengan rotasi awal...]")
        self.visualizer.show_rotation_preview(rot_x, rot_y, rot_z)
        
        while True:
            print("\n--- INPUT ROTASI (dalam derajat) ---")
            
            print("Rotasi X (Pitch, default 0): ", end="", flush=True)
            rot_x = self._get_float_input("", 0.0)
            self.visualizer.show_rotation_preview(rot_x, rot_y, rot_z)
            print(f"X = {rot_x}°")
            
            print("Rotasi Y (Yaw, default 0): ", end="", flush=True)
            rot_y = self._get_float_input("", 0.0)
            self.visualizer.show_rotation_preview(rot_x, rot_y, rot_z)
            print(f"Y = {rot_y}°")
            
            print("Rotasi Z (Roll, default 0): ", end="", flush=True)
            rot_z = self._get_float_input("", 0.0)
            self.visualizer.show_rotation_preview(rot_x, rot_y, rot_z)
            print(f"Z = {rot_z}°")
            
            print(f"\nRotasi: X={rot_x}°, Y={rot_y}°, Z={rot_z}°")
            if self._get_yes_no("Konfirmasi rotasi ini? (y/n): "):
                break
            print("Ulangi input rotasi...")
        
        loop = self._get_yes_no("\nAktifkan rotasi loop (berputar terus)? (y/n): ")
        
        print("\n" + "-"*60)
        print("RINGKASAN ROTASI:")
        print(f"  X (Pitch): {rot_x}°")
        print(f"  Y (Yaw): {rot_y}°")
        print(f"  Z (Roll): {rot_z}°")
        print(f"  Loop: {'Ya' if loop else 'Tidak'}")
        
        self.rotation = {"x": rot_x, "y": rot_y, "z": rot_z, "loop": loop}
        return True
    
    def run(self) -> ConfigManager:
        """Run the complete interactive input process"""
        print("\n" + "="*70)
        print(" "*10 + "ROCKET ANIMATION CONFIGURATOR - INTERACTIVE")
        print("="*70)
        print("\nProgram ini akan memandu Anda mengatur animasi roket.")
        print("Setiap tahap menampilkan visualisasi REAL-TIME di Matplotlib.")
        print("\n[!] Pastikan jendela Matplotlib terlihat untuk feedback visual!")
        
        if not self.input_translation_stage():
            self.visualizer.close()
            return None
        
        if not self.input_scale_stage():
            self.visualizer.close()
            return None
        
        if not self.input_rotation_stage():
            self.visualizer.close()
            return None
        
        for point, scale in zip(self.translation_points, self.scales):
            self.config.add_translation_point(point[0], point[1], point[2], scale)
        
        self.config.set_rotation(
            self.rotation["x"], 
            self.rotation["y"], 
            self.rotation["z"], 
            self.rotation["loop"]
        )
        
        self.config.save()
        
        print("\n" + "="*70)
        print("KONFIGURASI SELESAI!")
        print("="*70)
        print("\nSemua pengaturan telah disimpan.")
        print("Memulai proses render...")
        
        self.visualizer.close()
        return self.config

from typing import List, Tuple, Dict, Optional
from visualizer import Visualizer
from config_manager import ConfigManager

class InteractiveInput:
    """Handles interactive user input with real-time visualization and CRUD menu"""
    
    def __init__(self):
        self.visualizer = Visualizer()
        self.config = ConfigManager()
        self.translation_points: List[List[float]] = []
        self.scales: List[float] = []
        self.rotations: List[Dict[str, float]] = []
        self.camera_settings: Dict = {}
    
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
    
    def _get_int_input(self, prompt: str, min_val: int = 1, max_val: int = 100, default: int = -1) -> int:
        """Get integer input from user within range with default"""
        while True:
            try:
                user_input = input(prompt)
                if user_input.strip() == "":
                    if default >= min_val and default <= max_val:
                        return default
                    return -1
                val = int(user_input)
                if min_val <= val <= max_val:
                    return val
                print(f"Masukkan angka antara {min_val} dan {max_val}")
            except ValueError:
                print("Input tidak valid. Masukkan angka.")
    
    def _get_yes_no(self, prompt: str, default_yes: bool = True) -> bool:
        """Get yes/no input from user with default (Enter = default)"""
        default_hint = "Y/n" if default_yes else "y/N"
        full_prompt = prompt.replace("(y/n)", f"({default_hint})").replace("(Y/n)", f"({default_hint})").replace("(y/N)", f"({default_hint})")
        if "(Y/n)" not in full_prompt and "(y/N)" not in full_prompt and "(y/n)" not in full_prompt:
            full_prompt = full_prompt.rstrip(": ") + f" ({default_hint}): "
        
        while True:
            response = input(full_prompt).strip().lower()
            if response == '':
                return default_yes
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Tekan Enter untuk default, atau ketik 'y'/'n'")
    
    def _display_points_list(self, points: List[List[float]], title: str = "DAFTAR TITIK"):
        """Display numbered list of points"""
        print("\n" + "=" * 50)
        print(f"  {title}")
        print("=" * 50)
        if len(points) == 0:
            print("  (Belum ada titik)")
        else:
            for i, point in enumerate(points):
                label = "START" if i == 0 else ("END" if i == len(points)-1 and len(points) > 1 else f"P{i}")
                print(f"  {i+1}. {label}: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})")
        print("=" * 50)
    
    def _display_menu(self, options: List[str], default: int = 1):
        """Display menu options with default"""
        print("\n" + "-" * 30)
        print("  OPSI:")
        print("-" * 30)
        for i, opt in enumerate(options):
            marker = " [default]" if i + 1 == default else ""
            print(f"  {i+1}. {opt}{marker}")
        print("-" * 30)
    
    def _input_single_point(self, default_x=0.0, default_y=0.0, default_z=0.0) -> List[float]:
        """Input a single 3D point"""
        print(f"Masukkan X [Enter={default_x}]: ", end="", flush=True)
        x = self._get_float_input("", default_x)
        print(f"X = {x}")
        
        print(f"Masukkan Y [Enter={default_y}]: ", end="", flush=True)
        y = self._get_float_input("", default_y)
        print(f"Y = {y}")
        
        print(f"Masukkan Z [Enter={default_z}]: ", end="", flush=True)
        z = self._get_float_input("", default_z)
        print(f"Z = {z}")
        
        return [x, y, z]
    
    def _input_single_rotation(self, default_x=0.0, default_y=0.0, default_z=0.0) -> Dict[str, float]:
        """Input a single rotation (X, Y, Z degrees)"""
        print(f"Rotasi X/Pitch [Enter={default_x}]: ", end="", flush=True)
        rx = self._get_float_input("", default_x)
        print(f"X = {rx}°")
        
        print(f"Rotasi Y/Yaw [Enter={default_y}]: ", end="", flush=True)
        ry = self._get_float_input("", default_y)
        print(f"Y = {ry}°")
        
        print(f"Rotasi Z/Roll [Enter={default_z}]: ", end="", flush=True)
        rz = self._get_float_input("", default_z)
        print(f"Z = {rz}°")
        
        return {"x": rx, "y": ry, "z": rz}

    def input_camera_stage(self):
        """Stage 0: Setup camera position and rotation"""
        print("\n" + "="*60)
        print("TAHAP 0: PENGATURAN KAMERA")
        print("="*60)
        print("Atur posisi dan rotasi kamera.")
        print("Kamera berada DI LUAR grid dan melihat ke objek.")
        print("Kiri = Tampilan Scene | Kanan = Sudut Pandang Kamera (POV)")
        print("-"*60)
        
        cam_x, cam_y, cam_z = 0.0, 0.0, -150.0
        rot_x, rot_y, rot_z = 0.0, 0.0, 0.0
        
        self.visualizer.set_camera_position(cam_x, cam_y, cam_z)
        self.visualizer.set_camera_rotation(rot_x, rot_y, rot_z)
        self.visualizer.show_camera_setup([[0, 0, 0]])
        
        while True:
            print("\n--- POSISI KAMERA SAAT INI ---")
            print(f"  Posisi: ({cam_x:.1f}, {cam_y:.1f}, {cam_z:.1f})")
            print(f"  Rotasi: X={rot_x:.1f}° Y={rot_y:.1f}° Z={rot_z:.1f}°")
            
            self._display_menu(["Edit Posisi Kamera", "Edit Rotasi Kamera", "Konfirmasi"], default=3)
            
            choice = self._get_int_input("Pilih opsi [Enter=3]: ", 1, 3, default=3)
            if choice == -1:
                choice = 3
            
            if choice == 1:
                print("\n--- EDIT POSISI KAMERA ---")
                print("Tips: Nilai Z negatif = kamera di belakang objek (melihat ke depan)")
                print(f"Posisi X [Enter={cam_x}]: ", end="", flush=True)
                cam_x = self._get_float_input("", cam_x)
                print(f"X = {cam_x}")
                
                print(f"Posisi Y [Enter={cam_y}]: ", end="", flush=True)
                cam_y = self._get_float_input("", cam_y)
                print(f"Y = {cam_y}")
                
                print(f"Posisi Z [Enter={cam_z}]: ", end="", flush=True)
                cam_z = self._get_float_input("", cam_z)
                print(f"Z = {cam_z}")
                
                self.visualizer.set_camera_position(cam_x, cam_y, cam_z)
                self.visualizer.show_camera_setup([[0, 0, 0]])
                print("Posisi kamera diupdate!")
            
            elif choice == 2:
                print("\n--- EDIT ROTASI KAMERA ---")
                print("Tips: Rotasi mengubah arah pandang kamera")
                print(f"Rotasi X (Pitch) [Enter={rot_x}]: ", end="", flush=True)
                rot_x = self._get_float_input("", rot_x)
                print(f"X = {rot_x}°")
                
                print(f"Rotasi Y (Yaw) [Enter={rot_y}]: ", end="", flush=True)
                rot_y = self._get_float_input("", rot_y)
                print(f"Y = {rot_y}°")
                
                print(f"Rotasi Z (Roll) [Enter={rot_z}]: ", end="", flush=True)
                rot_z = self._get_float_input("", rot_z)
                print(f"Z = {rot_z}°")
                
                self.visualizer.set_camera_rotation(rot_x, rot_y, rot_z)
                self.visualizer.show_camera_setup([[0, 0, 0]])
                print("Rotasi kamera diupdate!")
            
            elif choice == 3:
                print("\n--- KONFIRMASI KAMERA ---")
                print(f"  Posisi: ({cam_x:.1f}, {cam_y:.1f}, {cam_z:.1f})")
                print(f"  Rotasi: X={rot_x:.1f}° Y={rot_y:.1f}° Z={rot_z:.1f}°")
                
                if self._get_yes_no("Konfirmasi pengaturan kamera?", default_yes=True):
                    self.camera_settings = {
                        "position": [cam_x, cam_y, cam_z],
                        "rotation": {"x": rot_x, "y": rot_y, "z": rot_z}
                    }
                    print("Pengaturan kamera dikonfirmasi!")
                    break
                else:
                    print("Kembali ke menu...")
        
        return True

    def input_translation_stage(self):
        """Stage 1: Input translation path with CRUD menu"""
        print("\n" + "="*60)
        print("TAHAP 1: JALUR TRANSLASI")
        print("="*60)
        print("Tentukan jalur yang akan dilalui roket.")
        print("Gunakan GRID di matplotlib untuk mengukur koordinat.")
        print("Kiri = Scene | Kanan = POV Kamera")
        print("-"*60)
        
        points = []
        
        while True:
            self._display_points_list(points, "JALUR TRANSLASI")
            self.visualizer.show_translation_with_sphere(points, None)
            
            if len(points) >= 2:
                self._display_menu(["Tambah Titik", "Edit Titik", "Hapus Titik", "Konfirmasi"], default=4)
                choice = self._get_int_input("Pilih opsi [Enter=4]: ", 1, 4, default=4)
                if choice == -1:
                    choice = 4
            else:
                self._display_menu(["Tambah Titik", "Edit Titik", "Hapus Titik", "Konfirmasi"], default=1)
                choice = self._get_int_input("Pilih opsi [Enter=1]: ", 1, 4, default=1)
                if choice == -1:
                    choice = 1
            
            if choice == 1:
                print("\n--- TAMBAH TITIK BARU ---")
                if len(points) == 0:
                    default = [0.0, 0.0, 0.0]
                else:
                    default = points[-1].copy()
                
                new_point = self._input_single_point(default[0], default[1], default[2])
                self.visualizer.show_translation_with_sphere(points, new_point)
                
                print(f"\nTitik baru: ({new_point[0]:.1f}, {new_point[1]:.1f}, {new_point[2]:.1f})")
                if self._get_yes_no("Konfirmasi tambah titik ini?", default_yes=True):
                    points.append(new_point)
                    print("Titik ditambahkan!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 2:
                if len(points) == 0:
                    print("\nBelum ada titik untuk diedit.")
                    continue
                
                print("\n--- EDIT TITIK ---")
                self._display_points_list(points)
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(points)}) [Enter=batal]: ", 1, len(points))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                old_point = points[idx]
                print(f"Titik saat ini: ({old_point[0]:.1f}, {old_point[1]:.1f}, {old_point[2]:.1f})")
                
                new_point = self._input_single_point(old_point[0], old_point[1], old_point[2])
                self.visualizer.show_translation_with_sphere(points[:idx] + [new_point] + points[idx+1:], None)
                
                print(f"\nTitik baru: ({new_point[0]:.1f}, {new_point[1]:.1f}, {new_point[2]:.1f})")
                if self._get_yes_no("Konfirmasi perubahan?", default_yes=True):
                    points[idx] = new_point
                    print("Titik diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 3:
                if len(points) == 0:
                    print("\nBelum ada titik untuk dihapus.")
                    continue
                
                print("\n--- HAPUS TITIK ---")
                self._display_points_list(points)
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(points)}) [Enter=batal]: ", 1, len(points))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                old_point = points[idx]
                print(f"Akan menghapus: ({old_point[0]:.1f}, {old_point[1]:.1f}, {old_point[2]:.1f})")
                
                if self._get_yes_no("Konfirmasi hapus?", default_yes=False):
                    points.pop(idx)
                    print("Titik dihapus!")
                    self.visualizer.show_translation_with_sphere(points, None)
                else:
                    print("Dibatalkan.")
            
            elif choice == 4:
                if len(points) < 2:
                    print("\nMinimal 2 titik diperlukan (START dan END).")
                    continue
                
                print("\n--- KONFIRMASI JALUR ---")
                self._display_points_list(points, "JALUR FINAL")
                if self._get_yes_no("Konfirmasi jalur ini?", default_yes=True):
                    self.translation_points = points
                    print("Jalur translasi dikonfirmasi!")
                    break
                else:
                    print("Kembali ke menu...")
        
        return True
    
    def input_scale_stage(self):
        """Stage 2: Input scale per point with CRUD menu"""
        print("\n" + "="*60)
        print("TAHAP 2: SKALA PER TITIK")
        print("="*60)
        print("Atur skala objek di setiap titik.")
        print("Sphere akan berubah ukuran sesuai skala.")
        print("-"*60)
        
        scales = [1.0] * len(self.translation_points)
        
        def display_scales():
            print("\n" + "=" * 50)
            print("  DAFTAR SKALA")
            print("=" * 50)
            for i, (point, scale) in enumerate(zip(self.translation_points, scales)):
                label = "START" if i == 0 else ("END" if i == len(self.translation_points)-1 else f"P{i}")
                print(f"  {i+1}. {label}: ({point[0]:.0f},{point[1]:.0f},{point[2]:.0f}) - Skala: {scale:.2f}x")
            print("=" * 50)
        
        while True:
            display_scales()
            
            if len(scales) > 0:
                idx = len(scales) // 2
                self.visualizer.show_scale_preview(self.translation_points[idx], scales[idx])
            
            self._display_menu(["Edit Skala Titik", "Set Semua Sama", "Konfirmasi"], default=3)
            
            choice = self._get_int_input("Pilih opsi [Enter=3]: ", 1, 3, default=3)
            if choice == -1:
                choice = 3
            
            if choice == 1:
                print("\n--- EDIT SKALA ---")
                display_scales()
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(scales)}) [Enter=batal]: ", 1, len(scales))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                point = self.translation_points[idx]
                old_scale = scales[idx]
                
                print(f"Skala saat ini: {old_scale:.2f}x")
                print(f"Masukkan skala baru [Enter={old_scale}]: ", end="", flush=True)
                new_scale = self._get_float_input("", old_scale)
                if new_scale <= 0:
                    new_scale = 1.0
                
                self.visualizer.show_scale_preview(point, new_scale)
                
                if self._get_yes_no(f"Konfirmasi skala {new_scale:.2f}x?", default_yes=True):
                    scales[idx] = new_scale
                    print("Skala diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 2:
                print("\n--- SET SEMUA SKALA SAMA ---")
                print("Masukkan skala untuk semua titik [Enter=1.0]: ", end="", flush=True)
                new_scale = self._get_float_input("", 1.0)
                if new_scale <= 0:
                    new_scale = 1.0
                
                if self._get_yes_no(f"Set semua skala ke {new_scale:.2f}x?", default_yes=True):
                    scales = [new_scale] * len(self.translation_points)
                    print("Semua skala diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 3:
                print("\n--- KONFIRMASI SKALA ---")
                display_scales()
                if self._get_yes_no("Konfirmasi skala ini?", default_yes=True):
                    self.scales = scales
                    print("Skala dikonfirmasi!")
                    break
                else:
                    print("Kembali ke menu...")
        
        return True
    
    def input_rotation_stage(self):
        """Stage 3: Input rotation per point with CRUD menu"""
        print("\n" + "="*60)
        print("TAHAP 3: ROTASI PER TITIK")
        print("="*60)
        print("Atur rotasi objek di setiap titik.")
        print("MERAH=Depan | HIJAU=Samping | BIRU=Belakang | KUNING=Atas")
        print("-"*60)
        
        rotations = [{"x": 0.0, "y": 0.0, "z": 0.0} for _ in self.translation_points]
        
        def display_rotations():
            print("\n" + "=" * 60)
            print("  DAFTAR ROTASI")
            print("=" * 60)
            for i, (point, rot) in enumerate(zip(self.translation_points, rotations)):
                label = "START" if i == 0 else ("END" if i == len(self.translation_points)-1 else f"P{i}")
                print(f"  {i+1}. {label}: ({point[0]:.0f},{point[1]:.0f},{point[2]:.0f}) - X:{rot['x']:.0f}° Y:{rot['y']:.0f}° Z:{rot['z']:.0f}°")
            print("=" * 60)
        
        while True:
            display_rotations()
            
            if len(rotations) > 0:
                idx = len(rotations) // 2
                point = self.translation_points[idx]
                rot = rotations[idx]
                self.visualizer.show_rotation_at_position(point, rot['x'], rot['y'], rot['z'], f"P{idx}")
            
            self._display_menu(["Edit Rotasi Titik", "Set Semua Sama", "Konfirmasi"], default=3)
            
            choice = self._get_int_input("Pilih opsi [Enter=3]: ", 1, 3, default=3)
            if choice == -1:
                choice = 3
            
            if choice == 1:
                print("\n--- EDIT ROTASI ---")
                display_rotations()
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(rotations)}) [Enter=batal]: ", 1, len(rotations))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                point = self.translation_points[idx]
                old_rot = rotations[idx]
                
                print(f"Rotasi saat ini: X={old_rot['x']}° Y={old_rot['y']}° Z={old_rot['z']}°")
                new_rot = self._input_single_rotation(old_rot['x'], old_rot['y'], old_rot['z'])
                
                self.visualizer.show_rotation_at_position(point, new_rot['x'], new_rot['y'], new_rot['z'], f"P{idx}")
                
                if self._get_yes_no(f"Konfirmasi rotasi X={new_rot['x']}° Y={new_rot['y']}° Z={new_rot['z']}°?", default_yes=True):
                    rotations[idx] = new_rot
                    print("Rotasi diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 2:
                print("\n--- SET SEMUA ROTASI SAMA ---")
                new_rot = self._input_single_rotation()
                
                if self._get_yes_no(f"Set semua rotasi ke X={new_rot['x']}° Y={new_rot['y']}° Z={new_rot['z']}°?", default_yes=True):
                    rotations = [new_rot.copy() for _ in self.translation_points]
                    print("Semua rotasi diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 3:
                print("\n--- KONFIRMASI ROTASI ---")
                display_rotations()
                if self._get_yes_no("Konfirmasi rotasi ini?", default_yes=True):
                    self.rotations = rotations
                    print("Rotasi dikonfirmasi!")
                    break
                else:
                    print("Kembali ke menu...")
        
        loop = self._get_yes_no("Aktifkan rotasi loop (berputar terus)?", default_yes=False)
        self.rotation_loop = loop
        
        return True
    
    def run(self) -> ConfigManager:
        """Run the complete interactive input process"""
        print("\n" + "="*70)
        print(" "*10 + "ROCKET ANIMATION CONFIGURATOR - INTERACTIVE")
        print("="*70)
        print("\nProgram ini akan memandu Anda mengatur animasi roket.")
        print("Setiap tahap menampilkan visualisasi REAL-TIME di Matplotlib.")
        print("\nFitur:")
        print("  - 2 Tampilan: Scene (kiri) + POV Kamera (kanan)")
        print("  - Kamera berada DI LUAR grid")
        print("  - Atur posisi & rotasi kamera")
        print("  - Tekan ENTER untuk nilai default")
        print("\n[!] Pastikan jendela Matplotlib terlihat untuk feedback visual!")
        
        if not self.input_camera_stage():
            self.visualizer.close()
            return None
        
        if not self.input_translation_stage():
            self.visualizer.close()
            return None
        
        if not self.input_scale_stage():
            self.visualizer.close()
            return None
        
        if not self.input_rotation_stage():
            self.visualizer.close()
            return None
        
        for point, scale, rotation in zip(self.translation_points, self.scales, self.rotations):
            self.config.add_translation_point(point[0], point[1], point[2], scale, rotation)
        
        self.config.set_rotation_loop(self.rotation_loop)
        
        if self.camera_settings:
            self.config.set_camera_settings(self.camera_settings)
        
        self.config.save()
        
        print("\n" + "="*70)
        print("KONFIGURASI SELESAI!")
        print("="*70)
        print("\nSemua pengaturan telah disimpan.")
        print("Memulai proses render...")
        
        self.visualizer.close()
        return self.config

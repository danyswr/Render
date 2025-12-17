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
    
    def _display_points_table(self, points: List[List[float]], title: str = "DAFTAR TITIK TRANSLASI"):
        """Display clean table of points"""
        print("\n" + "=" * 55)
        print(f"  {title}")
        print("=" * 55)
        if len(points) == 0:
            print("  (Belum ada titik)")
        else:
            print("  No.  | Label  | Koordinat (X, Y, Z)")
            print("  " + "-" * 50)
            for i, point in enumerate(points):
                if i == 0:
                    label = "START"
                elif i == len(points) - 1 and len(points) > 1:
                    label = "END"
                else:
                    label = f"P{i}"
                print(f"  {i+1:3}.  | {label:6} | ({point[0]:7.1f}, {point[1]:7.1f}, {point[2]:7.1f})")
        print("=" * 55)
    
    def _display_menu(self, options: List[str], default: int = 1):
        """Display menu options with default"""
        print("\n" + "-" * 35)
        print("  OPSI:")
        print("-" * 35)
        for i, opt in enumerate(options):
            marker = " [Enter]" if i + 1 == default else ""
            print(f"  {i+1}. {opt}{marker}")
        print("-" * 35)
    
    def _input_xyz_inline(self, prompt: str, default_x=0.0, default_y=0.0, default_z=0.0) -> List[float]:
        """Input XYZ coordinates with clean inline format"""
        print(f"\n{prompt}")
        print(f"  Default: ({default_x:.1f}, {default_y:.1f}, {default_z:.1f})")
        
        x = self._get_float_input(f"  X [{default_x:.1f}]: ", default_x)
        y = self._get_float_input(f"  Y [{default_y:.1f}]: ", default_y)
        z = self._get_float_input(f"  Z [{default_z:.1f}]: ", default_z)
        
        return [x, y, z]
    
    def _input_single_rotation(self, default_x=0.0, default_y=0.0, default_z=0.0) -> Dict[str, float]:
        """Input a single rotation (X, Y, Z degrees)"""
        print(f"\n  Default: X={default_x}°, Y={default_y}°, Z={default_z}°")
        
        rx = self._get_float_input(f"  Rotasi X/Pitch [{default_x}]: ", default_x)
        ry = self._get_float_input(f"  Rotasi Y/Yaw [{default_y}]: ", default_y)
        rz = self._get_float_input(f"  Rotasi Z/Roll [{default_z}]: ", default_z)
        
        return {"x": rx, "y": ry, "z": rz}

    def input_camera_stage(self):
        """Stage 0: Setup camera position and rotation"""
        print("\n" + "="*60)
        print("  TAHAP 0: PENGATURAN KAMERA")
        print("="*60)
        print("  Atur posisi dan rotasi kamera.")
        print("  Kiri = Tampilan Scene 3D | Kanan = Sudut Pandang Kamera 2D")
        print("-"*60)
        
        cam_x, cam_y, cam_z = 0.0, 0.0, -150.0
        rot_x, rot_y, rot_z = 0.0, 0.0, 0.0
        
        self.visualizer.set_camera_position(cam_x, cam_y, cam_z)
        self.visualizer.set_camera_rotation(rot_x, rot_y, rot_z)
        self.visualizer.show_camera_setup([[0, 0, 0]])
        
        while True:
            print("\n" + "=" * 45)
            print("  KAMERA SAAT INI")
            print("=" * 45)
            print(f"  Posisi : ({cam_x:.1f}, {cam_y:.1f}, {cam_z:.1f})")
            print(f"  Rotasi : X={rot_x:.1f}°, Y={rot_y:.1f}°, Z={rot_z:.1f}°")
            print("=" * 45)
            
            self._display_menu(["Edit Posisi Kamera", "Edit Rotasi Kamera", "Konfirmasi"], default=3)
            
            choice = self._get_int_input("Pilih opsi: ", 1, 3, default=3)
            if choice == -1:
                choice = 3
            
            if choice == 1:
                print("\n--- EDIT POSISI KAMERA ---")
                print("Tips: Z negatif = kamera di belakang objek")
                pos = self._input_xyz_inline("Posisi kamera:", cam_x, cam_y, cam_z)
                cam_x, cam_y, cam_z = pos[0], pos[1], pos[2]
                
                self.visualizer.set_camera_position(cam_x, cam_y, cam_z)
                self.visualizer.show_camera_setup([[0, 0, 0]])
                print("Posisi kamera diupdate!")
            
            elif choice == 2:
                print("\n--- EDIT ROTASI KAMERA ---")
                print("Tips: Rotasi mengubah arah pandang kamera")
                rot = self._input_single_rotation(rot_x, rot_y, rot_z)
                rot_x, rot_y, rot_z = rot['x'], rot['y'], rot['z']
                
                self.visualizer.set_camera_rotation(rot_x, rot_y, rot_z)
                self.visualizer.show_camera_setup([[0, 0, 0]])
                print("Rotasi kamera diupdate!")
            
            elif choice == 3:
                print("\n" + "=" * 45)
                print("  KONFIRMASI PENGATURAN KAMERA")
                print("=" * 45)
                print(f"  Posisi : ({cam_x:.1f}, {cam_y:.1f}, {cam_z:.1f})")
                print(f"  Rotasi : X={rot_x:.1f}°, Y={rot_y:.1f}°, Z={rot_z:.1f}°")
                print("=" * 45)
                
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
        """Stage 1: Input translation path - first set start point, then add more"""
        print("\n" + "="*60)
        print("  TAHAP 1: JALUR TRANSLASI")
        print("="*60)
        print("  1. Tentukan titik AWAL (START)")
        print("  2. Tambahkan titik-titik lainnya")
        print("  3. Titik terakhir = titik AKHIR (END)")
        print("  ")
        print("  Kiri = Scene 3D | Kanan = Tampilan Kamera 2D")
        print("-"*60)
        
        points = []
        
        print("\n>>> LANGKAH 1: Tentukan Titik Awal (START)")
        start_point = self._input_xyz_inline("Koordinat titik START:", 0.0, 0.0, 0.0)
        self.visualizer.show_translation_with_sphere([], start_point)
        
        print(f"\n  Titik START: ({start_point[0]:.1f}, {start_point[1]:.1f}, {start_point[2]:.1f})")
        if self._get_yes_no("Konfirmasi titik START?", default_yes=True):
            points.append(start_point)
            print("Titik START ditambahkan!")
        else:
            while True:
                start_point = self._input_xyz_inline("Koordinat titik START:", 0.0, 0.0, 0.0)
                self.visualizer.show_translation_with_sphere([], start_point)
                print(f"\n  Titik START: ({start_point[0]:.1f}, {start_point[1]:.1f}, {start_point[2]:.1f})")
                if self._get_yes_no("Konfirmasi titik START?", default_yes=True):
                    points.append(start_point)
                    print("Titik START ditambahkan!")
                    break
        
        print("\n>>> LANGKAH 2: Tambahkan Titik Lainnya")
        print("    (Titik terakhir akan menjadi END)")
        
        while True:
            self._display_points_table(points)
            self.visualizer.show_translation_with_sphere(points, None)
            
            if len(points) >= 2:
                self._display_menu([
                    "Tambah Titik Baru",
                    "Edit Titik",
                    "Hapus Titik",
                    "Konfirmasi Jalur"
                ], default=4)
                choice = self._get_int_input("Pilih opsi: ", 1, 4, default=4)
                if choice == -1:
                    choice = 4
            else:
                self._display_menu([
                    "Tambah Titik Baru",
                    "Edit Titik",
                    "Hapus Titik",
                    "Konfirmasi Jalur"
                ], default=1)
                choice = self._get_int_input("Pilih opsi: ", 1, 4, default=1)
                if choice == -1:
                    choice = 1
            
            if choice == 1:
                print("\n--- TAMBAH TITIK BARU ---")
                last = points[-1] if points else [0.0, 0.0, 0.0]
                new_point = self._input_xyz_inline(f"Koordinat titik P{len(points)}:", last[0], last[1], last[2])
                self.visualizer.show_translation_with_sphere(points, new_point)
                
                print(f"\n  Titik baru: ({new_point[0]:.1f}, {new_point[1]:.1f}, {new_point[2]:.1f})")
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
                self._display_points_table(points)
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(points)}), Enter=batal: ", 1, len(points))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                old = points[idx]
                label = "START" if idx == 0 else ("END" if idx == len(points)-1 else f"P{idx}")
                print(f"Mengedit titik {label}")
                
                new_point = self._input_xyz_inline(f"Koordinat baru untuk {label}:", old[0], old[1], old[2])
                temp_points = points[:idx] + [new_point] + points[idx+1:]
                self.visualizer.show_translation_with_sphere(temp_points, None)
                
                print(f"\n  {label} lama: ({old[0]:.1f}, {old[1]:.1f}, {old[2]:.1f})")
                print(f"  {label} baru: ({new_point[0]:.1f}, {new_point[1]:.1f}, {new_point[2]:.1f})")
                if self._get_yes_no("Konfirmasi perubahan?", default_yes=True):
                    points[idx] = new_point
                    print("Titik diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 3:
                if len(points) == 0:
                    print("\nBelum ada titik untuk dihapus.")
                    continue
                
                if len(points) == 1:
                    print("\nTidak bisa menghapus titik START satu-satunya.")
                    continue
                
                print("\n--- HAPUS TITIK ---")
                self._display_points_table(points)
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(points)}), Enter=batal: ", 1, len(points))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                old = points[idx]
                label = "START" if idx == 0 else ("END" if idx == len(points)-1 else f"P{idx}")
                
                print(f"\n  Akan menghapus {label}: ({old[0]:.1f}, {old[1]:.1f}, {old[2]:.1f})")
                if self._get_yes_no("Konfirmasi hapus?", default_yes=False):
                    points.pop(idx)
                    print("Titik dihapus!")
                    self.visualizer.show_translation_with_sphere(points, None)
                else:
                    print("Dibatalkan.")
            
            elif choice == 4:
                if len(points) < 2:
                    print("\n[!] Minimal 2 titik diperlukan (START dan END).")
                    print("    Silakan tambah minimal 1 titik lagi.")
                    continue
                
                print("\n" + "=" * 55)
                print("  KONFIRMASI JALUR TRANSLASI")
                print("=" * 55)
                self._display_points_table(points, "JALUR FINAL")
                
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
        print("  TAHAP 2: SKALA PER TITIK")
        print("="*60)
        print("  Atur skala objek di setiap titik.")
        print("-"*60)
        
        scales = [1.0] * len(self.translation_points)
        
        def display_scales():
            print("\n" + "=" * 60)
            print("  DAFTAR SKALA")
            print("=" * 60)
            print("  No.  | Label  | Koordinat          | Skala")
            print("  " + "-" * 55)
            for i, (point, scale) in enumerate(zip(self.translation_points, scales)):
                if i == 0:
                    label = "START"
                elif i == len(self.translation_points) - 1:
                    label = "END"
                else:
                    label = f"P{i}"
                coord = f"({point[0]:.0f}, {point[1]:.0f}, {point[2]:.0f})"
                print(f"  {i+1:3}.  | {label:6} | {coord:18} | {scale:.2f}x")
            print("=" * 60)
        
        while True:
            display_scales()
            
            if len(scales) > 0:
                idx = len(scales) // 2
                self.visualizer.show_scale_preview(self.translation_points[idx], scales[idx])
            
            self._display_menu(["Edit Skala Titik", "Set Semua Sama", "Konfirmasi"], default=3)
            
            choice = self._get_int_input("Pilih opsi: ", 1, 3, default=3)
            if choice == -1:
                choice = 3
            
            if choice == 1:
                print("\n--- EDIT SKALA ---")
                display_scales()
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(scales)}), Enter=batal: ", 1, len(scales))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                point = self.translation_points[idx]
                old_scale = scales[idx]
                
                print(f"\n  Skala saat ini: {old_scale:.2f}x")
                new_scale = self._get_float_input(f"  Skala baru [{old_scale}]: ", old_scale)
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
                new_scale = self._get_float_input("  Skala untuk semua titik [1.0]: ", 1.0)
                if new_scale <= 0:
                    new_scale = 1.0
                
                if self._get_yes_no(f"Set semua skala ke {new_scale:.2f}x?", default_yes=True):
                    scales = [new_scale] * len(self.translation_points)
                    print("Semua skala diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 3:
                print("\n" + "=" * 50)
                print("  KONFIRMASI SKALA")
                print("=" * 50)
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
        print("  TAHAP 3: ROTASI PER TITIK")
        print("="*60)
        print("  Atur rotasi objek di setiap titik.")
        print("  MERAH=Depan | HIJAU=Samping | BIRU=Belakang | KUNING=Atas")
        print("-"*60)
        
        rotations = [{"x": 0.0, "y": 0.0, "z": 0.0} for _ in self.translation_points]
        
        def display_rotations():
            print("\n" + "=" * 70)
            print("  DAFTAR ROTASI")
            print("=" * 70)
            print("  No.  | Label  | Koordinat          | Rotasi (X, Y, Z)")
            print("  " + "-" * 65)
            for i, (point, rot) in enumerate(zip(self.translation_points, rotations)):
                if i == 0:
                    label = "START"
                elif i == len(self.translation_points) - 1:
                    label = "END"
                else:
                    label = f"P{i}"
                coord = f"({point[0]:.0f}, {point[1]:.0f}, {point[2]:.0f})"
                rot_str = f"({rot['x']:.0f}, {rot['y']:.0f}, {rot['z']:.0f})"
                print(f"  {i+1:3}.  | {label:6} | {coord:18} | {rot_str}")
            print("=" * 70)
        
        while True:
            display_rotations()
            
            if len(rotations) > 0:
                idx = len(rotations) // 2
                point = self.translation_points[idx]
                rot = rotations[idx]
                label = "START" if idx == 0 else ("END" if idx == len(rotations)-1 else f"P{idx}")
                self.visualizer.show_rotation_at_position(point, rot['x'], rot['y'], rot['z'], label)
            
            self._display_menu(["Edit Rotasi Titik", "Set Semua Sama", "Konfirmasi"], default=3)
            
            choice = self._get_int_input("Pilih opsi: ", 1, 3, default=3)
            if choice == -1:
                choice = 3
            
            if choice == 1:
                print("\n--- EDIT ROTASI ---")
                display_rotations()
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(rotations)}), Enter=batal: ", 1, len(rotations))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                point = self.translation_points[idx]
                old_rot = rotations[idx]
                label = "START" if idx == 0 else ("END" if idx == len(rotations)-1 else f"P{idx}")
                
                print(f"\n  Mengedit rotasi {label}")
                print(f"  Rotasi saat ini: X={old_rot['x']}°, Y={old_rot['y']}°, Z={old_rot['z']}°")
                new_rot = self._input_single_rotation(old_rot['x'], old_rot['y'], old_rot['z'])
                
                self.visualizer.show_rotation_at_position(point, new_rot['x'], new_rot['y'], new_rot['z'], label)
                
                if self._get_yes_no(f"Konfirmasi rotasi ({new_rot['x']}°, {new_rot['y']}°, {new_rot['z']}°)?", default_yes=True):
                    rotations[idx] = new_rot
                    print("Rotasi diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 2:
                print("\n--- SET SEMUA ROTASI SAMA ---")
                new_rot = self._input_single_rotation()
                
                if self._get_yes_no(f"Set semua rotasi ke ({new_rot['x']}°, {new_rot['y']}°, {new_rot['z']}°)?", default_yes=True):
                    rotations = [new_rot.copy() for _ in self.translation_points]
                    print("Semua rotasi diupdate!")
                else:
                    print("Dibatalkan.")
            
            elif choice == 3:
                print("\n" + "=" * 50)
                print("  KONFIRMASI ROTASI")
                print("=" * 50)
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
        print(" "*15 + "ROCKET ANIMATION CONFIGURATOR")
        print("="*70)
        print("\n  Program ini akan memandu Anda mengatur animasi roket.")
        print("  Visualisasi REAL-TIME ditampilkan di Matplotlib.")
        print("\n  Tampilan:")
        print("    - KIRI  : Scene 3D (tampilan keseluruhan)")
        print("    - KANAN : Sudut Pandang Kamera 2D (apa yang kamera lihat)")
        print("\n  Tips: Tekan ENTER untuk nilai default")
        print("\n" + "="*70)
        
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
        print("  KONFIGURASI SELESAI!")
        print("="*70)
        print("\n  Semua pengaturan telah disimpan.")
        print("  Memulai proses render...")
        
        self.visualizer.close()
        return self.config

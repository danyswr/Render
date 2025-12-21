from typing import List, Dict, Optional
from visualizer import Visualizer
from config_manager import ConfigManager

class InteractiveInput:
    """Handles interactive user input with real-time rocket visualization"""
    
    def __init__(self):
        self.visualizer = Visualizer()
        self.config = ConfigManager()
        self.translation_points: List[List[float]] = []
        self.rotations: List[Dict[str, float]] = []
        self.camera_position: List[float] = [0.0, 0.0, -150.0]
        self.camera_rotation: Dict[str, float] = {"x": 0.0, "y": 0.0}
        self.total_frames: int = 1
    
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
        """Get integer input from user within range"""
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
        """Get yes/no input"""
        default_hint = "Y/n" if default_yes else "y/N"
        while True:
            response = input(f"{prompt} ({default_hint}): ").strip().lower()
            if response == '':
                return default_yes
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            print("Tekan Enter untuk default, atau ketik 'y'/'n'")
    
    def _display_menu(self, options: List[str], default: int = 1):
        """Display menu options"""
        print("\n" + "-" * 35)
        print("  OPSI:")
        print("-" * 35)
        for i, opt in enumerate(options):
            marker = " [Enter]" if i + 1 == default else ""
            print(f"  {i+1}. {opt}{marker}")
        print("-" * 35)
    
    def _display_points_table(self, points: List[List[float]], title: str = "DAFTAR TITIK"):
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
    
    def _input_xyz_realtime(self, prompt: str, default_x=0.0, default_y=0.0, default_z=0.0) -> List[float]:
        """Input XYZ with real-time updates"""
        print(f"\n{prompt}")
        print(f"  Default: ({default_x:.1f}, {default_y:.1f}, {default_z:.1f})")
        print("  [Tekan ENTER tanpa angka untuk gunakan default]")
        
        x = self._get_float_input(f"  X [{default_x:.1f}]: ", default_x)
        self.visualizer.show_translation_with_rocket(self.translation_points, [x, default_y, default_z], self.rotations)
        
        y = self._get_float_input(f"  Y [{default_y:.1f}]: ", default_y)
        self.visualizer.show_translation_with_rocket(self.translation_points, [x, y, default_z], self.rotations)
        
        z = self._get_float_input(f"  Z [{default_z:.1f}]: ", default_z)
        self.visualizer.show_translation_with_rocket(self.translation_points, [x, y, z], self.rotations)
        
        return [x, y, z]
    
    def _input_rotation_realtime(self, default_x=0.0, default_y=0.0) -> Dict[str, float]:
        """Input rotation (X, Y only) with real-time updates"""
        print(f"\n  Default: Pitch={default_x}°, Yaw={default_y}°")
        print("  [Tekan ENTER tanpa angka untuk gunakan default]")
        
        x = self._get_float_input(f"  Pitch/X [{default_x}]: ", default_x)
        self.visualizer.show_camera_setup_realtime(self.translation_points[-1] if self.translation_points else [0, 0, 0], 
                                                   {"x": x, "y": default_y})
        
        y = self._get_float_input(f"  Yaw/Y [{default_y}]: ", default_y)
        self.visualizer.show_camera_setup_realtime(self.translation_points[-1] if self.translation_points else [0, 0, 0], 
                                                   {"x": x, "y": y})
        
        return {"x": x, "y": y}
    
    def _input_camera_position_realtime(self, default_x=0.0, default_y=0.0, default_z=-150.0) -> List[float]:
        """Input camera position with real-time visualization"""
        print(f"\n  Default: ({default_x:.1f}, {default_y:.1f}, {default_z:.1f})")
        print("  [Tekan ENTER tanpa angka untuk gunakan default]")
        print("  Tips: Z negatif = kamera di belakang objek")
        
        x = self._get_float_input(f"  X [{default_x:.1f}]: ", default_x)
        self.visualizer.set_camera_position(x, default_y, default_z)
        self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": 0, "y": 0})
        
        y = self._get_float_input(f"  Y [{default_y:.1f}]: ", default_y)
        self.visualizer.set_camera_position(x, y, default_z)
        self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": 0, "y": 0})
        
        z = self._get_float_input(f"  Z [{default_z:.1f}]: ", default_z)
        self.visualizer.set_camera_position(x, y, z)
        self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": 0, "y": 0})
        
        return [x, y, z]
    
    def input_camera_stage(self):
        """Stage 0: Setup camera with translation and rotation (X,Y only)"""
        print("\n" + "="*60)
        print("  TAHAP 0: PENGATURAN KAMERA")
        print("="*60)
        print("  Atur posisi dan rotasi kamera.")
        print("  Kiri = Scene 3D | Kanan = Sudut Pandang Kamera 2D")
        print("-"*60)
        
        cam_x, cam_y, cam_z = 0.0, 0.0, -150.0
        rot_x, rot_y = 0.0, 0.0
        
        self.visualizer.set_camera_position(cam_x, cam_y, cam_z)
        self.visualizer.set_camera_rotation(rot_x, rot_y)
        self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": 0, "y": 0})
        
        while True:
            print("\n" + "=" * 45)
            print("  KAMERA SAAT INI")
            print("=" * 45)
            print(f"  Posisi : ({cam_x:.1f}, {cam_y:.1f}, {cam_z:.1f})")
            print(f"  Rotasi : Pitch={rot_x:.1f}°, Yaw={rot_y:.1f}°")
            print("=" * 45)
            
            self._display_menu(["Edit Posisi Kamera", "Edit Rotasi Kamera", "Konfirmasi"], default=3)
            
            choice = self._get_int_input("Pilih opsi: ", 1, 3, default=3)
            if choice == -1:
                choice = 3
            
            if choice == 1:
                print("\n--- EDIT POSISI KAMERA (X, Y, Z) ---")
                pos_input = self._input_camera_position_realtime(cam_x, cam_y, cam_z)
                cam_x, cam_y, cam_z = pos_input[0], pos_input[1], pos_input[2]
                
                self.visualizer.set_camera_position(cam_x, cam_y, cam_z)
                self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": rot_x, "y": rot_y})
                print("Posisi kamera diupdate!")
            
            elif choice == 2:
                print("\n--- EDIT ROTASI KAMERA (PITCH, YAW) ---")
                print("Tips: Pitch mengubah arah vertikal, Yaw mengubah arah horizontal")
                rot_input = self._input_rotation_realtime(rot_x, rot_y)
                rot_x, rot_y = rot_input['x'], rot_input['y']
                
                self.visualizer.set_camera_rotation(rot_x, rot_y)
                self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": rot_x, "y": rot_y})
                print("Rotasi kamera diupdate!")
            
            elif choice == 3:
                print("\n" + "=" * 45)
                print("  KONFIRMASI PENGATURAN KAMERA")
                print("=" * 45)
                print(f"  Posisi : ({cam_x:.1f}, {cam_y:.1f}, {cam_z:.1f})")
                print(f"  Rotasi : Pitch={rot_x:.1f}°, Yaw={rot_y:.1f}°")
                print("=" * 45)
                
                if self._get_yes_no("Konfirmasi pengaturan kamera?", default_yes=True):
                    self.camera_position = [cam_x, cam_y, cam_z]
                    self.camera_rotation = {"x": rot_x, "y": rot_y}
                    self.visualizer.set_camera_position(cam_x, cam_y, cam_z)
                    self.visualizer.set_camera_rotation(rot_x, rot_y)
                    print("Pengaturan kamera dikonfirmasi!")
                    break
                else:
                    print("Kembali ke menu...")
        
        return True
    
    def input_translation_stage(self):
        """Stage 1: Input translation path"""
        print("\n" + "="*60)
        print("  TAHAP 1: JALUR TRANSLASI OBJECT")
        print("="*60)
        print("  1. Tentukan titik AWAL (START)")
        print("  2. Tambahkan titik-titik lainnya")
        print("  3. Titik terakhir = titik AKHIR (END)")
        print("-"*60)
        
        points = []
        
        print("\n>>> LANGKAH 1: Tentukan Titik Awal (START)")
        start_point = self._input_xyz_realtime("Koordinat titik START:", 0.0, 0.0, 0.0)
        self.visualizer.show_translation_with_rocket([], start_point)
        
        print(f"\n  Titik START: ({start_point[0]:.1f}, {start_point[1]:.1f}, {start_point[2]:.1f})")
        if self._get_yes_no("Konfirmasi titik START?", default_yes=True):
            points.append(start_point)
            print("Titik START ditambahkan!")
        else:
            while True:
                start_point = self._input_xyz_realtime("Koordinat titik START:", 0.0, 0.0, 0.0)
                self.visualizer.show_translation_with_rocket([], start_point)
                if self._get_yes_no("Konfirmasi titik START?", default_yes=True):
                    points.append(start_point)
                    break
        
        print("\n>>> LANGKAH 2: Tambahkan Titik Lainnya")
        
        while True:
            self._display_points_table(points)
            self.visualizer.show_translation_with_rocket(points, None, self.rotations)
            
            if len(points) >= 2:
                self._display_menu(["Tambah Titik Baru", "Edit Titik", "Hapus Titik", "Konfirmasi Jalur"], default=4)
                choice = self._get_int_input("Pilih opsi: ", 1, 4, default=4)
                if choice == -1:
                    choice = 4
            else:
                self._display_menu(["Tambah Titik Baru", "Edit Titik", "Hapus Titik", "Konfirmasi Jalur"], default=1)
                choice = self._get_int_input("Pilih opsi: ", 1, 4, default=1)
                if choice == -1:
                    choice = 1
            
            if choice == 1:
                print("\n--- TAMBAH TITIK BARU ---")
                last = points[-1] if points else [0.0, 0.0, 0.0]
                new_point = self._input_xyz_realtime(f"Koordinat titik P{len(points)}:", last[0], last[1], last[2])
                self.visualizer.show_translation_with_rocket(points, new_point)
                
                if self._get_yes_no("Konfirmasi tambah titik ini?", default_yes=True):
                    points.append(new_point)
                    print("Titik ditambahkan!")
            
            elif choice == 2:
                if len(points) == 0:
                    print("\nBelum ada titik untuk diedit.")
                    continue
                
                print("\n--- EDIT TITIK ---")
                self._display_points_table(points)
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(points)}): ", 1, len(points))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                old = points[idx]
                label = "START" if idx == 0 else ("END" if idx == len(points)-1 else f"P{idx}")
                
                new_point = self._input_xyz_realtime(f"Koordinat baru untuk {label}:", old[0], old[1], old[2])
                temp_points = points[:idx] + [new_point] + points[idx+1:]
                self.visualizer.show_translation_with_rocket(temp_points, None)
                
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
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(points)}): ", 1, len(points))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                old = points[idx]
                label = "START" if idx == 0 else ("END" if idx == len(points)-1 else f"P{idx}")
                
                print(f"\n  Akan menghapus {label}: ({old[0]:.1f}, {old[1]:.1f}, {old[2]:.1f})")
                if self._get_yes_no("Konfirmasi hapus?", default_yes=False):
                    points.pop(idx)
                    if self.rotations and len(self.rotations) > idx:
                        self.rotations.pop(idx)
                    print("Titik dihapus!")
            
            elif choice == 4:
                if len(points) < 2:
                    print("\n[!] Minimal 2 titik diperlukan (START dan END).")
                    continue
                
                print("\n" + "=" * 55)
                print("  KONFIRMASI JALUR TRANSLASI")
                print("=" * 55)
                self._display_points_table(points, "JALUR FINAL")
                
                if self._get_yes_no("Konfirmasi jalur ini?", default_yes=True):
                    self.translation_points = points
                    print("Jalur translasi dikonfirmasi!")
                    break
        
        return True
    
    def input_rotation_stage(self):
        """Stage 2: Input rotation per point (X, Y only)"""
        print("\n" + "="*60)
        print("  TAHAP 2: ROTASI OBJECT PER TITIK")
        print("="*60)
        print("  Atur rotasi object di setiap titik (Pitch & Yaw saja).")
        print("-"*60)
        
        rotations = [{"x": 0.0, "y": 0.0} for _ in self.translation_points]
        
        def display_rotations():
            print("\n" + "=" * 70)
            print("  DAFTAR ROTASI")
            print("=" * 70)
            print("  No.  | Label  | Koordinat          | Pitch, Yaw")
            print("  " + "-" * 65)
            for i, (point, rot) in enumerate(zip(self.translation_points, rotations)):
                if i == 0:
                    label = "START"
                elif i == len(self.translation_points) - 1:
                    label = "END"
                else:
                    label = f"P{i}"
                coord = f"({point[0]:.0f}, {point[1]:.0f}, {point[2]:.0f})"
                rot_str = f"Pitch={rot['x']:.0f}°, Yaw={rot['y']:.0f}°"
                print(f"  {i+1:3}.  | {label:6} | {coord:18} | {rot_str}")
            print("=" * 70)
        
        while True:
            display_rotations()
            
            self._display_menu(["Edit Rotasi Titik", "Set Semua Sama", "Konfirmasi"], default=3)
            
            choice = self._get_int_input("Pilih opsi: ", 1, 3, default=3)
            if choice == -1:
                choice = 3
            
            if choice == 1:
                print("\n--- EDIT ROTASI ---")
                display_rotations()
                idx = self._get_int_input(f"Pilih nomor titik (1-{len(rotations)}): ", 1, len(rotations))
                if idx == -1:
                    print("Dibatalkan.")
                    continue
                
                idx -= 1
                point = self.translation_points[idx]
                old_rot = rotations[idx]
                label = "START" if idx == 0 else ("END" if idx == len(rotations)-1 else f"P{idx}")
                
                print(f"\n  Mengedit rotasi {label}")
                print(f"  Rotasi saat ini: Pitch={old_rot['x']}°, Yaw={old_rot['y']}°")
                new_rot = self._input_rotation_realtime(old_rot['x'], old_rot['y'])
                
                self.visualizer.show_camera_setup_realtime(point, new_rot)
                
                if self._get_yes_no(f"Konfirmasi rotasi?", default_yes=True):
                    rotations[idx] = new_rot
                    print("Rotasi diupdate!")
            
            elif choice == 2:
                print("\n--- SET SEMUA ROTASI SAMA ---")
                new_rot = self._input_rotation_realtime()
                
                if self._get_yes_no(f"Set semua rotasi ke Pitch={new_rot['x']}°, Yaw={new_rot['y']}°?", default_yes=True):
                    rotations = [new_rot.copy() for _ in self.translation_points]
                    print("Semua rotasi diupdate!")
            
            elif choice == 3:
                print("\n" + "=" * 50)
                print("  KONFIRMASI ROTASI")
                print("=" * 50)
                display_rotations()
                if self._get_yes_no("Konfirmasi rotasi ini?", default_yes=True):
                    self.rotations = rotations
                    print("Rotasi dikonfirmasi!")
                    break
        
        return True
    
    def input_frame_count_stage(self):
        """Stage 3: Input total frames to render"""
        print("\n" + "="*60)
        print("  TAHAP 3: JUMLAH FRAME RENDERING")
        print("="*60)
        print("  Berapa banyak frame yang ingin di-render?")
        print("-"*60)
        
        frames = self._get_int_input(f"\nJumlah frame (1-1000) [1]: ", 1, 1000, default=1)
        if frames == -1:
            frames = 1
        
        self.total_frames = frames
        print(f"Total frame diset ke {frames}")
        
        return True
    
    def run(self) -> ConfigManager:
        """Run complete interactive input process"""
        print("\n" + "="*70)
        print(" "*10 + "ROCKET 3D RENDERER - INTERACTIVE CONFIGURATOR v2")
        print("="*70)
        print("\nProgram ini akan memandu Anda mengatur animasi roket.")
        print("Visualisasi REAL-TIME ditampilkan dengan rocket model asli!")
        print("\nTahap:")
        print("  0. Setup Kamera (posisi & rotasi)")
        print("  1. Jalur Translasi Object")
        print("  2. Rotasi Object (Pitch & Yaw)")
        print("  3. Jumlah Frame")
        print("\n" + "="*70)
        
        load_existing = input("\nLoad existing configuration? (y/N): ").strip().lower()
        
        if load_existing == 'y':
            self.config.load()
            loaded = self.config.get_animation_points()
            if loaded:
                self.translation_points = [p["translation"]["position"] for p in loaded]
                self.rotations = [{"x": p["rotation"]["pitch"], "y": p["rotation"]["yaw"]} for p in loaded]
                cam_settings = self.config.get_camera_settings()
                self.camera_position = cam_settings["translation"]["position"]
                self.camera_rotation = {"x": cam_settings["rotation"]["pitch"], "y": cam_settings["rotation"]["yaw"]}
                self.total_frames = self.config.get_render_settings().get("total_frames", 1)
                print("\n✓ Konfigurasi loaded!")
            return self.config
        
        if not self.input_camera_stage():
            self.visualizer.close()
            return None
        
        if not self.input_translation_stage():
            self.visualizer.close()
            return None
        
        if not self.input_rotation_stage():
            self.visualizer.close()
            return None
        
        if not self.input_frame_count_stage():
            self.visualizer.close()
            return None
        
        # Save to config
        for point, rot in zip(self.translation_points, self.rotations):
            self.config.add_animation_point(
                position=point,
                pitch=rot["x"],
                yaw=rot["y"]
            )
        
        self.config.set_camera_settings(
            position=self.camera_position,
            pitch=self.camera_rotation["x"],
            yaw=self.camera_rotation["y"]
        )
        
        self.config.set_render_settings(total_frames=self.total_frames)
        
        self.config.save()
        print("\n✓ Konfigurasi tersimpan!")
        
        self.visualizer.close()
        
        return self.config

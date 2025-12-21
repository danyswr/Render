import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from config_manager import ConfigManager
from visualizer import Visualizer
import threading


class GUIInput:
    """Simple GUI untuk input konfigurasi - matplotlib visualization tetap terpisah"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Rocket 3D Renderer - Configuration")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        
        self.config = ConfigManager()
        self.visualizer = Visualizer()
        
        # Configuration data
        self.camera_position = [0.0, 0.0, -150.0]
        self.camera_rotation = {"x": 0.0, "y": 0.0}
        self.translation_points = []
        self.rotations = []
        self.camera_translation_points = []
        self.camera_rotations = []
        self.total_frames = 1
        
        self.result = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup main UI dengan dua pilihan utama"""
        # Header
        header = ttk.Frame(self.window)
        header.pack(fill=tk.X, padx=15, pady=15)
        
        title = ttk.Label(header, text="ROCKET 3D RENDERER - Configuration", 
                         font=("Arial", 12, "bold"))
        title.pack()
        
        subtitle = ttk.Label(header, text="Setup Camera or Object - Choose order freely",
                            font=("Arial", 9))
        subtitle.pack()
        
        # Main frame dengan notebook (tabs)
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Tab 1: Camera Setup
        self.camera_frame = ttk.Frame(notebook)
        notebook.add(self.camera_frame, text="Camera Setup")
        self.setup_camera_tab()
        
        # Tab 2: Object Setup
        self.object_frame = ttk.Frame(notebook)
        notebook.add(self.object_frame, text="Object Setup")
        self.setup_object_tab()
        
        # Tab 3: Load Config
        self.load_frame = ttk.Frame(notebook)
        notebook.add(self.load_frame, text="Load Config")
        self.setup_load_tab()
        
        # Bottom buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        ttk.Button(btn_frame, text="Apply & Render", 
                  command=self.apply_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=5)
        
        # Status
        self.status = ttk.Label(self.window, text="Status: Ready", 
                               font=("Arial", 8), foreground="blue")
        self.status.pack(fill=tk.X, padx=15, pady=5)
    
    def setup_camera_tab(self):
        """Tab untuk camera setup"""
        # Posisi
        pos_frame = ttk.LabelFrame(self.camera_frame, text="Camera Position (X, Y, Z)", padding=10)
        pos_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.cam_x = tk.DoubleVar(value=0.0)
        self.cam_y = tk.DoubleVar(value=0.0)
        self.cam_z = tk.DoubleVar(value=-150.0)
        
        ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(pos_frame, textvariable=self.cam_x, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(pos_frame, textvariable=self.cam_y, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(pos_frame, text="Z:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(pos_frame, textvariable=self.cam_z, width=10).pack(side=tk.LEFT, padx=5)
        
        # Rotasi
        rot_frame = ttk.LabelFrame(self.camera_frame, text="Camera Rotation (degrees)", padding=10)
        rot_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.cam_pitch = tk.DoubleVar(value=0.0)
        self.cam_yaw = tk.DoubleVar(value=0.0)
        
        ttk.Label(rot_frame, text="Pitch:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(rot_frame, textvariable=self.cam_pitch, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(rot_frame, text="Yaw:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(rot_frame, textvariable=self.cam_yaw, width=10).pack(side=tk.LEFT, padx=5)
        
        # Animation points
        anim_frame = ttk.LabelFrame(self.camera_frame, text="Camera Animation Points", padding=10)
        anim_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Listbox
        list_frame = ttk.Frame(anim_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cam_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=5)
        self.cam_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.cam_listbox.yview)
        
        # Buttons
        btn_frame = ttk.Frame(anim_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Add Point", 
                  command=self.add_camera_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", 
                  command=self.remove_camera_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Camera", 
                  command=self.save_camera).pack(side=tk.RIGHT, padx=5)
    
    def setup_object_tab(self):
        """Tab untuk object setup"""
        # Translation points
        trans_frame = ttk.LabelFrame(self.object_frame, text="Translation Points", padding=10)
        trans_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Input fields
        input_frame = ttk.Frame(trans_frame)
        input_frame.pack(fill=tk.X, pady=10)
        
        self.trans_x = tk.DoubleVar(value=0.0)
        self.trans_y = tk.DoubleVar(value=0.0)
        self.trans_z = tk.DoubleVar(value=0.0)
        self.rot_pitch = tk.DoubleVar(value=0.0)
        self.rot_yaw = tk.DoubleVar(value=0.0)
        
        ttk.Label(input_frame, text="X:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(input_frame, textvariable=self.trans_x, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(input_frame, text="Y:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(input_frame, textvariable=self.trans_y, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(input_frame, text="Z:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(input_frame, textvariable=self.trans_z, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(input_frame, text="Pitch:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(input_frame, textvariable=self.rot_pitch, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(input_frame, text="Yaw:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(input_frame, textvariable=self.rot_yaw, width=8).pack(side=tk.LEFT, padx=3)
        
        # Listbox
        list_frame = ttk.Frame(trans_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=5)
        self.trans_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.trans_listbox.yview)
        
        # Buttons
        btn_frame = ttk.Frame(trans_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Add Point", 
                  command=self.add_translation_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", 
                  command=self.remove_translation_point).pack(side=tk.LEFT, padx=5)
        
        # Frame count
        frame_frame = ttk.LabelFrame(self.object_frame, text="Render Settings", padding=10)
        frame_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(frame_frame, text="Total Frames:").pack(side=tk.LEFT, padx=5)
        self.frame_var = tk.IntVar(value=1)
        ttk.Spinbox(frame_frame, from_=1, to=100, textvariable=self.frame_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_frame, text="Save Object", 
                  command=self.save_object).pack(side=tk.RIGHT, padx=5)
    
    def setup_load_tab(self):
        """Tab untuk load existing config"""
        info = ttk.Label(self.load_frame, 
                        text="Click button di bawah untuk load konfigurasi yang sudah tersimpan",
                        font=("Arial", 9))
        info.pack(pady=20)
        
        ttk.Button(self.load_frame, text="Load Existing Configuration",
                  command=self.load_config).pack(pady=20)
        
        self.load_status = ttk.Label(self.load_frame, text="", font=("Arial", 8), 
                                    foreground="green")
        self.load_status.pack(pady=10)
    
    def add_camera_point(self):
        """Tambah camera animation point"""
        try:
            point = [self.cam_x.get(), self.cam_y.get(), self.cam_z.get()]
            rotation = {"x": self.cam_pitch.get(), "y": self.cam_yaw.get()}
            
            self.camera_translation_points.append(point)
            self.camera_rotations.append(rotation)
            
            self.update_cam_listbox()
            self.status.config(text="Status: Camera point added")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def remove_camera_point(self):
        """Hapus camera point yang dipilih"""
        sel = self.cam_listbox.curselection()
        if sel:
            idx = sel[0]
            self.camera_translation_points.pop(idx)
            self.camera_rotations.pop(idx)
            self.update_cam_listbox()
            self.status.config(text="Status: Camera point removed")
    
    def update_cam_listbox(self):
        """Update display listbox camera"""
        self.cam_listbox.delete(0, tk.END)
        for i, p in enumerate(self.camera_translation_points):
            label = "CAM_START" if i == 0 else ("CAM_END" if i == len(self.camera_translation_points)-1 else f"CAM_P{i}")
            rot = self.camera_rotations[i] if i < len(self.camera_rotations) else {"x": 0, "y": 0}
            self.cam_listbox.insert(tk.END, 
                f"{label}: ({p[0]:.1f},{p[1]:.1f},{p[2]:.1f}) P={rot['x']:.0f}° Y={rot['y']:.0f}°")
    
    def add_translation_point(self):
        """Tambah translation point"""
        try:
            point = [self.trans_x.get(), self.trans_y.get(), self.trans_z.get()]
            rotation = {"x": self.rot_pitch.get(), "y": self.rot_yaw.get()}
            
            self.translation_points.append(point)
            self.rotations.append(rotation)
            
            self.update_trans_listbox()
            self.status.config(text="Status: Translation point added")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def remove_translation_point(self):
        """Hapus translation point yang dipilih"""
        sel = self.trans_listbox.curselection()
        if sel:
            idx = sel[0]
            self.translation_points.pop(idx)
            self.rotations.pop(idx)
            self.update_trans_listbox()
            self.status.config(text="Status: Translation point removed")
    
    def update_trans_listbox(self):
        """Update display listbox translation"""
        self.trans_listbox.delete(0, tk.END)
        for i, p in enumerate(self.translation_points):
            label = "START" if i == 0 else ("END" if i == len(self.translation_points)-1 else f"P{i}")
            rot = self.rotations[i] if i < len(self.rotations) else {"x": 0, "y": 0}
            self.trans_listbox.insert(tk.END, f"{label}: ({p[0]:.1f},{p[1]:.1f},{p[2]:.1f}) P={rot['x']:.0f}° Y={rot['y']:.0f}°")
    
    def save_camera(self):
        """Save camera settings"""
        try:
            self.camera_position = [self.cam_x.get(), self.cam_y.get(), self.cam_z.get()]
            self.camera_rotation = {"x": self.cam_pitch.get(), "y": self.cam_yaw.get()}
            self.status.config(text="Status: Camera settings saved")
            messagebox.showinfo("Success", "Camera settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def save_object(self):
        """Save object settings"""
        try:
            self.total_frames = self.frame_var.get()
            self.status.config(text="Status: Object settings saved")
            messagebox.showinfo("Success", "Object settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def load_config(self):
        """Load existing configuration"""
        try:
            self.config.load()
            
            # Load camera
            cam_settings = self.config.get_camera_settings()
            self.camera_position = cam_settings["translation"]["position"]
            self.camera_rotation = {
                "x": cam_settings["rotation"]["pitch"],
                "y": cam_settings["rotation"]["yaw"]
            }
            
            self.camera_translation_points = []
            self.camera_rotations = []
            for point in cam_settings.get("animation_points", []):
                self.camera_translation_points.append(point["translation"]["position"])
                self.camera_rotations.append({
                    "x": point["rotation"]["pitch"],
                    "y": point["rotation"]["yaw"]
                })
            
            # Load object
            obj_points = self.config.get_animation_points()
            self.translation_points = []
            self.rotations = []
            for point in obj_points:
                self.translation_points.append(point["translation"]["position"])
                self.rotations.append({
                    "x": point["rotation"]["pitch"],
                    "y": point["rotation"]["yaw"]
                })
            
            self.total_frames = self.config.get_render_settings()["total_frames"]
            
            self.load_status.config(text="✓ Configuration loaded successfully!")
            self.status.config(text="Status: Configuration loaded")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")
            self.load_status.config(text="✗ Load failed", foreground="red")
    
    def apply_config(self):
        """Apply konfigurasi dan siap render"""
        try:
            # Validate
            if len(self.translation_points) == 0:
                self.translation_points = [[0.0, 0.0, 0.0]]
                self.rotations = [{"x": 0.0, "y": 0.0}]
            
            # Save config
            self.config.clear_object_animation_points()
            self.config.clear_camera_animation_points()
            
            for i, point in enumerate(self.translation_points):
                rot = self.rotations[i] if i < len(self.rotations) else {"x": 0.0, "y": 0.0}
                self.config.add_animation_point(point, rot["x"], rot["y"])
            
            for i, point in enumerate(self.camera_translation_points):
                rot = self.camera_rotations[i] if i < len(self.camera_rotations) else {"x": 0.0, "y": 0.0}
                self.config.add_camera_animation_point(point, rot["x"], rot["y"])
            
            if len(self.camera_translation_points) == 0:
                self.config.set_camera_settings(self.camera_position, 
                                                self.camera_rotation["x"], 
                                                self.camera_rotation["y"])
            
            self.config.set_render_settings(self.total_frames)
            self.config.save()
            
            self.result = self.config
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply: {e}")
    
    def cancel(self):
        """Cancel"""
        if messagebox.askyesno("Cancel", "Batalkan konfigurasi?"):
            self.result = None
            self.window.destroy()
    
    def run(self) -> Optional[ConfigManager]:
        """Run GUI dan return config"""
        self.window.mainloop()
        return self.result

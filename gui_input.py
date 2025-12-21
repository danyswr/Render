import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from config_manager import ConfigManager
from visualizer import Visualizer
import matplotlib.pyplot as plt


class GUIInput:
    """Simple GUI untuk input konfigurasi - matplotlib ditampilkan langsung"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Rocket 3D Renderer - Configuration")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
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
        
        # Show matplotlib awal
        self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": 0, "y": 0})
        plt.show(block=False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup main UI dengan tab"""
        # Header
        header = ttk.Frame(self.window)
        header.pack(fill=tk.X, padx=15, pady=10)
        
        title = ttk.Label(header, text="ROCKET 3D RENDERER - Configuration", 
                         font=("Arial", 12, "bold"))
        title.pack()
        
        subtitle = ttk.Label(header, text="Setup Camera atau Object - Bebas urutan! Matplotlib ditampilkan di samping",
                            font=("Arial", 9))
        subtitle.pack()
        
        # Main container dengan scrollbar
        canvas_container = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas_container.yview)
        scrollable_frame = ttk.Frame(canvas_container)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_container.configure(scrollregion=canvas_container.bbox("all"))
        )
        
        canvas_container.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_container.configure(yscrollcommand=scrollbar.set)
        
        # Tab setup dengan 3 tab
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
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
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Apply & Render", 
                  command=self.apply_config).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=5)
        
        # Status
        self.status = ttk.Label(scrollable_frame, text="Status: Ready", 
                               font=("Arial", 8), foreground="blue")
        self.status.pack(fill=tk.X, padx=10, pady=5)
        
        canvas_container.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_camera_tab(self):
        """Tab untuk camera setup"""
        # Buat scrollbar untuk camera tab
        canvas = tk.Canvas(self.camera_frame)
        scrollbar = ttk.Scrollbar(self.camera_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Posisi
        pos_frame = ttk.LabelFrame(scrollable, text="Position (X, Y, Z)", padding=8)
        pos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.cam_x = tk.DoubleVar(value=0.0)
        self.cam_y = tk.DoubleVar(value=0.0)
        self.cam_z = tk.DoubleVar(value=-150.0)
        
        ttk.Label(pos_frame, text="X:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(pos_frame, textvariable=self.cam_x, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(pos_frame, text="Y:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(pos_frame, textvariable=self.cam_y, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(pos_frame, text="Z:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(pos_frame, textvariable=self.cam_z, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(pos_frame, text="Save Pos", command=self.save_camera).pack(side=tk.RIGHT, padx=5)
        
        # Rotasi
        rot_frame = ttk.LabelFrame(scrollable, text="Rotation (Pitch, Yaw)", padding=8)
        rot_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.cam_pitch = tk.DoubleVar(value=0.0)
        self.cam_yaw = tk.DoubleVar(value=0.0)
        
        ttk.Label(rot_frame, text="Pitch:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(rot_frame, textvariable=self.cam_pitch, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(rot_frame, text="Yaw:").pack(side=tk.LEFT, padx=3)
        ttk.Entry(rot_frame, textvariable=self.cam_yaw, width=8).pack(side=tk.LEFT, padx=3)
        
        ttk.Button(rot_frame, text="Update", command=self.update_vis).pack(side=tk.RIGHT, padx=5)
        
        # Animation points
        anim_frame = ttk.LabelFrame(scrollable, text="Animation Points", padding=8)
        anim_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox
        list_frame = ttk.Frame(anim_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar2 = ttk.Scrollbar(list_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cam_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar2.set, height=4)
        self.cam_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.cam_listbox.yview)
        
        # Buttons
        btn_frame = ttk.Frame(anim_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Add", command=self.add_camera_point).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="Remove", command=self.remove_camera_point).pack(side=tk.LEFT, padx=3)
        
        canvas.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_object_tab(self):
        """Tab untuk object setup"""
        # Buat scrollbar
        canvas = tk.Canvas(self.object_frame)
        scrollbar = ttk.Scrollbar(self.object_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Input fields
        input_frame = ttk.LabelFrame(scrollable, text="Add Translation Point", padding=8)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.trans_x = tk.DoubleVar(value=0.0)
        self.trans_y = tk.DoubleVar(value=0.0)
        self.trans_z = tk.DoubleVar(value=0.0)
        self.rot_pitch = tk.DoubleVar(value=0.0)
        self.rot_yaw = tk.DoubleVar(value=0.0)
        
        ttk.Label(input_frame, text="X:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(input_frame, textvariable=self.trans_x, width=7).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Y:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(input_frame, textvariable=self.trans_y, width=7).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Z:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(input_frame, textvariable=self.trans_z, width=7).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="P:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(input_frame, textvariable=self.rot_pitch, width=7).pack(side=tk.LEFT, padx=2)
        
        ttk.Label(input_frame, text="Y:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(input_frame, textvariable=self.rot_yaw, width=7).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(input_frame, text="Add", command=self.add_translation_point).pack(side=tk.LEFT, padx=5)
        
        # Translation listbox
        trans_frame = ttk.LabelFrame(scrollable, text="Translation Points", padding=8)
        trans_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        list_frame = ttk.Frame(trans_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar2 = ttk.Scrollbar(list_frame)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar2.set, height=4)
        self.trans_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar2.config(command=self.trans_listbox.yview)
        
        # Buttons
        btn_frame = ttk.Frame(trans_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Remove", command=self.remove_translation_point).pack(side=tk.LEFT, padx=3)
        
        # Frame count
        frame_frame = ttk.LabelFrame(scrollable, text="Render Settings", padding=8)
        frame_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame_frame, text="Total Frames:").pack(side=tk.LEFT, padx=5)
        self.frame_var = tk.IntVar(value=1)
        ttk.Spinbox(frame_frame, from_=1, to=100, textvariable=self.frame_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_frame, text="Save", command=self.save_object).pack(side=tk.RIGHT, padx=5)
        
        canvas.pack(fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_load_tab(self):
        """Tab untuk load config"""
        info = ttk.Label(self.load_frame, 
                        text="Load konfigurasi yang sudah tersimpan",
                        font=("Arial", 10), justify=tk.CENTER)
        info.pack(pady=30)
        
        ttk.Button(self.load_frame, text="Load Configuration",
                  command=self.load_config).pack(pady=20)
        
        self.load_status = ttk.Label(self.load_frame, text="", font=("Arial", 9), 
                                    foreground="green")
        self.load_status.pack(pady=10)
    
    def update_vis(self):
        """Update matplotlib visualization"""
        try:
            self.camera_position = [self.cam_x.get(), self.cam_y.get(), self.cam_z.get()]
            self.camera_rotation = {"x": self.cam_pitch.get(), "y": self.cam_yaw.get()}
            self.visualizer.set_camera_position(self.camera_position[0], self.camera_position[1], self.camera_position[2])
            self.visualizer.set_camera_rotation(self.camera_rotation["x"], self.camera_rotation["y"])
            self.visualizer.show_camera_setup_realtime([0, 0, 0], self.camera_rotation)
            plt.draw()
            self.status.config(text="Status: Visualization updated")
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {e}")
    
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
        """Hapus camera point"""
        sel = self.cam_listbox.curselection()
        if sel:
            idx = sel[0]
            self.camera_translation_points.pop(idx)
            self.camera_rotations.pop(idx)
            self.update_cam_listbox()
            self.status.config(text="Status: Camera point removed")
    
    def update_cam_listbox(self):
        """Update camera listbox"""
        self.cam_listbox.delete(0, tk.END)
        for i, p in enumerate(self.camera_translation_points):
            label = "CAM_START" if i == 0 else ("CAM_END" if i == len(self.camera_translation_points)-1 else f"P{i}")
            rot = self.camera_rotations[i] if i < len(self.camera_rotations) else {"x": 0, "y": 0}
            self.cam_listbox.insert(tk.END, 
                f"{label}: ({p[0]:.0f},{p[1]:.0f},{p[2]:.0f}) P={rot['x']:.0f}° Y={rot['y']:.0f}°")
    
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
        """Hapus translation point"""
        sel = self.trans_listbox.curselection()
        if sel:
            idx = sel[0]
            self.translation_points.pop(idx)
            self.rotations.pop(idx)
            self.update_trans_listbox()
            self.status.config(text="Status: Translation point removed")
    
    def update_trans_listbox(self):
        """Update translation listbox"""
        self.trans_listbox.delete(0, tk.END)
        for i, p in enumerate(self.translation_points):
            label = "START" if i == 0 else ("END" if i == len(self.translation_points)-1 else f"P{i}")
            rot = self.rotations[i] if i < len(self.rotations) else {"x": 0, "y": 0}
            self.trans_listbox.insert(tk.END, f"{label}: ({p[0]:.0f},{p[1]:.0f},{p[2]:.0f}) P={rot['x']:.0f}° Y={rot['y']:.0f}°")
    
    def save_camera(self):
        """Save camera settings"""
        try:
            self.camera_position = [self.cam_x.get(), self.cam_y.get(), self.cam_z.get()]
            self.camera_rotation = {"x": self.cam_pitch.get(), "y": self.cam_yaw.get()}
            self.status.config(text="Status: Camera position saved")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
    
    def save_object(self):
        """Save object settings"""
        try:
            self.total_frames = self.frame_var.get()
            self.status.config(text="Status: Object settings saved")
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
            
            self.load_status.config(text="✓ Configuration loaded!")
            self.status.config(text="Status: Configuration loaded")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")
            self.load_status.config(text="✗ Load failed", foreground="red")
    
    def apply_config(self):
        """Apply config"""
        try:
            if len(self.translation_points) == 0:
                self.translation_points = [[0.0, 0.0, 0.0]]
                self.rotations = [{"x": 0.0, "y": 0.0}]
            
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
            messagebox.showerror("Error", f"Failed: {e}")
    
    def cancel(self):
        """Cancel"""
        if messagebox.askyesno("Cancel", "Batalkan?"):
            self.result = None
            self.window.destroy()
    
    def run(self) -> Optional[ConfigManager]:
        """Run GUI"""
        self.window.mainloop()
        return self.result

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from config_manager import ConfigManager
from visualizer import Visualizer
import matplotlib.pyplot as plt


class GUIInput:
    """GUI untuk input konfigurasi - layout yang lebih baik dan lega"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Rocket 3D Renderer - Configuration")
        self.window.geometry("1400x850")
        self.window.minsize(1000, 700)
        
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
        self.current_tab = "camera"
        
        # Show matplotlib awal
        self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": 0, "y": 0})
        plt.show(block=False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup main UI"""
        # Header frame dengan button selector
        header = ttk.Frame(self.window, height=80)
        header.pack(fill=tk.X, padx=20, pady=15)
        
        title = ttk.Label(header, text="ROCKET 3D RENDERER - Configuration", 
                         font=("Arial", 14, "bold"))
        title.pack()
        
        subtitle = ttk.Label(header, text="Matplotlib 3D & 2D ditampilkan di samping - Input di sini",
                            font=("Arial", 10))
        subtitle.pack()
        
        # Tab selector buttons
        selector_frame = ttk.Frame(header)
        selector_frame.pack(pady=10)
        
        ttk.Button(selector_frame, text="Camera Setup", 
                  command=lambda: self.show_tab("camera")).pack(side=tk.LEFT, padx=10)
        ttk.Button(selector_frame, text="Object Setup", 
                  command=lambda: self.show_tab("object")).pack(side=tk.LEFT, padx=10)
        ttk.Button(selector_frame, text="Load Config", 
                  command=lambda: self.show_tab("load")).pack(side=tk.LEFT, padx=10)
        
        # Main content area
        self.content_frame = ttk.Frame(self.window)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Bottom buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Button(btn_frame, text="Render Now", 
                  command=self.render_config).pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame, text="Apply (Save Only)", 
                  command=self.apply_config).pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame, text="Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=10)
        
        # Status
        self.status = ttk.Label(self.window, text="Status: Ready", 
                               font=("Arial", 9), foreground="blue")
        self.status.pack(fill=tk.X, padx=20, pady=5)
        
        # Show first tab
        self.show_tab("camera")
    
    def clear_content(self):
        """Bersihkan content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_tab(self, tab_name):
        """Tampilkan tab yang dipilih"""
        self.current_tab = tab_name
        self.clear_content()
        
        if tab_name == "camera":
            self.setup_camera_tab()
        elif tab_name == "object":
            self.setup_object_tab()
        elif tab_name == "load":
            self.setup_load_tab()
    
    def setup_camera_tab(self):
        """Tab untuk camera setup"""
        # Main container dengan scrollbar
        canvas = tk.Canvas(self.content_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ===== POSISI =====
        pos_frame = ttk.LabelFrame(scrollable, text="CAMERA POSITION", padding=15)
        pos_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Input row
        input_row = ttk.Frame(pos_frame)
        input_row.pack(fill=tk.X, pady=10)
        
        self.cam_x = tk.DoubleVar(value=0.0)
        self.cam_y = tk.DoubleVar(value=0.0)
        self.cam_z = tk.DoubleVar(value=-150.0)
        
        ttk.Label(input_row, text="X:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(input_row, textvariable=self.cam_x, width=15, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(input_row, text="Y:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(input_row, textvariable=self.cam_y, width=15, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(input_row, text="Z:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(input_row, textvariable=self.cam_z, width=15, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(input_row, text="Save Position", command=self.save_camera).pack(side=tk.RIGHT, padx=15)
        
        # ===== ROTASI =====
        rot_frame = ttk.LabelFrame(scrollable, text="CAMERA ROTATION", padding=15)
        rot_frame.pack(fill=tk.X, padx=15, pady=15)
        
        rot_row = ttk.Frame(rot_frame)
        rot_row.pack(fill=tk.X, pady=10)
        
        self.cam_pitch = tk.DoubleVar(value=0.0)
        self.cam_yaw = tk.DoubleVar(value=0.0)
        
        ttk.Label(rot_row, text="Pitch (X):", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(rot_row, textvariable=self.cam_pitch, width=15, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(rot_row, text="Yaw (Y):", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(rot_row, textvariable=self.cam_yaw, width=15, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(rot_row, text="Update View", command=self.update_vis).pack(side=tk.RIGHT, padx=15)
        
        # ===== ANIMATION POINTS =====
        anim_frame = ttk.LabelFrame(scrollable, text="CAMERA ANIMATION POINTS", padding=15)
        anim_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Listbox dengan scrollbar
        list_container = ttk.Frame(anim_frame)
        list_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar2 = ttk.Scrollbar(list_container)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cam_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar2.set, 
                                      font=("Arial", 10), height=8)
        self.cam_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar2.config(command=self.cam_listbox.yview)
        
        self.update_cam_listbox()
        
        # Buttons
        btn_row = ttk.Frame(anim_frame)
        btn_row.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_row, text="Add Point", command=self.add_camera_point).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_row, text="Remove Selected", command=self.remove_camera_point).pack(side=tk.LEFT, padx=10)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_object_tab(self):
        """Tab untuk object setup"""
        canvas = tk.Canvas(self.content_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)
        
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # ===== INPUT SECTION =====
        input_frame = ttk.LabelFrame(scrollable, text="ADD TRANSLATION POINT", padding=15)
        input_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.trans_x = tk.DoubleVar(value=0.0)
        self.trans_y = tk.DoubleVar(value=0.0)
        self.trans_z = tk.DoubleVar(value=0.0)
        self.rot_pitch = tk.DoubleVar(value=0.0)
        self.rot_yaw = tk.DoubleVar(value=0.0)
        
        # Row 1: XYZ
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, pady=10)
        
        ttk.Label(row1, text="X:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(row1, textvariable=self.trans_x, width=12, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(row1, text="Y:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(row1, textvariable=self.trans_y, width=12, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(row1, text="Z:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(row1, textvariable=self.trans_z, width=12, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        # Row 2: Rotation
        row2 = ttk.Frame(input_frame)
        row2.pack(fill=tk.X, pady=10)
        
        ttk.Label(row2, text="Pitch:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(row2, textvariable=self.rot_pitch, width=12, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(row2, text="Yaw:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        ttk.Entry(row2, textvariable=self.rot_yaw, width=12, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(row2, text="Add Translation Point", command=self.add_translation_point).pack(side=tk.RIGHT, padx=15)
        
        # ===== TRANSLATION POINTS LIST =====
        trans_frame = ttk.LabelFrame(scrollable, text="TRANSLATION POINTS", padding=15)
        trans_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        list_container = ttk.Frame(trans_frame)
        list_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        scrollbar2 = ttk.Scrollbar(list_container)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_listbox = tk.Listbox(list_container, yscrollcommand=scrollbar2.set, 
                                       font=("Arial", 10), height=8)
        self.trans_listbox.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar2.config(command=self.trans_listbox.yview)
        
        self.update_trans_listbox()
        
        btn_row = ttk.Frame(trans_frame)
        btn_row.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_row, text="Remove Selected", command=self.remove_translation_point).pack(side=tk.LEFT, padx=10)
        
        # ===== RENDER SETTINGS =====
        frame_frame = ttk.LabelFrame(scrollable, text="RENDER SETTINGS", padding=15)
        frame_frame.pack(fill=tk.X, padx=15, pady=15)
        
        frame_row = ttk.Frame(frame_frame)
        frame_row.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_row, text="Total Frames:", font=("Arial", 11)).pack(side=tk.LEFT, padx=15)
        self.frame_var = tk.IntVar(value=1)
        ttk.Spinbox(frame_row, from_=1, to=100, textvariable=self.frame_var, width=15, font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(frame_row, text="Save Settings", command=self.save_object).pack(side=tk.RIGHT, padx=15)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_load_tab(self):
        """Tab untuk load config"""
        frame = ttk.Frame(self.content_frame)
        frame.pack(fill=tk.BOTH, expand=True)
        
        info = ttk.Label(frame, 
                        text="Load existing configuration dari file",
                        font=("Arial", 12))
        info.pack(pady=50)
        
        ttk.Button(frame, text="Load Configuration",
                  command=self.load_config).pack(pady=30)
        
        self.load_status = ttk.Label(frame, text="", font=("Arial", 10), 
                                    foreground="green")
        self.load_status.pack(pady=20)
    
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
                f"{label}: ({p[0]:.0f},{p[1]:.0f},{p[2]:.0f}) Pitch={rot['x']:.0f}° Yaw={rot['y']:.0f}°")
    
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
            self.trans_listbox.insert(tk.END, f"{label}: ({p[0]:.0f},{p[1]:.0f},{p[2]:.0f}) Pitch={rot['x']:.0f}° Yaw={rot['y']:.0f}°")
    
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
    
    def save_to_config(self):
        """Save current settings to config object"""
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
    
    def apply_config(self):
        """Apply config - save to JSON only"""
        try:
            self.save_to_config()
            self.config.save()
            self.status.config(text="Status: Configuration saved to JSON!")
            messagebox.showinfo("Success", "Configuration saved!\n\nClick 'Render Now' when ready to render.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
    
    def render_config(self):
        """Render config - save and close window to start rendering"""
        try:
            self.save_to_config()
            self.config.save()
            self.result = self.config
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")
    
    def cancel(self):
        """Cancel"""
        if messagebox.askyesno("Cancel", "Batalkan konfigurasi?"):
            self.result = None
            self.window.destroy()
    
    def run(self) -> Optional[ConfigManager]:
        """Run GUI"""
        self.window.mainloop()
        return self.result

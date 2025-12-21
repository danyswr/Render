import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from config_manager import ConfigManager
from visualizer import Visualizer
import threading


class GUIInput:
    """Handles GUI-based input using tkinter for rocket animation configuration"""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Rocket 3D Renderer - Configuration")
        self.window.geometry("900x700")
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
        
        # Current mode
        self.current_mode = None
        self.result = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI"""
        # Header
        header_frame = ttk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title = ttk.Label(header_frame, text="ROCKET 3D RENDERER - CONFIGURATION", 
                         font=("Arial", 14, "bold"))
        title.pack()
        
        subtitle = ttk.Label(header_frame, 
                            text="Choose what to setup first: Camera or Object",
                            font=("Arial", 10))
        subtitle.pack()
        
        # Main content frame
        content_frame = ttk.Frame(self.window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side: Selection buttons
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        left_title = ttk.Label(left_frame, text="Setup Options", font=("Arial", 11, "bold"))
        left_title.pack(pady=10)
        
        camera_btn = ttk.Button(left_frame, text="Setup Camera", 
                               command=self.show_camera_setup,
                               width=30)
        camera_btn.pack(pady=10, fill=tk.X)
        
        object_btn = ttk.Button(left_frame, text="Setup Object", 
                               command=self.show_object_setup,
                               width=30)
        object_btn.pack(pady=10, fill=tk.X)
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=20)
        
        load_btn = ttk.Button(left_frame, text="Load Existing Config",
                             command=self.load_existing_config,
                             width=30)
        load_btn.pack(pady=10, fill=tk.X)
        
        # Right side: Content area
        self.right_frame = ttk.Frame(content_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        self.content_label = ttk.Label(self.right_frame, 
                                       text="Select an option to begin",
                                       font=("Arial", 10))
        self.content_label.pack(pady=20)
        
        # Status frame
        status_frame = ttk.Frame(self.window)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_text = ttk.Label(status_frame, text="Status: Ready", 
                                     font=("Arial", 9))
        self.status_text.pack(anchor=tk.W)
        
        # Bottom buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        apply_btn = ttk.Button(button_frame, text="Apply & Render", 
                              command=self.apply_config)
        apply_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", 
                               command=self.cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def show_camera_setup(self):
        """Show camera setup interface"""
        self.current_mode = "camera"
        self.clear_right_frame()
        
        # Camera setup form
        form_frame = ttk.LabelFrame(self.right_frame, text="Camera Setup", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Position section
        pos_frame = ttk.LabelFrame(form_frame, text="Camera Position", padding=10)
        pos_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(pos_frame, text="X:").grid(row=0, column=0, padx=5, pady=5)
        cam_x_var = tk.DoubleVar(value=self.camera_position[0])
        ttk.Entry(pos_frame, textvariable=cam_x_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(pos_frame, text="Y:").grid(row=0, column=2, padx=5, pady=5)
        cam_y_var = tk.DoubleVar(value=self.camera_position[1])
        ttk.Entry(pos_frame, textvariable=cam_y_var, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(pos_frame, text="Z:").grid(row=1, column=0, padx=5, pady=5)
        cam_z_var = tk.DoubleVar(value=self.camera_position[2])
        ttk.Entry(pos_frame, textvariable=cam_z_var, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(pos_frame, text="(Z negative = behind object)").grid(row=1, column=2, columnspan=2, padx=5, pady=5)
        
        # Rotation section
        rot_frame = ttk.LabelFrame(form_frame, text="Camera Rotation", padding=10)
        rot_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(rot_frame, text="Pitch (X):").grid(row=0, column=0, padx=5, pady=5)
        pitch_var = tk.DoubleVar(value=self.camera_rotation["x"])
        ttk.Entry(rot_frame, textvariable=pitch_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(rot_frame, text="Yaw (Y):").grid(row=0, column=2, padx=5, pady=5)
        yaw_var = tk.DoubleVar(value=self.camera_rotation["y"])
        ttk.Entry(rot_frame, textvariable=yaw_var, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(rot_frame, text="(degrees)").grid(row=0, column=4, padx=5, pady=5)
        
        # Animation points section
        anim_frame = ttk.LabelFrame(form_frame, text="Camera Animation Points", padding=10)
        anim_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Listbox for animation points
        list_frame = ttk.Frame(anim_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.camera_anim_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=6)
        self.camera_anim_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.camera_anim_listbox.yview)
        
        self.update_camera_anim_listbox()
        
        # Add/Edit/Remove buttons
        btn_frame = ttk.Frame(anim_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Add Point", 
                  command=lambda: self.add_camera_point(cam_x_var, cam_y_var, cam_z_var, pitch_var, yaw_var)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", 
                  command=self.remove_selected_camera_point).pack(side=tk.LEFT, padx=5)
        
        # Save button
        save_frame = ttk.Frame(form_frame)
        save_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(save_frame, text="Save Camera Settings",
                  command=lambda: self.save_camera_settings(cam_x_var, cam_y_var, cam_z_var, 
                                                            pitch_var, yaw_var)).pack(side=tk.RIGHT)
        
        self.status_text.config(text="Status: Camera Setup Mode - Enter values and click Save")
    
    def show_object_setup(self):
        """Show object setup interface"""
        self.current_mode = "object"
        self.clear_right_frame()
        
        # Object setup form
        form_frame = ttk.LabelFrame(self.right_frame, text="Object Setup", padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Translation points section
        trans_frame = ttk.LabelFrame(form_frame, text="Translation Points", padding=10)
        trans_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Listbox for translation points
        list_frame = ttk.Frame(trans_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=6)
        self.trans_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.trans_listbox.yview)
        
        self.update_translation_listbox()
        
        # Input section
        input_frame = ttk.LabelFrame(trans_frame, text="Add Translation Point", padding=10)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="X:").grid(row=0, column=0, padx=5, pady=5)
        trans_x_var = tk.DoubleVar(value=0.0)
        ttk.Entry(input_frame, textvariable=trans_x_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Y:").grid(row=0, column=2, padx=5, pady=5)
        trans_y_var = tk.DoubleVar(value=0.0)
        ttk.Entry(input_frame, textvariable=trans_y_var, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Z:").grid(row=1, column=0, padx=5, pady=5)
        trans_z_var = tk.DoubleVar(value=0.0)
        ttk.Entry(input_frame, textvariable=trans_z_var, width=15).grid(row=1, column=1, padx=5, pady=5)
        
        # Rotation section
        rot_frame = ttk.LabelFrame(form_frame, text="Rotation Settings", padding=10)
        rot_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(rot_frame, text="Pitch (X):").grid(row=0, column=0, padx=5, pady=5)
        pitch_var = tk.DoubleVar(value=0.0)
        ttk.Entry(rot_frame, textvariable=pitch_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(rot_frame, text="Yaw (Y):").grid(row=0, column=2, padx=5, pady=5)
        yaw_var = tk.DoubleVar(value=0.0)
        ttk.Entry(rot_frame, textvariable=yaw_var, width=15).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(rot_frame, text="(degrees)").grid(row=0, column=4, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(trans_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Add Translation Point",
                  command=lambda: self.add_translation_point(trans_x_var, trans_y_var, trans_z_var, 
                                                             pitch_var, yaw_var)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected",
                  command=self.remove_selected_translation_point).pack(side=tk.LEFT, padx=5)
        
        # Frame count section
        frame_frame = ttk.LabelFrame(form_frame, text="Render Settings", padding=10)
        frame_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_frame, text="Total Frames:").grid(row=0, column=0, padx=5, pady=5)
        self.frame_var = tk.IntVar(value=self.total_frames)
        ttk.Spinbox(frame_frame, from_=1, to=100, textvariable=self.frame_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(frame_frame, text="Save Object Settings",
                  command=self.save_object_settings).pack(side=tk.RIGHT, padx=5, pady=5)
        
        self.status_text.config(text="Status: Object Setup Mode - Add translation points and set rotation")
    
    def add_translation_point(self, x_var, y_var, z_var, pitch_var, yaw_var):
        """Add a translation point"""
        try:
            point = [x_var.get(), y_var.get(), z_var.get()]
            rotation = {"x": pitch_var.get(), "y": yaw_var.get()}
            
            self.translation_points.append(point)
            self.rotations.append(rotation)
            
            self.update_translation_listbox()
            messagebox.showinfo("Success", "Translation point added!")
            
            # Clear inputs
            x_var.set(point[0])
            y_var.set(point[1])
            z_var.set(point[2])
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def remove_selected_translation_point(self):
        """Remove selected translation point"""
        selection = self.trans_listbox.curselection()
        if selection:
            idx = selection[0]
            self.translation_points.pop(idx)
            self.rotations.pop(idx)
            self.update_translation_listbox()
            messagebox.showinfo("Success", "Translation point removed!")
    
    def update_translation_listbox(self):
        """Update translation listbox display"""
        self.trans_listbox.delete(0, tk.END)
        for i, point in enumerate(self.translation_points):
            label = "START" if i == 0 else ("END" if i == len(self.translation_points)-1 else f"P{i}")
            self.trans_listbox.insert(tk.END, f"{label}: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})")
    
    def add_camera_point(self, x_var, y_var, z_var, pitch_var, yaw_var):
        """Add a camera animation point"""
        try:
            point = [x_var.get(), y_var.get(), z_var.get()]
            rotation = {"x": pitch_var.get(), "y": yaw_var.get()}
            
            self.camera_translation_points.append(point)
            self.camera_rotations.append(rotation)
            
            self.update_camera_anim_listbox()
            messagebox.showinfo("Success", "Camera point added!")
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def remove_selected_camera_point(self):
        """Remove selected camera point"""
        selection = self.camera_anim_listbox.curselection()
        if selection:
            idx = selection[0]
            self.camera_translation_points.pop(idx)
            self.camera_rotations.pop(idx)
            self.update_camera_anim_listbox()
            messagebox.showinfo("Success", "Camera point removed!")
    
    def update_camera_anim_listbox(self):
        """Update camera animation listbox display"""
        self.camera_anim_listbox.delete(0, tk.END)
        for i, point in enumerate(self.camera_translation_points):
            label = "CAM_START" if i == 0 else ("CAM_END" if i == len(self.camera_translation_points)-1 else f"CAM_P{i}")
            rot = self.camera_rotations[i] if i < len(self.camera_rotations) else {"x": 0.0, "y": 0.0}
            self.camera_anim_listbox.insert(tk.END, 
                f"{label}: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f}) P={rot['x']:.0f}° Y={rot['y']:.0f}°")
    
    def save_camera_settings(self, x_var, y_var, z_var, pitch_var, yaw_var):
        """Save camera settings"""
        try:
            self.camera_position = [x_var.get(), y_var.get(), z_var.get()]
            self.camera_rotation = {"x": pitch_var.get(), "y": yaw_var.get()}
            messagebox.showinfo("Success", "Camera settings saved!")
            self.status_text.config(text="Status: Camera settings saved")
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def save_object_settings(self):
        """Save object settings"""
        try:
            self.total_frames = self.frame_var.get()
            messagebox.showinfo("Success", "Object settings saved!")
            self.status_text.config(text="Status: Object settings saved")
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers")
    
    def load_existing_config(self):
        """Load existing configuration"""
        try:
            self.config.load()
            
            # Load camera settings
            cam_settings = self.config.get_camera_settings()
            self.camera_position = cam_settings["translation"]["position"]
            self.camera_rotation = {
                "x": cam_settings["rotation"]["pitch"],
                "y": cam_settings["rotation"]["yaw"]
            }
            
            # Load camera animation points
            self.camera_translation_points = []
            self.camera_rotations = []
            for point in cam_settings.get("animation_points", []):
                self.camera_translation_points.append(point["translation"]["position"])
                self.camera_rotations.append({
                    "x": point["rotation"]["pitch"],
                    "y": point["rotation"]["yaw"]
                })
            
            # Load object settings
            obj_points = self.config.get_animation_points()
            self.translation_points = []
            self.rotations = []
            for point in obj_points:
                self.translation_points.append(point["translation"]["position"])
                self.rotations.append({
                    "x": point["rotation"]["pitch"],
                    "y": point["rotation"]["yaw"]
                })
            
            # Load render settings
            render_settings = self.config.get_render_settings()
            self.total_frames = render_settings["total_frames"]
            
            messagebox.showinfo("Success", "Configuration loaded successfully!")
            self.status_text.config(text="Status: Configuration loaded")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
    
    def apply_config(self):
        """Apply configuration and prepare for rendering"""
        try:
            # Validate data
            if len(self.translation_points) == 0:
                messagebox.showwarning("Warning", "No translation points added for object. Using default.")
                self.translation_points = [[0.0, 0.0, 0.0]]
                self.rotations = [{"x": 0.0, "y": 0.0}]
            
            # Save to config
            self.config.clear_object_animation_points()
            self.config.clear_camera_animation_points()
            
            for i, point in enumerate(self.translation_points):
                rot = self.rotations[i] if i < len(self.rotations) else {"x": 0.0, "y": 0.0}
                self.config.add_animation_point(point, rot["x"], rot["y"])
            
            for i, point in enumerate(self.camera_translation_points):
                rot = self.camera_rotations[i] if i < len(self.camera_rotations) else {"x": 0.0, "y": 0.0}
                self.config.add_camera_animation_point(point, rot["x"], rot["y"])
            
            # Set camera position/rotation if no animation points
            if len(self.camera_translation_points) == 0:
                self.config.set_camera_settings(self.camera_position, 
                                                self.camera_rotation["x"], 
                                                self.camera_rotation["y"])
            
            self.config.set_render_settings(self.total_frames)
            self.config.save()
            
            self.result = self.config
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply configuration: {str(e)}")
    
    def cancel(self):
        """Cancel configuration"""
        if messagebox.askyesno("Cancel", "Are you sure you want to cancel?"):
            self.result = None
            self.window.destroy()
    
    def clear_right_frame(self):
        """Clear the right frame"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()
    
    def run(self) -> Optional[ConfigManager]:
        """Run the GUI and return configuration"""
        self.window.mainloop()
        return self.result

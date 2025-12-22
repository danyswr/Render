#ini file gui_input.py
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QScrollArea, QFrame, QListWidget, 
                            QListWidgetItem, QGridLayout, QMessageBox, QFileDialog, QLineEdit,
                            QDoubleSpinBox, QSpinBox, QGroupBox, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QDoubleValidator
from typing import Optional
from config_manager import ConfigManager
from visualizer import Visualizer

class GUIInput:
    """GUI untuk input konfigurasi - layout yang lebih baik dan lega"""
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.window.setWindowTitle("Rocket 3D Renderer - Configuration")
        self.window.setGeometry(100, 100, 1400, 850)
        self.window.setMinimumSize(1000, 700)
        
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
        self.selected_point_idx = None
        
        # Show matplotlib awal
        self.visualizer.show_camera_setup_realtime([0, 0, 0], {"x": 0, "y": 0})
        plt.show(block=False)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup main UI"""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Header frame dengan button selector
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("ROCKET 3D RENDERER - Configuration")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Matplotlib 3D & 2D ditampilkan di samping - Input di sini")
        subtitle.setFont(QFont("Arial", 10))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        # Tab selector buttons
        selector_frame = QFrame()
        selector_layout = QHBoxLayout(selector_frame)
        selector_layout.setContentsMargins(0, 10, 0, 0)
        
        self.camera_btn = QPushButton("Camera Setup")
        self.camera_btn.clicked.connect(lambda: self.show_tab("camera"))
        selector_layout.addWidget(self.camera_btn)
        
        self.object_btn = QPushButton("Object Setup")
        self.object_btn.clicked.connect(lambda: self.show_tab("object"))
        selector_layout.addWidget(self.object_btn)
        
        self.load_btn = QPushButton("Load Config")
        self.load_btn.clicked.connect(lambda: self.show_tab("load"))
        selector_layout.addWidget(self.load_btn)
        
        header_layout.addWidget(selector_frame)
        main_layout.addWidget(header_frame)
        
        # Main content area
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.addWidget(self.content_frame, 1)
        
        # Bottom buttons
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(20, 5, 20, 5)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel)
        btn_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton("Apply (Save & Update View)")
        self.apply_btn.clicked.connect(self.apply_config)
        btn_layout.addWidget(self.apply_btn)
        
        self.render_btn = QPushButton("Render Now")
        self.render_btn.clicked.connect(self.render_config)
        btn_layout.addWidget(self.render_btn)
        
        main_layout.addWidget(btn_frame)
        
        # Status
        self.status = QLabel("Status: Ready")
        self.status.setFont(QFont("Arial", 9))
        self.status.setStyleSheet("color: blue;")
        self.status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.status.setContentsMargins(20, 5, 20, 5)
        main_layout.addWidget(self.status)
        
        self.window.setCentralWidget(central_widget)
        self.window.show()
        
        # Show first tab
        self.show_tab("camera")
        
    def clear_content(self):
        """Bersihkan content frame"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def show_tab(self, tab_name):
        """Tampilkan tab yang dipilih"""
        self.current_tab = tab_name
        self.selected_point_idx = None
        self.clear_content()
        
        if tab_name == "camera":
            self.setup_camera_tab()
            self.camera_btn.setStyleSheet("background-color: #a0c8f0;")
            self.object_btn.setStyleSheet("")
            self.load_btn.setStyleSheet("")
        elif tab_name == "object":
            self.setup_object_tab()
            self.camera_btn.setStyleSheet("")
            self.object_btn.setStyleSheet("background-color: #a0c8f0;")
            self.load_btn.setStyleSheet("")
        elif tab_name == "load":
            self.setup_load_tab()
            self.camera_btn.setStyleSheet("")
            self.object_btn.setStyleSheet("")
            self.load_btn.setStyleSheet("background-color: #a0c8f0;")
            
    def setup_camera_tab(self):
        """Tab untuk camera setup"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(15, 10, 15, 10)
        scroll_layout.setSpacing(15)
        
        # ===== POSISI =====
        pos_group = QGroupBox("CAMERA POSITION")
        pos_layout = QVBoxLayout(pos_group)
        pos_layout.setContentsMargins(10, 15, 10, 15)
        
        input_row = QFrame()
        input_layout = QHBoxLayout(input_row)
        
        # X coordinate
        x_frame = QFrame()
        x_layout = QHBoxLayout(x_frame)
        x_layout.addWidget(QLabel("X:"))
        self.cam_x = QDoubleSpinBox()
        self.cam_x.setRange(-1000, 1000)
        self.cam_x.setValue(0.0)
        self.cam_x.setSingleStep(1.0)
        self.cam_x.setDecimals(1)
        self.cam_x.setFixedWidth(100)
        x_layout.addWidget(self.cam_x)
        input_layout.addWidget(x_frame)
        
        # Y coordinate
        y_frame = QFrame()
        y_layout = QHBoxLayout(y_frame)
        y_layout.addWidget(QLabel("Y:"))
        self.cam_y = QDoubleSpinBox()
        self.cam_y.setRange(-1000, 1000)
        self.cam_y.setValue(0.0)
        self.cam_y.setSingleStep(1.0)
        self.cam_y.setDecimals(1)
        self.cam_y.setFixedWidth(100)
        y_layout.addWidget(self.cam_y)
        input_layout.addWidget(y_frame)
        
        # Z coordinate
        z_frame = QFrame()
        z_layout = QHBoxLayout(z_frame)
        z_layout.addWidget(QLabel("Z:"))
        self.cam_z = QDoubleSpinBox()
        self.cam_z.setRange(-1000, 1000)
        self.cam_z.setValue(-150.0)
        self.cam_z.setSingleStep(1.0)
        self.cam_z.setDecimals(1)
        self.cam_z.setFixedWidth(100)
        z_layout.addWidget(self.cam_z)
        input_layout.addWidget(z_frame)
        
        save_btn = QPushButton("Save Position")
        save_btn.clicked.connect(self.save_camera)
        input_layout.addWidget(save_btn)
        
        pos_layout.addWidget(input_row)
        scroll_layout.addWidget(pos_group)
        
        # ===== ROTASI =====
        rot_group = QGroupBox("CAMERA ROTATION")
        rot_layout = QVBoxLayout(rot_group)
        rot_layout.setContentsMargins(10, 15, 10, 15)
        
        rot_row = QFrame()
        rot_layout_inner = QHBoxLayout(rot_row)
        
        # Pitch (X)
        pitch_frame = QFrame()
        pitch_layout = QHBoxLayout(pitch_frame)
        pitch_layout.addWidget(QLabel("Pitch (X):"))
        self.cam_pitch = QDoubleSpinBox()
        self.cam_pitch.setRange(-180, 180)
        self.cam_pitch.setValue(0.0)
        self.cam_pitch.setSingleStep(1.0)
        self.cam_pitch.setDecimals(1)
        self.cam_pitch.setFixedWidth(100)
        pitch_layout.addWidget(self.cam_pitch)
        rot_layout_inner.addWidget(pitch_frame)
        
        # Yaw (Y)
        yaw_frame = QFrame()
        yaw_layout = QHBoxLayout(yaw_frame)
        yaw_layout.addWidget(QLabel("Yaw (Y):"))
        self.cam_yaw = QDoubleSpinBox()
        self.cam_yaw.setRange(-180, 180)
        self.cam_yaw.setValue(0.0)
        self.cam_yaw.setSingleStep(1.0)
        self.cam_yaw.setDecimals(1)
        self.cam_yaw.setFixedWidth(100)
        yaw_layout.addWidget(self.cam_yaw)
        rot_layout_inner.addWidget(yaw_frame)
        
        update_btn = QPushButton("Update View")
        update_btn.clicked.connect(self.update_vis)
        rot_layout_inner.addWidget(update_btn)
        
        rot_layout.addWidget(rot_row)
        scroll_layout.addWidget(rot_group)
        
        # ===== ANIMATION POINTS =====
        anim_group = QGroupBox("CAMERA ANIMATION POINTS")
        anim_layout = QVBoxLayout(anim_group)
        anim_layout.setContentsMargins(10, 15, 10, 15)
        
        self.cam_listbox = QListWidget()
        self.cam_listbox.itemClicked.connect(self.on_camera_point_click)
        anim_layout.addWidget(self.cam_listbox, 1)
        
        # Buttons row
        btn_row = QFrame()
        btn_layout = QHBoxLayout(btn_row)
        
        add_btn = QPushButton("Add Point from Current")
        add_btn.clicked.connect(self.add_camera_point)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit Selected Rotation")
        edit_btn.clicked.connect(self.edit_camera_rotation)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_camera_point)
        btn_layout.addWidget(remove_btn)
        
        anim_layout.addWidget(btn_row)
        scroll_layout.addWidget(anim_group, 1)
        
        scroll_area.setWidget(scroll_content)
        self.content_layout.addWidget(scroll_area)
        
        self.update_cam_listbox()
        
    def setup_object_tab(self):
        """Tab untuk object setup"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(15, 10, 15, 10)
        scroll_layout.setSpacing(15)
        
        # ===== INPUT SECTION =====
        input_group = QGroupBox("ADD OBJECT POINT (Translation + Rotation)")
        input_layout = QVBoxLayout(input_group)
        input_layout.setContentsMargins(10, 15, 10, 15)
        
        # Row 1: XYZ coordinates
        row1 = QFrame()
        row1_layout = QHBoxLayout(row1)
        
        # X coordinate
        x_frame = QFrame()
        x_layout = QHBoxLayout(x_frame)
        x_layout.addWidget(QLabel("X:"))
        self.trans_x = QDoubleSpinBox()
        self.trans_x.setRange(-1000, 1000)
        self.trans_x.setValue(0.0)
        self.trans_x.setSingleStep(1.0)
        self.trans_x.setDecimals(1)
        self.trans_x.setFixedWidth(90)
        x_layout.addWidget(self.trans_x)
        row1_layout.addWidget(x_frame)
        
        # Y coordinate
        y_frame = QFrame()
        y_layout = QHBoxLayout(y_frame)
        y_layout.addWidget(QLabel("Y:"))
        self.trans_y = QDoubleSpinBox()
        self.trans_y.setRange(-1000, 1000)
        self.trans_y.setValue(0.0)
        self.trans_y.setSingleStep(1.0)
        self.trans_y.setDecimals(1)
        self.trans_y.setFixedWidth(90)
        y_layout.addWidget(self.trans_y)
        row1_layout.addWidget(y_frame)
        
        # Z coordinate
        z_frame = QFrame()
        z_layout = QHBoxLayout(z_frame)
        z_layout.addWidget(QLabel("Z:"))
        self.trans_z = QDoubleSpinBox()
        self.trans_z.setRange(-1000, 1000)
        self.trans_z.setValue(0.0)
        self.trans_z.setSingleStep(1.0)
        self.trans_z.setDecimals(1)
        self.trans_z.setFixedWidth(90)
        z_layout.addWidget(self.trans_z)
        row1_layout.addWidget(z_frame)
        
        input_layout.addWidget(row1)
        
        # Row 2: Rotation
        row2 = QFrame()
        row2_layout = QHBoxLayout(row2)
        
        # Pitch
        pitch_frame = QFrame()
        pitch_layout = QHBoxLayout(pitch_frame)
        pitch_layout.addWidget(QLabel("Pitch:"))
        self.rot_pitch = QDoubleSpinBox()
        self.rot_pitch.setRange(-180, 180)
        self.rot_pitch.setValue(0.0)
        self.rot_pitch.setSingleStep(1.0)
        self.rot_pitch.setDecimals(1)
        self.rot_pitch.setFixedWidth(90)
        pitch_layout.addWidget(self.rot_pitch)
        row2_layout.addWidget(pitch_frame)
        
        # Yaw
        yaw_frame = QFrame()
        yaw_layout = QHBoxLayout(yaw_frame)
        yaw_layout.addWidget(QLabel("Yaw:"))
        self.rot_yaw = QDoubleSpinBox()
        self.rot_yaw.setRange(-180, 180)
        self.rot_yaw.setValue(0.0)
        self.rot_yaw.setSingleStep(1.0)
        self.rot_yaw.setDecimals(1)
        self.rot_yaw.setFixedWidth(90)
        yaw_layout.addWidget(self.rot_yaw)
        row2_layout.addWidget(yaw_frame)
        
        add_btn = QPushButton("Add Point")
        add_btn.clicked.connect(self.add_translation_point)
        row2_layout.addWidget(add_btn)
        
        input_layout.addWidget(row2)
        scroll_layout.addWidget(input_group)
        
        # ===== TRANSLATION POINTS LIST =====
        trans_group = QGroupBox("OBJECT POINTS (Click to Edit Rotation)")
        trans_layout = QVBoxLayout(trans_group)
        trans_layout.setContentsMargins(10, 15, 10, 15)
        
        self.trans_listbox = QListWidget()
        self.trans_listbox.itemClicked.connect(self.on_object_point_click)
        trans_layout.addWidget(self.trans_listbox, 1)
        
        # Buttons row
        btn_row = QFrame()
        btn_layout = QHBoxLayout(btn_row)
        
        edit_btn = QPushButton("Edit Selected Rotation")
        edit_btn.clicked.connect(self.edit_object_rotation)
        btn_layout.addWidget(edit_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_translation_point)
        btn_layout.addWidget(remove_btn)
        
        trans_layout.addWidget(btn_row)
        scroll_layout.addWidget(trans_group, 1)
        
        # ===== RENDER SETTINGS =====
        frame_group = QGroupBox("RENDER SETTINGS")
        frame_layout = QVBoxLayout(frame_group)
        frame_layout.setContentsMargins(10, 15, 10, 15)
        
        frame_row = QFrame()
        frame_row_layout = QHBoxLayout(frame_row)
        
        frame_row_layout.addWidget(QLabel("Total Frames:"))
        
        self.frame_var = QSpinBox()
        self.frame_var.setRange(1, 100)
        self.frame_var.setValue(1)
        self.frame_var.setFixedWidth(100)
        frame_row_layout.addWidget(self.frame_var)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_object)
        frame_row_layout.addWidget(save_btn)
        
        frame_row_layout.addStretch()
        frame_layout.addWidget(frame_row)
        scroll_layout.addWidget(frame_group)
        
        scroll_area.setWidget(scroll_content)
        self.content_layout.addWidget(scroll_area)
        
        self.update_trans_listbox()
        
    def setup_load_tab(self):
        """Tab untuk load config"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        info = QLabel("Load existing configuration dari file")
        info.setFont(QFont("Arial", 12))
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        load_btn = QPushButton("Load Configuration")
        load_btn.setFixedSize(200, 40)
        load_btn.clicked.connect(self.load_config)
        layout.addWidget(load_btn)
        
        self.load_status = QLabel("")
        self.load_status.setFont(QFont("Arial", 10))
        self.load_status.setStyleSheet("color: green;")
        self.load_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.load_status)
        
        layout.addStretch()
        self.content_layout.addWidget(frame)
        
    def on_camera_point_click(self, item):
        """Handle camera point selection"""
        self.selected_point_idx = self.cam_listbox.row(item)
        
    def on_object_point_click(self, item):
        """Handle object point selection"""
        self.selected_point_idx = self.trans_listbox.row(item)
        
    def edit_camera_rotation(self):
        """Edit selected camera point rotation"""
        if self.selected_point_idx is None:
            QMessageBox.warning(self.window, "Warning", "Pilih point dulu!")
            return
        if self.selected_point_idx >= len(self.camera_rotations):
            QMessageBox.critical(self.window, "Error", "Invalid point index")
            return
            
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Edit Camera Rotation")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Pitch input
        pitch_layout = QHBoxLayout()
        pitch_layout.addWidget(QLabel("Pitch (X):"))
        pitch_var = QDoubleSpinBox()
        pitch_var.setRange(-180, 180)
        pitch_var.setValue(self.camera_rotations[self.selected_point_idx]["x"])
        pitch_var.setSingleStep(1.0)
        pitch_var.setDecimals(1)
        pitch_layout.addWidget(pitch_var)
        layout.addLayout(pitch_layout)
        
        # Yaw input
        yaw_layout = QHBoxLayout()
        yaw_layout.addWidget(QLabel("Yaw (Y):"))
        yaw_var = QDoubleSpinBox()
        yaw_var.setRange(-180, 180)
        yaw_var.setValue(self.camera_rotations[self.selected_point_idx]["y"])
        yaw_var.setSingleStep(1.0)
        yaw_var.setDecimals(1)
        yaw_layout.addWidget(yaw_var)
        layout.addLayout(yaw_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.camera_rotations[self.selected_point_idx]["x"] = pitch_var.value()
            self.camera_rotations[self.selected_point_idx]["y"] = yaw_var.value()
            self.update_cam_listbox()
            self.status.setText("Status: Camera rotation updated")
            
    def edit_object_rotation(self):
        """Edit selected object point rotation"""
        if self.selected_point_idx is None:
            QMessageBox.warning(self.window, "Warning", "Pilih point dulu!")
            return
        if self.selected_point_idx >= len(self.rotations):
            QMessageBox.critical(self.window, "Error", "Invalid point index")
            return
            
        dialog = QDialog(self.window)
        dialog.setWindowTitle("Edit Object Rotation")
        dialog.setFixedSize(400, 200)
        
        layout = QVBoxLayout(dialog)
        
        # Pitch input
        pitch_layout = QHBoxLayout()
        pitch_layout.addWidget(QLabel("Pitch (X):"))
        pitch_var = QDoubleSpinBox()
        pitch_var.setRange(-180, 180)
        pitch_var.setValue(self.rotations[self.selected_point_idx]["x"])
        pitch_var.setSingleStep(1.0)
        pitch_var.setDecimals(1)
        pitch_layout.addWidget(pitch_var)
        layout.addLayout(pitch_layout)
        
        # Yaw input
        yaw_layout = QHBoxLayout()
        yaw_layout.addWidget(QLabel("Yaw (Y):"))
        yaw_var = QDoubleSpinBox()
        yaw_var.setRange(-180, 180)
        yaw_var.setValue(self.rotations[self.selected_point_idx]["y"])
        yaw_var.setSingleStep(1.0)
        yaw_var.setDecimals(1)
        yaw_layout.addWidget(yaw_var)
        layout.addLayout(yaw_layout)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.rotations[self.selected_point_idx]["x"] = pitch_var.value()
            self.rotations[self.selected_point_idx]["y"] = yaw_var.value()
            self.update_trans_listbox()
            self.status.setText("Status: Object rotation updated")
            
    def update_vis(self):
        """Update matplotlib visualization"""
        try:
            self.camera_position = [self.cam_x.value(), self.cam_y.value(), self.cam_z.value()]
            self.camera_rotation = {"x": self.cam_pitch.value(), "y": self.cam_yaw.value()}
            
            # Update visualizer
            self.visualizer.set_camera_position(self.camera_position[0], self.camera_position[1], self.camera_position[2])
            self.visualizer.set_camera_rotation(self.camera_rotation["x"], self.camera_rotation["y"])
            
            # Update view
            self.visualizer.show_camera_setup_realtime([0, 0, 0], self.camera_rotation)
            plt.draw()
            
            self.status.setText("Status: Visualization updated")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Update failed: {e}")
            
    def add_camera_point(self):
        """Tambah camera animation point"""
        try:
            point = [self.cam_x.value(), self.cam_y.value(), self.cam_z.value()]
            rotation = {"x": self.cam_pitch.value(), "y": self.cam_yaw.value()}
            self.camera_translation_points.append(point)
            self.camera_rotations.append(rotation)
            self.update_cam_listbox()
            self.status.setText("Status: Camera point added")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Invalid input: {e}")
            
    def remove_camera_point(self):
        """Hapus camera point"""
        if self.selected_point_idx is not None and 0 <= self.selected_point_idx < self.cam_listbox.count():
            self.camera_translation_points.pop(self.selected_point_idx)
            self.camera_rotations.pop(self.selected_point_idx)
            self.update_cam_listbox()
            self.status.setText("Status: Camera point removed")
            self.selected_point_idx = None
            
    def update_cam_listbox(self):
        """Update camera listbox"""
        self.cam_listbox.clear()
        for i, p in enumerate(self.camera_translation_points):
            label = "CAM_START" if i == 0 else ("CAM_END" if i == len(self.camera_translation_points)-1 else f"P{i}")
            rot = self.camera_rotations[i] if i < len(self.camera_rotations) else {"x": 0, "y": 0}
            item_text = f"{label}: ({p[0]:.0f},{p[1]:.0f},{p[2]:.0f}) Pitch={rot['x']:.0f}° Yaw={rot['y']:.0f}°"
            item = QListWidgetItem(item_text)
            self.cam_listbox.addItem(item)
            
    def add_translation_point(self):
        """Tambah translation point"""
        try:
            point = [self.trans_x.value(), self.trans_y.value(), self.trans_z.value()]
            rotation = {"x": self.rot_pitch.value(), "y": self.rot_yaw.value()}
            self.translation_points.append(point)
            self.rotations.append(rotation)
            self.update_trans_listbox()
            self.status.setText("Status: Object point added")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Invalid input: {e}")
            
    def remove_translation_point(self):
        """Hapus translation point"""
        if self.selected_point_idx is not None and 0 <= self.selected_point_idx < self.trans_listbox.count():
            self.translation_points.pop(self.selected_point_idx)
            self.rotations.pop(self.selected_point_idx)
            self.update_trans_listbox()
            self.status.setText("Status: Object point removed")
            self.selected_point_idx = None
            
    def update_trans_listbox(self):
        """Update translation listbox"""
        self.trans_listbox.clear()
        for i, p in enumerate(self.translation_points):
            label = "START" if i == 0 else ("END" if i == len(self.translation_points)-1 else f"P{i}")
            rot = self.rotations[i] if i < len(self.rotations) else {"x": 0, "y": 0}
            item_text = f"{label}: ({p[0]:.0f},{p[1]:.0f},{p[2]:.0f}) Pitch={rot['x']:.0f}° Yaw={rot['y']:.0f}°"
            item = QListWidgetItem(item_text)
            self.trans_listbox.addItem(item)
            
    def save_camera(self):
        """Save camera settings"""
        try:
            self.camera_position = [self.cam_x.value(), self.cam_y.value(), self.cam_z.value()]
            self.camera_rotation = {"x": self.cam_pitch.value(), "y": self.cam_yaw.value()}
            self.status.setText("Status: Camera position saved")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Invalid input: {e}")
            
    def save_object(self):
        """Save object settings"""
        try:
            self.total_frames = self.frame_var.value()
            self.status.setText("Status: Object settings saved")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Invalid input: {e}")
            
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
            
            # Reset camera animation points
            self.camera_translation_points = []
            self.camera_rotations = []
            for point in cam_settings.get("animation_points", []):
                self.camera_translation_points.append(point["translation"]["position"])
                self.camera_rotations.append({
                    "x": point["rotation"]["pitch"],
                    "y": point["rotation"]["yaw"]
                })
            
            # Reset object animation points
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
            
            # Update UI
            self.cam_x.setValue(self.camera_position[0])
            self.cam_y.setValue(self.camera_position[1])
            self.cam_z.setValue(self.camera_position[2])
            self.cam_pitch.setValue(self.camera_rotation["x"])
            self.cam_yaw.setValue(self.camera_rotation["y"])
            self.frame_var.setValue(self.total_frames)
            
            self.update_cam_listbox()
            self.update_trans_listbox()
            
            self.load_status.setText("✓ Configuration loaded successfully!")
            self.load_status.setStyleSheet("color: green;")
            self.status.setText("Status: Configuration loaded")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Failed to load: {e}")
            self.load_status.setText("✗ Load failed")
            self.load_status.setStyleSheet("color: red;")
            
    def save_to_config(self):
        """Save current settings to config object"""
        if len(self.translation_points) == 0:
            self.translation_points = [[0.0, 0.0, 0.0]]
            self.rotations = [{"x": 0.0, "y": 0.0}]
            
        self.config.clear_object_animation_points()
        self.config.clear_camera_animation_points()
        
        # Save object animation points
        for i, point in enumerate(self.translation_points):
            rot = self.rotations[i] if i < len(self.rotations) else {"x": 0.0, "y": 0.0}
            self.config.add_animation_point(point, rot["x"], rot["y"])
            
        # Save camera animation points
        for i, point in enumerate(self.camera_translation_points):
            rot = self.camera_rotations[i] if i < len(self.camera_rotations) else {"x": 0.0, "y": 0.0}
            self.config.add_camera_animation_point(point, rot["x"], rot["y"])
            
        # If no camera animation points, save current camera position and rotation
        if len(self.camera_translation_points) == 0:
            self.config.set_camera_settings(self.camera_position, 
                                           self.camera_rotation["x"], 
                                           self.camera_rotation["y"])
                                           
        # Save render settings
        self.config.set_render_settings(self.total_frames)
        
    def apply_config(self):
        """Apply config - save to JSON and update visualization"""
        try:
            self.save_to_config()
            self.config.save()
            self.status.setText("Status: Configuration saved to JSON and view updated!")
            
            # Update visualization with current settings
            if len(self.translation_points) > 0:
                self.visualizer.show_translation_with_rocket(
                    self.translation_points,
                    None,
                    self.rotations
                )
            elif len(self.camera_translation_points) > 0:
                self.visualizer.show_camera_translation_path(
                    self.camera_translation_points,
                    None,
                    self.camera_rotations
                )
            else:
                self.update_vis()
                
            plt.draw()
            QMessageBox.information(self.window, "Success", "Configuration saved!\nClick 'Render Now' when ready to render.")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Failed to save: {e}")
            
    def render_config(self):
        """Render config - save and close window to start rendering"""
        try:
            self.save_to_config()
            self.config.save()
            self.result = self.config
            self.window.close()
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Failed: {e}")
            
    def cancel(self):
        """Cancel"""
        reply = QMessageBox.question(self.window, "Cancel", "Batalkan konfigurasi?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.result = None
            self.window.close()
            
    def run(self) -> Optional[ConfigManager]:
        """Run GUI"""
        sys.exit(self.app.exec())
        return self.result
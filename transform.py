"""
Transform - Kelas untuk transformasi 3D (Rotation + Translation + Scale)
"""
import numpy as np


class Transform:
    """Class untuk menangani transformasi 3D"""
    
    def __init__(self):
        # Rotation dalam radian (yaw, pitch, roll)
        self.yaw = 0.0      # Rotasi Y-axis
        self.pitch = 0.0    # Rotasi X-axis
        self.roll = 0.0     # Rotasi Z-axis
        
        # Translation
        self.tx = 0.0
        self.ty = 0.0
        self.tz = 0.0
        
        self.scale = 1.0
    
    def set_rotation_degrees(self, yaw=0, pitch=0, roll=0):
        """Set rotasi dalam derajat"""
        self.yaw = np.radians(yaw)
        self.pitch = np.radians(pitch)
        self.roll = np.radians(roll)
    
    def set_translation(self, tx=0, ty=0, tz=0):
        """Set translasi"""
        self.tx = tx
        self.ty = ty
        self.tz = tz
    
    def set_scale(self, scale=1.0):
        """Set scale factor"""
        self.scale = scale if scale > 0 else 1.0
    
    def apply_rotation(self, x, y, z):
        """
        Apply rotasi YXZ (Yaw → Pitch → Roll) pada koordinat
        Returns: (x_rot, y_rot, z_rot)
        """
        # Yaw (Y-axis rotation)
        cos_yaw, sin_yaw = np.cos(self.yaw), np.sin(self.yaw)
        x1 = cos_yaw * x + sin_yaw * z
        y1 = y
        z1 = -sin_yaw * x + cos_yaw * z
        
        # Pitch (X-axis rotation)
        cos_pitch, sin_pitch = np.cos(self.pitch), np.sin(self.pitch)
        x2 = x1
        y2 = cos_pitch * y1 - sin_pitch * z1
        z2 = sin_pitch * y1 + cos_pitch * z1
        
        # Roll (Z-axis rotation)
        cos_roll, sin_roll = np.cos(self.roll), np.sin(self.roll)
        x3 = cos_roll * x2 - sin_roll * y2
        y3 = sin_roll * x2 + cos_roll * y2
        z3 = z2
        
        return x3, y3, z3
    
    def apply_translation(self, x, y, z):
        """Apply translasi pada koordinat"""
        return x + self.tx, y + self.ty, z + self.tz
    
    def transform_point(self, x, y, z, centroid_x, centroid_y, centroid_z):
        """
        Transform point: Scale → Rotation around centroid → Translation
        Returns: (world_x, world_y, world_z)
        """
        # 1. Relative to centroid
        x_local = x - centroid_x
        y_local = y - centroid_y
        z_local = z - centroid_z
        
        # 2. Apply scale
        x_scaled = x_local * self.scale
        y_scaled = y_local * self.scale
        z_scaled = z_local * self.scale
        
        # 3. Apply rotation
        x_rot, y_rot, z_rot = self.apply_rotation(x_scaled, y_scaled, z_scaled)
        
        # 4. Back to world space + translation
        world_x = centroid_x + x_rot + self.tx
        world_y = centroid_y + y_rot + self.ty
        world_z = centroid_z + z_rot + self.tz
        
        return world_x, world_y, world_z

"""
Camera - Kelas untuk kamera 3D dengan dukungan rotasi
"""
import numpy as np


class Camera:
    """Class untuk menangani kamera 3D dengan rotasi"""
    
    def __init__(self, position, target, rotation=None):
        """
        Initialize camera
        position: (x, y, z) posisi kamera
        target: (x, y, z) target yang dilihat
        rotation: dict dengan 'x', 'y', 'z' dalam derajat (opsional)
        """
        self.position = np.array(position, dtype=float)
        self.target = np.array(target, dtype=float)
        self.rotation = rotation if rotation else {"x": 0.0, "y": 0.0, "z": 0.0}
        
        self._calculate_basis()
    
    def _rotation_matrix(self, rx, ry, rz):
        """Create rotation matrix from Euler angles (degrees)"""
        rx_rad = np.radians(rx)
        ry_rad = np.radians(ry)
        rz_rad = np.radians(rz)
        
        Rx = np.array([[1, 0, 0],
                      [0, np.cos(rx_rad), -np.sin(rx_rad)],
                      [0, np.sin(rx_rad), np.cos(rx_rad)]])
        
        Ry = np.array([[np.cos(ry_rad), 0, np.sin(ry_rad)],
                      [0, 1, 0],
                      [-np.sin(ry_rad), 0, np.cos(ry_rad)]])
        
        Rz = np.array([[np.cos(rz_rad), -np.sin(rz_rad), 0],
                      [np.sin(rz_rad), np.cos(rz_rad), 0],
                      [0, 0, 1]])
        
        return Rz @ Ry @ Rx
    
    def _calculate_basis(self):
        """Menghitung basis vectors kamera (forward, right, up) dengan rotasi"""
        forward = self.target - self.position
        forward_len = np.linalg.norm(forward)
        if forward_len > 0:
            forward = forward / forward_len
        else:
            forward = np.array([0, 0, 1])
        
        world_up = np.array([0, 1, 0])
        right = np.cross(forward, world_up)
        right_len = np.linalg.norm(right)
        if right_len > 0:
            right = right / right_len
        else:
            right = np.array([1, 0, 0])
        
        up = np.cross(right, forward)
        
        rot_x = self.rotation.get('x', 0.0)
        rot_y = self.rotation.get('y', 0.0)
        rot_z = self.rotation.get('z', 0.0)
        
        if rot_x != 0 or rot_y != 0 or rot_z != 0:
            R = self._rotation_matrix(rot_x, rot_y, rot_z)
            forward = R @ forward
            right = R @ right
            up = R @ up
        
        self.forward = forward
        self.right = right
        self.up = up
    
    def set_rotation(self, rot_x: float, rot_y: float, rot_z: float):
        """Set camera rotation in degrees and recalculate basis"""
        self.rotation = {"x": rot_x, "y": rot_y, "z": rot_z}
        self._calculate_basis()
    
    def world_to_camera(self, world_x, world_y, world_z):
        """
        Transform dari world space ke camera space
        Returns: (cam_x, cam_y, cam_z)
        """
        dx = world_x - self.position[0]
        dy = world_y - self.position[1]
        dz = world_z - self.position[2]
        
        cam_x = dx * self.right[0] + dy * self.right[1] + dz * self.right[2]
        cam_y = dx * self.up[0] + dy * self.up[1] + dz * self.up[2]
        cam_z = dx * self.forward[0] + dy * self.forward[1] + dz * self.forward[2]
        
        return cam_x, cam_y, cam_z

"""
Camera - Kelas untuk kamera 3D
"""
import numpy as np


class Camera:
    """Class untuk menangani kamera 3D"""
    
    def __init__(self, position, target):
        """
        Initialize camera
        position: (x, y, z) posisi kamera
        target: (x, y, z) target yang dilihat
        """
        self.position = np.array(position, dtype=float)
        self.target = np.array(target, dtype=float)
        
        # Calculate camera basis vectors
        self._calculate_basis()
    
    def _calculate_basis(self):
        """Menghitung basis vectors kamera (forward, right, up)"""
        # Forward vector (dari kamera ke target)
        self.forward = self.target - self.position
        self.forward /= np.linalg.norm(self.forward)
        
        # Right vector
        world_up = np.array([0, 1, 0])
        self.right = np.cross(self.forward, world_up)
        self.right /= np.linalg.norm(self.right)
        
        # Up vector
        self.up = np.cross(self.right, self.forward)
    
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

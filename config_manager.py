import json
import os
from typing import List, Dict, Any

class ConfigManager:
    """Manages configuration for rocket animation"""
    
    def __init__(self, config_file: str = "animation_config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "translation": {
                "points": [],
                "scales": [],
                "rotations": []
            },
            "rotation": {
                "loop": False
            },
            "camera": {
                "position": [50, 50, 100],
                "target": [0, 0, 0]
            },
            "render": {
                "total_frames": 1,
                "interpolate": False
            }
        }
    
    def add_translation_point(self, x: float, y: float, z: float, scale: float = 1.0, rotation: Dict[str, float] = None):
        """Add translation point with scale and rotation"""
        self.config["translation"]["points"].append([x, y, z])
        self.config["translation"]["scales"].append(scale)
        if rotation is None:
            rotation = {"x": 0.0, "y": 0.0, "z": 0.0}
        self.config["translation"]["rotations"].append(rotation)
    
    def set_rotation_loop(self, loop: bool = False):
        """Set rotation loop parameter"""
        self.config["rotation"]["loop"] = loop
    
    def set_rotation(self, x: float, y: float, z: float, loop: bool = False):
        """Set rotation parameters (legacy support)"""
        self.config["rotation"]["loop"] = loop
    
    def set_render_settings(self, total_frames: int = 1, interpolate: bool = False):
        """Set render settings"""
        self.config["render"] = {
            "total_frames": max(1, total_frames),
            "interpolate": interpolate
        }
    
    def get_render_settings(self) -> Dict[str, Any]:
        """Get render settings"""
        return self.config.get("render", {"total_frames": 1, "interpolate": False})
    
    def save(self):
        """Save configuration to file"""
        os.makedirs("result", exist_ok=True)
        config_path = os.path.join("result", self.config_file)
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"\n✓ Configuration saved to {config_path}")
    
    def load(self):
        """Load configuration from file with backward compatibility"""
        config_path = os.path.join("result", self.config_file)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            if "rotations" not in self.config.get("translation", {}):
                self.config["translation"]["rotations"] = []
            
            points = self.config.get("translation", {}).get("points", [])
            rotations = self.config["translation"]["rotations"]
            
            if len(rotations) < len(points):
                legacy_rotation = self.config.get("rotation", {})
                rot_x = legacy_rotation.get("x", 0.0)
                rot_y = legacy_rotation.get("y", 0.0)
                rot_z = legacy_rotation.get("z", 0.0)
                
                for _ in range(len(points) - len(rotations)):
                    rotations.append({"x": rot_x, "y": rot_y, "z": rot_z})
            
            scales = self.config.get("translation", {}).get("scales", [])
            if len(scales) < len(points):
                for _ in range(len(points) - len(scales)):
                    scales.append(1.0)
                self.config["translation"]["scales"] = scales
            
            if "render" not in self.config:
                self.config["render"] = {"total_frames": 1, "interpolate": False}
            
            print(f"✓ Configuration loaded from {config_path}")
        return self.config
    
    def get_translation_points(self) -> List[List[float]]:
        """Get translation points"""
        return self.config["translation"]["points"]
    
    def get_scales(self) -> List[float]:
        """Get scales for each point"""
        return self.config["translation"]["scales"]
    
    def get_rotation(self) -> Dict[str, Any]:
        """Get rotation parameters"""
        return self.config["rotation"]
    
    def get_rotations(self) -> List[Dict[str, float]]:
        """Get rotations for each point"""
        return self.config["translation"].get("rotations", [])
    
    def set_camera_settings(self, settings: Dict[str, Any]):
        """Set camera settings (position and rotation)"""
        self.config["camera"] = settings
    
    def get_camera_settings(self) -> Dict[str, Any]:
        """Get camera settings"""
        return self.config.get("camera", {
            "position": [0, 0, -150],
            "rotation": {"x": 0, "y": 0, "z": 0}
        })

#ini file config_mnanager.py
import json
import os
from typing import List, Dict, Any

class ConfigManager:
    """Manages configuration for rocket animation with detailed tracking"""
    
    def __init__(self, config_file: str = "animation_config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration with detailed structure"""
        return {
            "metadata": {
                "version": "2.0",
                "description": "Rocket 3D Animation Configuration"
            },
            "object": {
                "type": "rocket",
                "animation_points": []
            },
            "camera": {
                "translation": {
                    "position": [0.0, 0.0, -150.0],
                    "description": "Camera position in world space (X, Y, Z)"
                },
                "rotation": {
                    "pitch": 0.0,
                    "yaw": 0.0,
                    "description": "Camera rotation - Pitch (X-axis), Yaw (Y-axis) in degrees"
                }
            },
            "canvas": {
                "width": 640,
                "height": 480,
                "fov": 50,
                "description": "Render canvas dimensions and field of view"
            },
            "render": {
                "total_frames": 1,
                "description": "Number of frames to render"
            }
        }
    
    def add_animation_point(self, position: List[float], pitch: float = 0.0, yaw: float = 0.0):
        """Add animation point with object translation and rotation
        
        Args:
            position: [x, y, z] position of object
            pitch: rotation pitch in degrees
            yaw: rotation yaw in degrees
        """
        self.config["object"]["animation_points"].append({
            "translation": {
                "position": [float(x) for x in position],
                "description": "Object translation in world space (X, Y, Z)"
            },
            "rotation": {
                "pitch": float(pitch),
                "yaw": float(yaw),
                "description": "Object rotation - Pitch (X-axis), Yaw (Y-axis) in degrees"
            }
        })
    
    def set_camera_translation(self, position: List[float]):
        """Set camera translation position"""
        self.config["camera"]["translation"]["position"] = [float(x) for x in position]
    
    def set_camera_rotation(self, pitch: float, yaw: float):
        """Set camera rotation (pitch and yaw only)"""
        self.config["camera"]["rotation"]["pitch"] = float(pitch)
        self.config["camera"]["rotation"]["yaw"] = float(yaw)
    
    def set_camera_settings(self, position: List[float], pitch: float = 0.0, yaw: float = 0.0):
        """Set all camera settings at once"""
        self.set_camera_translation(position)
        self.set_camera_rotation(pitch, yaw)
    
    def set_render_settings(self, total_frames: int = 1):
        """Set render settings"""
        self.config["render"]["total_frames"] = max(1, int(total_frames))
    
    def set_canvas_settings(self, width: int = 640, height: int = 480, fov: int = 50):
        """Set canvas settings"""
        self.config["canvas"]["width"] = int(width)
        self.config["canvas"]["height"] = int(height)
        self.config["canvas"]["fov"] = int(fov)
    
    def save(self):
        """Save configuration to file"""
        os.makedirs("result", exist_ok=True)
        config_path = os.path.join("result", self.config_file)
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"\n✓ Configuration saved to {config_path}")
    
    def load(self):
        """Load configuration from file"""
        config_path = os.path.join("result", self.config_file)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                loaded = json.load(f)
                self.config = self._merge_configs(self._load_default_config(), loaded)
            print(f"✓ Configuration loaded from {config_path}")
        return self.config
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config with defaults"""
        merged = default.copy()
        for key in loaded:
            if key in merged and isinstance(merged[key], dict) and isinstance(loaded[key], dict):
                merged[key] = {**merged[key], **loaded[key]}
            else:
                merged[key] = loaded[key]
        return merged
    
    def get_animation_points(self) -> List[Dict]:
        """Get all animation points"""
        return self.config["object"]["animation_points"]
    
    def get_camera_settings(self) -> Dict[str, Any]:
        """Get camera settings"""
        return self.config["camera"]
    
    def get_canvas_settings(self) -> Dict[str, Any]:
        """Get canvas settings"""
        return self.config["canvas"]
    
    def get_render_settings(self) -> Dict[str, Any]:
        """Get render settings"""
        return self.config["render"]

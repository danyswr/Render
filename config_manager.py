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
                "scales": []
            },
            "rotation": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "loop": False
            },
            "camera": {
                "position": [50, 50, 100],
                "target": [0, 0, 0]
            }
        }
    
    def add_translation_point(self, x: float, y: float, z: float, scale: float = 1.0):
        """Add translation point with scale"""
        self.config["translation"]["points"].append([x, y, z])
        self.config["translation"]["scales"].append(scale)
    
    def set_rotation(self, x: float, y: float, z: float, loop: bool = False):
        """Set rotation parameters"""
        self.config["rotation"]["x"] = x
        self.config["rotation"]["y"] = y
        self.config["rotation"]["z"] = z
        self.config["rotation"]["loop"] = loop
    
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
                self.config = json.load(f)
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

from typing import List, Tuple
from visualizer import Visualizer
from config_manager import ConfigManager

class InteractiveInput:
    """Handles interactive user input with real-time visualization"""
    
    def __init__(self):
        self.visualizer = Visualizer()
        self.config = ConfigManager()
    
    def _get_float_input(self, prompt: str, default: float = 0.0) -> float:
        """Get float input from user with default value"""
        while True:
            try:
                user_input = input(prompt)
                if user_input.strip() == "":
                    return default
                return float(user_input)
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def _get_yes_no(self, prompt: str) -> bool:
        """Get yes/no input from user"""
        while True:
            response = input(prompt).strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
    
    def input_translation_stage(self):
        """Stage 1: Input translation path with visualization"""
        print("\n" + "="*60)
        print("STAGE 1: TRANSLATION PATH")
        print("="*60)
        print("Define the path your rocket will follow.")
        print("You can add multiple points to create complex paths (zigzag, curves, etc.)")
        print("-"*60)
        
        points = []
        
        # Input start point
        print("\nEnter START POINT:")
        x = self._get_float_input("  X coordinate (default 0): ", 0.0)
        y = self._get_float_input("  Y coordinate (default 0): ", 0.0)
        z = self._get_float_input("  Z coordinate (default 0): ", 0.0)
        points.append([x, y, z])
        
        # Visualize first point
        self.visualizer.show_translation_path(points)
        
        # Input additional points
        while True:
            add_more = self._get_yes_no("\nAdd another point? (y/n): ")
            if not add_more:
                break
            
            print("\nEnter NEXT POINT:")
            x = self._get_float_input("  X coordinate: ", points[-1][0])
            y = self._get_float_input("  Y coordinate: ", points[-1][1])
            z = self._get_float_input("  Z coordinate: ", points[-1][2])
            points.append([x, y, z])
            
            # Update visualization
            self.visualizer.show_translation_path(points)
        
        # Input end point
        print("\nEnter END POINT:")
        x = self._get_float_input("  X coordinate (default 50): ", 50.0)
        y = self._get_float_input("  Y coordinate (default 50): ", 50.0)
        z = self._get_float_input("  Z coordinate (default 50): ", 50.0)
        points.append([x, y, z])
        
        # Final visualization
        self.visualizer.show_translation_path(points)
        
        # Input scale for each point
        print("\n" + "-"*60)
        print("SCALE CONFIGURATION")
        print("-"*60)
        scales = []
        for i, point in enumerate(points):
            print(f"\nPoint {i}: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})")
            scale = self._get_float_input(f"  Scale (default 1.0): ", 1.0)
            scales.append(scale)
            
            # Visualize scale
            self.visualizer.show_scale_preview(point, scale)
        
        # Confirm
        print("\n" + "-"*60)
        print("TRANSLATION PATH SUMMARY:")
        for i, (point, scale) in enumerate(zip(points, scales)):
            print(f"  Point {i}: Position({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f}), Scale: {scale:.2f}x")
        
        if self._get_yes_no("\nConfirm translation path? (y/n): "):
            for point, scale in zip(points, scales):
                self.config.add_translation_point(point[0], point[1], point[2], scale)
            print("Translation path confirmed!")
            return True
        else:
            print("Translation path cancelled. Please restart.")
            return False
    
    def input_rotation_stage(self):
        """Stage 2: Input rotation with visualization"""
        print("\n" + "="*60)
        print("STAGE 2: ROTATION")
        print("="*60)
        print("Define how your rocket will rotate.")
        print("View the colored sphere to understand orientation:")
        print("  - RED: Front face")
        print("  - GREEN: Side faces")
        print("  - BLUE: Back face")
        print("  - YELLOW: Top")
        print("-"*60)
        
        while True:
            print("\nEnter rotation angles (in degrees):")
            rot_x = self._get_float_input("  X-axis rotation (pitch, default 0): ", 0.0)
            rot_y = self._get_float_input("  Y-axis rotation (yaw, default 0): ", 0.0)
            rot_z = self._get_float_input("  Z-axis rotation (roll, default 0): ", 0.0)
            
            # Visualize rotation
            self.visualizer.show_rotation_preview(rot_x, rot_y, rot_z)
            
            if self._get_yes_no("\nIs this rotation correct? (y/n): "):
                break
        
        # Ask for loop option
        loop = self._get_yes_no("\nEnable continuous rotation loop? (y/n): ")
        
        # Confirm
        print("\n" + "-"*60)
        print("ROTATION SUMMARY:")
        print(f"  X-axis (Pitch): {rot_x}°")
        print(f"  Y-axis (Yaw): {rot_y}°")
        print(f"  Z-axis (Roll): {rot_z}°")
        print(f"  Loop: {'Yes' if loop else 'No'}")
        
        if self._get_yes_no("\nConfirm rotation? (y/n): "):
            self.config.set_rotation(rot_x, rot_y, rot_z, loop)
            print("Rotation confirmed!")
            return True
        else:
            print("Rotation cancelled. Please restart.")
            return False
    
    def run(self) -> ConfigManager:
        """Run the complete interactive input process"""
        print("\n" + "="*70)
        print(" "*15 + "ROCKET ANIMATION CONFIGURATOR")
        print("="*70)
        print("\nThis tool will guide you through setting up your rocket animation.")
        print("Each stage will show real-time visualization in a 3D plot.")
        print("\nMake sure to view the Matplotlib window for visual feedback!")
        
        # Stage 1: Translation
        if not self.input_translation_stage():
            self.visualizer.close()
            return None
        
        # Stage 2: Rotation
        if not self.input_rotation_stage():
            self.visualizer.close()
            return None
        
        # Save configuration
        self.config.save()
        
        print("\n" + "="*70)
        print("CONFIGURATION COMPLETE!")
        print("="*70)
        print("\nAll settings have been saved.")
        print("Starting render process...")
        
        self.visualizer.close()
        return self.config

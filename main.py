"""
Main - Entry point untuk render rocket dengan input interaktif
USER INPUT: Translasi (path dengan titik-titik), Skala per titik, Rotasi (X, Y, Z)
Setiap input divisualisasikan secara real-time dengan Matplotlib
"""
print("\033c")
import os
import numpy as np
from interactive_input import InteractiveInput
from config_manager import ConfigManager
from rocket_model import RocketModel
from transform import Transform
from camera import Camera
from renderer import Renderer


def render_with_config(config: ConfigManager):
    """Render rocket using configuration"""
    print("\n" + "=" * 60)
    print("RENDERING ROCKET")
    print("=" * 60)
    
    print("\n[1] Building Rocket Model...")
    rocket = RocketModel(col=320, row=450, length=320)
    voxel_data = rocket.build()
    centroid = rocket.get_centroid()
    print(f"Rocket built! Centroid: {centroid}")
    
    print("\n[2] Setting up Camera...")
    cam_position = (rocket.cx, rocket.cy - 120, rocket.cz - 600)
    cam_target = (rocket.cx, rocket.cy, rocket.cz)
    camera = Camera(cam_position, cam_target)
    print(f"Camera positioned at: {cam_position}")
    print(f"Looking at: {cam_target}")
    
    print("\n[3] Initializing Renderer...")
    renderer = Renderer(width=640, height=480, fov=50, threshold=10)
    print("Renderer ready!")
    
    translation_points = config.get_translation_points()
    scales = config.get_scales()
    rotations = config.get_rotations()
    
    print("\n[4] Rendering frames...")
    
    if len(translation_points) == 0:
        translation_points = [[0, 0, 0]]
        scales = [1.0]
        rotations = [{"x": 0.0, "y": 0.0, "z": 0.0}]
    
    if len(rotations) < len(translation_points):
        for _ in range(len(translation_points) - len(rotations)):
            rotations.append({"x": 0.0, "y": 0.0, "z": 0.0})
    
    rendered_images = []
    for i, (point, scale, rotation) in enumerate(zip(translation_points, scales, rotations)):
        rot_x = rotation.get('x', 0.0)
        rot_y = rotation.get('y', 0.0)
        rot_z = rotation.get('z', 0.0)
        
        print(f"\n  Frame {i+1}/{len(translation_points)}:")
        print(f"    Position: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})")
        print(f"    Scale: {scale:.2f}x")
        print(f"    Rotation: X={rot_x}°, Y={rot_y}°, Z={rot_z}°")
        
        transform = Transform()
        transform.set_rotation_degrees(
            yaw=rot_y, 
            pitch=rot_x, 
            roll=rot_z
        )
        transform.set_translation(tx=point[0], ty=point[1], tz=point[2])
        
        pixel = renderer.render(voxel_data, camera, transform, centroid)
        rendered_images.append(pixel)
        
        output_file = f"rocket_frame_{i:03d}.jpg"
        filepath = renderer.save_image(pixel, output_file)
        print(f"    Saved: {filepath}")
    
    print("\n[5] Creating final composite...")
    if len(rendered_images) > 0:
        titles = [f"Frame {i}" for i in range(len(rendered_images))]
        renderer.display_images(rendered_images[:min(4, len(rendered_images))], 
                               titles[:min(4, len(rendered_images))])
    
    print("\n" + "=" * 60)
    print("RENDER COMPLETE!")
    print("=" * 60)
    print(f"\nOutput saved in 'result/' folder:")
    print(f"  - {len(rendered_images)} frame(s) rendered")
    print(f"  - Configuration: result/animation_config.json")
    print("=" * 60)


def main():
    print("=" * 70)
    print(" " * 15 + "ROCKET 3D RENDERER - INTERACTIVE MODE")
    print("=" * 70)
    print("\nThis program will guide you through:")
    print("  1. Translation Path - Define waypoints with grid visualization")
    print("  2. Scale per Point - Set object scale at each position")
    print("  3. Rotation - Configure X/Y/Z rotation with sphere preview")
    print("\nA Matplotlib window will open for real-time visualization.")
    print("Use the grid to measure coordinates accurately.")
    print("\n" + "-" * 70)
    
    load_existing = input("\nLoad existing configuration? (y/n, default=n): ").strip().lower()
    
    if load_existing == 'y':
        config = ConfigManager()
        config.load()
        print("\nUsing loaded configuration.")
    else:
        interactive = InteractiveInput()
        config = interactive.run()
        
        if config is None:
            print("\nConfiguration cancelled. Exiting.")
            return
    
    proceed = input("\nProceed with rendering? (y/n, default=y): ").strip().lower()
    if proceed == 'n':
        print("\nRender cancelled. Configuration saved for later use.")
        return
    
    render_with_config(config)
    
    print("\n" + "=" * 70)
    print("ALL DONE!")
    print("=" * 70)
    print("\nNotes:")
    print("  - All outputs saved in 'result/' folder")
    print("  - Configuration can be reused by loading animation_config.json")
    print("  - Re-run to create new animations")
    print("=" * 70)


if __name__ == "__main__":
    main()

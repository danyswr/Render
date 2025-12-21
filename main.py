"""
Main - Entry point untuk render rocket dengan input interaktif
Real-time visualization dengan rocket model asli
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
    print(f"✓ Rocket built! Centroid: {centroid}")
    
    print("\n[2] Setting up Camera...")
    camera_settings = config.get_camera_settings()
    cam_pos = camera_settings.get("translation", {}).get("position", [0, 0, -150])
    cam_rotation = camera_settings.get("rotation", {"pitch": 0, "yaw": 0})
    
    cam_position = (cam_pos[0] + rocket.cx, cam_pos[1] + rocket.cy, cam_pos[2] + rocket.cz)
    cam_target = (rocket.cx, rocket.cy, rocket.cz)
    
    # Convert pitch/yaw to x/y for Camera class
    camera = Camera(cam_position, cam_target, {
        "x": cam_rotation.get("pitch", 0),
        "y": cam_rotation.get("yaw", 0),
        "z": 0
    })
    print(f"✓ Camera positioned at: {cam_position}")
    print(f"✓ Camera rotation: Pitch={cam_rotation.get('pitch', 0)}° Yaw={cam_rotation.get('yaw', 0)}°")
    
    print("\n[3] Initializing Renderer...")
    canvas_settings = config.get_canvas_settings()
    renderer = Renderer(
        width=canvas_settings.get("width", 640),
        height=canvas_settings.get("height", 480),
        fov=canvas_settings.get("fov", 50),
        threshold=10
    )
    print("✓ Renderer ready!")
    
    animation_points = config.get_animation_points()
    render_settings = config.get_render_settings()
    total_frames = render_settings.get("total_frames", 1)
    
    print("\n[4] Rendering frames...")
    
    if len(animation_points) == 0:
        animation_points = [{
            "translation": {"position": [0, 0, 0]},
            "rotation": {"pitch": 0, "yaw": 0}
        }]
    
    rendered_images = []
    
    for i, point_data in enumerate(animation_points):
        translation = point_data["translation"]["position"]
        rotation = point_data["rotation"]
        
        rot_x = rotation.get('pitch', 0.0)
        rot_y = rotation.get('yaw', 0.0)
        
        print(f"\n  Frame {i+1}/{len(animation_points)}:")
        print(f"    Position: ({translation[0]:.1f}, {translation[1]:.1f}, {translation[2]:.1f})")
        print(f"    Rotation: Pitch={rot_x}°, Yaw={rot_y}°")
        
        transform = Transform()
        transform.set_rotation_degrees(
            yaw=rot_y,
            pitch=rot_x,
            roll=0
        )
        transform.set_translation(tx=translation[0], ty=translation[1], tz=translation[2])
        
        pixel = renderer.render(voxel_data, camera, transform, centroid)
        rendered_images.append(pixel)
        
        output_file = f"rocket_frame_{i:03d}.jpg"
        filepath = renderer.save_image(pixel, output_file)
        print(f"    ✓ Saved: {filepath}")
    
    print("\n[5] Creating final composite...")
    if len(rendered_images) > 0:
        titles = [f"Frame {i+1}" for i in range(len(rendered_images))]
        renderer.display_images(rendered_images[:min(4, len(rendered_images))],
                               titles[:min(4, len(rendered_images))])
    
    print("\n" + "=" * 60)
    print("RENDER COMPLETE!")
    print("=" * 60)
    print(f"\nOutput saved in 'result/' folder:")
    print(f"  - {len(rendered_images)} frame(s) rendered")
    print(f"  - Configuration: result/animation_config.json")
    print(f"  - Total frames configured: {total_frames}")
    print("=" * 60)


def main():
    print("=" * 70)
    print(" " * 15 + "ROCKET 3D RENDERER - INTERACTIVE MODE v2")
    print("=" * 70)
    print("\nThis program will guide you through:")
    print("  1. Camera Setup - Position and rotation (Pitch/Yaw)")
    print("  2. Translation Path - Define waypoints with real-time rocket preview")
    print("  3. Rotation - Configure object rotation at each position")
    print("  4. Frame Count - Set how many frames to render")
    print("\nReal-time Matplotlib visualization with actual rocket model!")
    print("\n" + "-" * 70)
    
    load_existing = input("\nLoad existing configuration? (y/N, tekan Enter=tidak): ").strip().lower()
    
    if load_existing == 'y':
        config = ConfigManager()
        config.load()
        print("\n✓ Using loaded configuration.")
    else:
        interactive = InteractiveInput()
        config = interactive.run()
        
        if config is None:
            print("\n✗ Configuration cancelled. Exiting.")
            return
    
    proceed = input("\nProceed with rendering? (Y/n, tekan Enter=ya): ").strip().lower()
    if proceed == 'n':
        print("\n✗ Render cancelled. Configuration saved for later use.")
        return
    
    render_with_config(config)
    
    print("\n" + "=" * 70)
    print("ALL DONE!")
    print("=" * 70)
    print("\nNotes:")
    print("  - All outputs saved in 'result/' folder")
    print("  - Configuration saved as animation_config.json")
    print("  - Run again to create new animations")
    print("=" * 70)


if __name__ == "__main__":
    main()

"""
Main - Entry point untuk render rocket dengan input manual
USER INPUT: Rotasi (Yaw, Pitch, Roll) dan Translasi (X, Y, Z)
"""
print("\033c")  # Clear console
import numpy as np
from rocket_model import RocketModel
from transform import Transform
from camera import Camera
from renderer import Renderer


def main():
    print("=" * 60)
    print("🚀 ROCKET 3D RENDERER - OOP VERSION")
    print("=" * 60)
    
    # ===== 1. BUILD ROCKET (OBJECT TIDAK DIUBAH) =====
    print("\n[1] Building Rocket Model...")
    rocket = RocketModel(col=320, row=450, length=320)
    voxel_data = rocket.build()
    centroid = rocket.get_centroid()
    print(f"✅ Rocket built! Centroid: {centroid}")
    
    # ===== 2. SETUP CAMERA (TETAP) =====
    print("\n[2] Setting up Camera...")
    cam_position = (rocket.cx, rocket.cy - 120, rocket.cz - 600)  # Belakang & atas
    cam_target = (rocket.cx, rocket.cy, rocket.cz)
    camera = Camera(cam_position, cam_target)
    print(f"✅ Camera positioned at: {cam_position}")
    print(f"   Looking at: {cam_target}")
    
    # ===== 3. SETUP RENDERER =====
    print("\n[3] Initializing Renderer...")
    renderer = Renderer(width=640, height=480, fov=50, threshold=10)
    print("✅ Renderer ready!")
    
    # ===== 4. USER INPUT MANUAL =====
    print("\n" + "=" * 60)
    print("📝 INPUT MANUAL - TRANSFORMASI ROCKET")
    print("=" * 60)
    
    try:
        print("\n🔄 ROTASI (dalam derajat):")
        yaw = float(input("  • Yaw (rotasi Y-axis, -180 s/d 180): ") or "0")
        pitch = float(input("  • Pitch (rotasi X-axis, -180 s/d 180): ") or "0")
        roll = float(input("  • Roll (rotasi Z-axis, -180 s/d 180): ") or "0")
        
        print("\n📍 TRANSLASI:")
        tx = float(input("  • Translasi X (kiri/kanan): ") or "0")
        ty = float(input("  • Translasi Y (atas/bawah): ") or "0")
        tz = float(input("  • Translasi Z (maju/mundur): ") or "0")
        
    except ValueError:
        print("❌ Input tidak valid! Menggunakan default (0)...")
        yaw = pitch = roll = tx = ty = tz = 0
    
    # ===== 5. APPLY TRANSFORM =====
    print("\n[4] Applying Transformations...")
    transform = Transform()
    transform.set_rotation_degrees(yaw=yaw, pitch=pitch, roll=roll)
    transform.set_translation(tx=tx, ty=ty, tz=tz)
    print(f"✅ Rotation: Yaw={yaw}°, Pitch={pitch}°, Roll={roll}°")
    print(f"✅ Translation: X={tx}, Y={ty}, Z={tz}")
    
    # ===== 6. RENDER =====
    print("\n[5] Rendering...")
    pixel = renderer.render(voxel_data, camera, transform, centroid)
    
    # ===== 7. SAVE & DISPLAY =====
    output_file = "rocket_render.jpg"
    renderer.save_image(pixel, output_file)
    print(f"✅ Saved to: {output_file}")
    
    print("\n[6] Displaying result...")
    title = f"Rocket | Yaw={yaw}° Pitch={pitch}° Roll={roll}° | T=({tx},{ty},{tz})"
    renderer.display_images([pixel], [title])
    
    print("\n" + "=" * 60)
    print("✅ SELESAI!")
    print("=" * 60)
    print("📌 NOTES:")
    print("  • Object Rocket: 100% TIDAK DIUBAH")
    print("  • Transformasi: User input manual")
    print("  • Kamera: Tetap di belakang & atas")
    print("  • Architecture: Clean OOP (4 class + main)")
    print("=" * 60)


if __name__ == "__main__":
    main()

render_3D_to_2D.py


"""
Render 3D Voxel to 2D Image - FINAL HIGH QUALITY
=================================================
Metode: VECTORIZED FORWARD PROJECTION (POINT CLOUD SPLATTING)
- Kualitas Solid: Menggunakan splatting (titik besar) untuk menutup lubang.
- Kecepatan: Menggunakan NumPy Matrix Operations (sangat cepat).
- Trajectory: "Dynamic LookAt" -> Memanipulasi sudut pandang kamera agar roket mulai dari pojok dan ke tengah.
"""

print("\033c")
import numpy as np
from matplotlib import pyplot as plt
import os

#=====================================================================================
nama_file_base = "shuttle_realistic_space"
input_folder = "/home/danyswr/Render/result_npy63"
output_folder = "/home/danyswr/Render/result_npy63"

wallpaper_path = "/home/danyswr/Render/wallpaper/cosmic.png"

threshold = 10
no_of_frames = 24

# Camera Settings
cam_focal = 500
cam_pos_base = np.array([-600, 400, -600]) # Posisi Kamera (Kiri-Atas-Belakang)

# Ukuran Splat (Agar solid, titik digambar lebih besar dari 1 pixel)
SPLAT_SIZE = 2

#=====================================================================================

print(f"Screen: 1024 x 1024")

# Load wallpaper
print(f"Loading wallpaper...")
try:
    wallpaper = plt.imread(wallpaper_path)
    # Resize wallpaper to 1024x1024 (or use original)
    rows, cols = 1024, 1024
    if wallpaper.shape[0] != rows or wallpaper.shape[1] != cols:
        h, w = wallpaper.shape[:2]
        row_idx = np.clip((np.arange(rows) * h / rows).astype(int), 0, h-1)
        col_idx = np.clip((np.arange(cols) * w / cols).astype(int), 0, w-1)
        wallpaper = wallpaper[row_idx][:, col_idx]
    if wallpaper.dtype != np.uint8:
        wallpaper = (wallpaper * 255).astype(np.uint8) if wallpaper.max() <= 1.0 else wallpaper.astype(np.uint8)
    if len(wallpaper.shape) == 2:
        wallpaper = np.stack([wallpaper]*3, axis=-1)
    elif wallpaper.shape[2] == 4:
        wallpaper = wallpaper[:, :, :3]
    use_wallpaper = True
    print("  Wallpaper ready!")
except:
    use_wallpaper = False
    wallpaper = np.zeros((1024, 1024, 3), dtype=np.uint8)

def draw_moon(pixel, center_x, center_y, radius, progress):
    """Draw clean, simple moon using numpy only."""
    rows, cols = pixel.shape[:2]
    
    # Create coordinate grids
    y_grid, x_grid = np.ogrid[:rows, :cols]
    
    # Distance from center
    dx = x_grid - center_x
    dy = y_grid - center_y
    dist = np.sqrt(dx**2 + dy**2)
    
    # Moon mask
    moon_mask = dist <= radius
    
    # Simple 3D shading: brighter on one side, darker on other
    # Light comes from upper-left
    light_offset_x = -0.3 * radius
    light_offset_y = -0.3 * radius
    
    dist_from_light = np.sqrt((dx - light_offset_x)**2 + (dy - light_offset_y)**2)
    
    # Normalize and invert: closer to light = brighter
    max_dist = radius * 1.5
    brightness_factor = 1 - (dist_from_light / max_dist)
    brightness_factor = np.clip(brightness_factor, 0.3, 1.0)
    
    # Base moon color
    base_color = 220 + int(35 * progress)  # Gets brighter as rocket approaches
    
    # Apply shading
    shaded = (brightness_factor * base_color).astype(np.uint8)
    
    # Draw moon with warm gray tint
    pixel[moon_mask, 0] = shaded[moon_mask]
    pixel[moon_mask, 1] = shaded[moon_mask]
    pixel[moon_mask, 2] = (shaded[moon_mask] * 0.95).astype(np.uint8)
    
    # Simple craters (just darker circles)
    crater_list = [
        (center_x - radius*0.3, center_y - radius*0.2, radius*0.15),
        (center_x + radius*0.25, center_y + radius*0.3, radius*0.12),
        (center_x + radius*0.1, center_y - radius*0.35, radius*0.1),
    ]
    
    for cx, cy, cr in crater_list:
        crater_dist = np.sqrt((x_grid - cx)**2 + (y_grid - cy)**2)
        crater_mask = (crater_dist <= cr) & moon_mask
        # Darken crater area
        pixel[crater_mask] = (pixel[crater_mask] * 0.7).astype(np.uint8)
    
    # Soft edge (anti-aliasing)
    edge_width = 3
    edge_mask = (dist > radius - edge_width) & (dist <= radius)
    edge_alpha = (radius - dist[edge_mask]) / edge_width
    for c in range(3):
        pixel[edge_mask, c] = (pixel[edge_mask, c] * edge_alpha).astype(np.uint8)
    
    return pixel

def look_at_matrix(eye, target, up=np.array([0, 1, 0])):
    """Membuat View Matrix (World -> Camera)."""
    z_axis = eye - target # Forward (kamera melihat ke -Z, jadi Z axis adalah vector ke belakang)
    z_axis = z_axis / np.linalg.norm(z_axis)
    
    x_axis = np.cross(up, z_axis)
    x_axis = x_axis / np.linalg.norm(x_axis)
    
    y_axis = np.cross(z_axis, x_axis)
    
    # Rotation (Row-major: Proyeksi titik ke axis local kamera)
    # [ Rx Ry Rz ]
    # [ Ux Uy Uz ]
    # [ Fx Fy Fz ]
    
    R = np.array([
        [x_axis[0], x_axis[1], x_axis[2]],
        [y_axis[0], y_axis[1], y_axis[2]],
        [z_axis[0], z_axis[1], z_axis[2]]
    ])
    
    # Translation: Camera position becomes origin
    # T = -dot(R, eye)
    # Matrix 4x4
    
    View = np.eye(4)
    View[:3, :3] = R
    View[:3, 3] = -R @ eye
    return View

def project_points(points, view_matrix, focal, width, height):
    """Proyeksi titik 3D ke layar 2D."""
    # 1. Transform World -> Camera
    # Points Nx3 -> Homogeneous Nx4
    n = points.shape[0]
    ones = np.ones((n, 1))
    pts_h = np.hstack([points, ones]) # (N, 4)
    
    # Apply View Matrix
    # (View @ pts_h.T).T -> pts_cam
    pts_cam = (view_matrix @ pts_h.T).T # (N, 4)
    
    # 2. Project Camera -> Screen
    # x_cam = pts_cam[:, 0]
    # y_cam = pts_cam[:, 1]
    # z_cam = pts_cam[:, 2] # Depth
    
    # Filter titik di belakang kamera (z > 0 jika forward -z, disini z axis kita +z ke belakang)
    # Jadi titik di depan kamera harus punya z negatif (OpenGL convention)?
    # LookAt kita: z_axis = eye - target. Forward world vector is -z_axis.
    # Titik transformed akan punya Z negatif jika di depan kamera.
    
    # Perspective division
    # x_screen = x / -z * f + cw
    # y_screen = y / -z * f + ch
    
    x = pts_cam[:, 0]
    y = pts_cam[:, 1]
    z = pts_cam[:, 2] # Positive if behind camera
    
    # Valid mask (objects in front of camera, Z < 0)
    # Wait, z_axis = eye - target -> points to viewer.
    # So points in front of cam have Negative Z.
    mask = z < -10 
    
    # Inverse depth for projection (positive dist)
    dist = -z
    
    scale = focal / dist
    
    screen_x = width // 2 + x * scale
    screen_y = height // 2 - y * scale # Flip Y for screen
    
    return screen_x, screen_y, dist, mask, x, y, z

def ease_in_out(t):
    return t * t * (3 - 2 * t)

print(f"\n{'='*50}")
print(f"HIGH QUALITY RENDER (Forward Splatting)")
print(f"{'='*50}\n")

plt.figure(figsize=(10, 10))

# Loop Frames
for frame_num in range(1, no_of_frames + 1):
    frame_path = os.path.join(input_folder, f"{nama_file_base}frame{frame_num}.npy")
    
    if not os.path.exists(frame_path):
        print(f"Waiting for frame {frame_num}...")
        continue
        
    try:
        voxel = np.load(frame_path)
    except:
        continue

    # ANALISIS POSISI OBJECT (utk centering)
    # Cari bounding box atau center of mass
    indices = np.argwhere(np.sum(voxel[:,:,:,:3], axis=3) > threshold)
    if len(indices) == 0: continue
    
    # Indices (y, x, z)
    ys = indices[:, 0]
    xs = indices[:, 1]
    zs = indices[:, 2]
    colors = voxel[ys, xs, zs]
    
    # Center object real
    obj_center = np.mean(indices, axis=0) # y, x, z
    obj_pos_world = np.array([obj_center[1], obj_center[0], obj_center[2]]) # x, y, z
    
    # Convert voxel indices to points
    # Voxel grid (0..399). Origin 0,0,0
    # Map to world centered at 0,0,0?
    points = np.stack([xs, ys, zs], axis=1).astype(float)
    # Center the world so 200,200,200 is 0,0,0?
    # No, keep raw, adjust camera.
    
    # ANIMASI KAMERA (Trajectory Logic)
    # Frame 1: Rocket START (Kanan-Bawah, DEKAT kamera = BESAR)
    # Frame 24: Rocket END (Kiri-Atas dekat bulan, JAUH kamera = KECIL)
    
    progress = (frame_num - 1) / (no_of_frames - 1)
    t = ease_in_out(progress)
    
    # ========== FIXED CAMERA - TIDAK MENGIKUTI ROKET ==========
    # Kamera melihat ke TITIK TETAP di tengah grid (256, 200, 256)
    # Roket bergerak melewati frame, BUKAN frame mengikuti roket!
    
    # Posisi kamera: di belakang-bawah, melihat ke tengah-atas
    cam_pos = np.array([256, 300, -250])  # Kamera SUPER DEKAT (Z=-250) untuk roket BESAR
    
    # Target kamera: TITIK TETAP di tengah grid (bukan obj_pos_world!)
    # Ini membuat roket bergerak di dalam frame
    grid_center = np.array([256, 256, 256])  # Tengah grid 512x512x512
    
    # View Matrix - kamera melihat ke tengah, BUKAN mengikuti roket
    view_mat = look_at_matrix(cam_pos, grid_center, up=np.array([0, 1, 0]))
    
    # PROJECTION
    sx, sy, dist, mask, _, _, _ = project_points(points, view_matrix=view_mat, focal=cam_focal, width=1024, height=1024)
    
    # ============ DIRECT SCREEN OFFSET - FORCE POSITION! ============
    # Ini PAKSA roket bergerak di layar dari pojok ke pojok
    # Screen: 1024x1024, Moon at (200, 200)
    
    # Frame 1: Start at BOTTOM-RIGHT corner (around 750, 750)
    # Frame 24: End at TOP-LEFT near moon (around 280, 280)
    
    start_screen_x = 350   # Offset ke KANAN dari center (512 + 350 = 862)
    start_screen_y = 350   # Offset ke BAWAH dari center (512 + 350 = 862)
    
    end_screen_x = -250    # Offset ke KIRI dari center (512 - 250 = 262, dekat moon X=200)
    end_screen_y = -250    # Offset ke ATAS dari center (512 - 250 = 262, dekat moon Y=200)
    
    # Interpolasi LURUS berdasarkan progress
    current_offset_x = start_screen_x + (end_screen_x - start_screen_x) * t
    current_offset_y = start_screen_y + (end_screen_y - start_screen_y) * t
    
    # TERAPKAN offset ke koordinat screen!
    sx = sx + current_offset_x
    sy = sy + current_offset_y
    # ================================================================
    
    # Filter valid
    valid_points = mask
    
    # Sort by Depth (Painter's Algorithm) -> Jauh digambar duluan
    # Dist is positive distance. Large = Far.
    # Sort Ascending? No, Descending (Large Dist first).
    # Painter: Draw Background (Far) then Foreground (Close).
    
    sx_valid = sx[valid_points]
    sy_valid = sy[valid_points]
    dist_valid = dist[valid_points]
    colors_valid = colors[valid_points]
    
    sort_idx = np.argsort(dist_valid)[::-1] # Descending
    
    sx_sorted = sx_valid[sort_idx]
    sy_sorted = sy_valid[sort_idx]
    c_sorted = colors_valid[sort_idx]
    
    # RENDER TO PIXEL GRID
    if use_wallpaper:
        pixel = wallpaper.copy()
    else:
        pixel = np.zeros((1024, 1024, 3), dtype=np.uint8)
        
    # Splatting (simulasi soliditas)
    # Gambar titik sebagai kotak 2x2 atau 3x3
    # Kita loop manual di pixel array? Lambat di python.
    # Tapi kita punya sorted lists.
    # Bisa pakai scatter plot matplotlib lalu save? 
    # Matplotlib scatter lambat untuk 100k points.
    # Direct pixel manipulation is fastest if vectorized, but splatting needs loop or dilation.
    
    # Trik Vectorized Splatting:
    # Round coordinates
    ix = np.round(sx_sorted).astype(int)
    iy = np.round(sy_sorted).astype(int)
    
    # Filter screen bounds (dengan margin untuk splat)
    in_screen = (ix >= 0) & (ix < 1024-SPLAT_SIZE) & (iy >= 0) & (iy < 1024-SPLAT_SIZE)
    
    ix = ix[in_screen]
    iy = iy[in_screen]
    c_final = c_sorted[in_screen]
    
    # Draw Splat (2x2)
    # Overwrite pixels (Painter's Algo ensures correctness)
    # Order: Far to Near.
    
    # Vectorized write dengan advanced indexing akan mengambil last value (Near). Correct.
    pixel[iy, ix] = c_final
    pixel[iy+1, ix] = c_final
    pixel[iy, ix+1] = c_final
    pixel[iy+1, ix+1] = c_final
    
    # (Optional: 3x3 for super solidity)
    if SPLAT_SIZE > 2:
        pixel[iy+2, ix] = c_final
        pixel[iy, ix+2] = c_final
        pixel[iy+2, ix+2] = c_final
        pixel[iy+1, ix+2] = c_final
        pixel[iy+2, ix+1] = c_final
    
    # DRAW MOON as destination target (upper-left area)
    # FIXED position and size - NO scaling
    moon_x = 200  # Fixed X (scaled for 1024x1024)
    moon_y = 200  # Fixed Y (scaled for 1024x1024)
    moon_radius = 100  # Fixed radius (scaled for 1024x1024)
    pixel = draw_moon(pixel, moon_x, moon_y, moon_radius, progress)
    
    plt.clf()
    plt.imshow(pixel)
    plt.title(f"Final Render - Frame {frame_num}", color='white')
    plt.axis('off')
    plt.pause(0.01)
    
    output_path = os.path.join(output_folder, f"render_{nama_file_base}_{frame_num}.jpg")
    plt.imsave(output_path, pixel)
    print(f"Saved: {output_path} (ObjZ: {obj_center[2]:.1f})")

print("\nDONE!")
plt.show()
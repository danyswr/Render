#!/usr/bin/env python3
"""
ROCKET PREVIEW TOOL
==================
Lihat design roket SEBELUM rendering.
- Tampilkan 3D view dengan axis 0, 1, 2 (X, Y, Z)
- Close window untuk lanjut render
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os
import sys

# Import dari create_shuttle
sys.path.insert(0, '/home/danyswr/Render')
from create_shuttle import VoxelModel, ShuttleBuilder

def preview_rocket():
    print("\n" + "="*60)
    print("ROCKET PREVIEW TOOL")
    print("="*60)
    print("Lihat design roket SEBELUM rendering.")
    print("TUTUP WINDOW untuk lanjut ke rendering.")
    print("="*60 + "\n")
    
    # Build rocket model
    print("Building rocket model for preview...")
    model = VoxelModel(400, 400, 400)  # Create empty model
    builder = ShuttleBuilder(model, include_boosters=False)  # Pass model to builder
    builder.build()  # Build the shuttle
    voxel = model.data
    
    # Get non-empty voxels
    threshold = 10
    indices = np.argwhere(np.sum(voxel[:,:,:,:3], axis=3) > threshold)
    
    if len(indices) == 0:
        print("ERROR: No voxels found!")
        return False
    
    print(f"Found {len(indices)} voxels")
    
    # Extract coordinates and colors
    ys = indices[:, 0]  # Axis 0
    xs = indices[:, 1]  # Axis 1
    zs = indices[:, 2]  # Axis 2
    colors = voxel[ys, xs, zs, :3] / 255.0  # Normalize to 0-1
    
    # Subsample for faster display (max 10000 points)
    if len(indices) > 10000:
        step = len(indices) // 10000
        ys = ys[::step]
        xs = xs[::step]
        zs = zs[::step]
        colors = colors[::step]
        print(f"Subsampled to {len(ys)} voxels for display")
    
    # Create 3D plot
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Scatter plot
    ax.scatter(xs, ys, zs, c=colors, s=1, alpha=0.8)
    
    # Set labels with axis numbers
    ax.set_xlabel('Axis 1 (X) - Width', fontsize=12)
    ax.set_ylabel('Axis 0 (Y) - Length', fontsize=12)
    ax.set_zlabel('Axis 2 (Z) - Height', fontsize=12)
    
    # Title
    ax.set_title('ROCKET PREVIEW\n(Tutup window untuk lanjut render)', fontsize=14, fontweight='bold')
    
    # Add axis arrows at origin
    center_x, center_y, center_z = model.cx, model.cy, model.cz
    arrow_len = 50
    
    # Draw axis arrows
    ax.quiver(center_x, center_y, center_z, arrow_len, 0, 0, color='red', arrow_length_ratio=0.3, linewidth=2)
    ax.quiver(center_x, center_y, center_z, 0, arrow_len, 0, color='green', arrow_length_ratio=0.3, linewidth=2)
    ax.quiver(center_x, center_y, center_z, 0, 0, arrow_len, color='blue', arrow_length_ratio=0.3, linewidth=2)
    
    # Add axis labels near arrows
    ax.text(center_x + arrow_len + 10, center_y, center_z, '1 (X)', color='red', fontsize=10, fontweight='bold')
    ax.text(center_x, center_y + arrow_len + 10, center_z, '0 (Y)', color='green', fontsize=10, fontweight='bold')
    ax.text(center_x, center_y, center_z + arrow_len + 10, '2 (Z)', color='blue', fontsize=10, fontweight='bold')
    
    # Set equal aspect ratio
    max_range = np.array([xs.max()-xs.min(), ys.max()-ys.min(), zs.max()-zs.min()]).max() / 2.0
    mid_x = (xs.max()+xs.min()) * 0.5
    mid_y = (ys.max()+ys.min()) * 0.5
    mid_z = (zs.max()+zs.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    print("\n>>> PREVIEW WINDOW OPENED <<<")
    print(">>> Putar view dengan mouse untuk melihat dari berbagai sudut <<<")
    print(">>> TUTUP WINDOW untuk lanjut ke rendering <<<\n")
    
    plt.tight_layout()
    plt.show()
    
    print("\n>>> PREVIEW CLOSED <<<")
    return True

def run_full_pipeline():
    """Run the full render pipeline after preview."""
    print("\n" + "="*60)
    print("STARTING FULL RENDER PIPELINE")
    print("="*60 + "\n")
    
    import subprocess
    
    # Run create_shuttle.py
    print("Step 1: Generating .npy frames...")
    result1 = subprocess.run(['python', 'create_shuttle.py'], cwd='/home/danyswr/Render')
    
    if result1.returncode != 0:
        print("ERROR: create_shuttle.py failed!")
        return
    
    # Run render_3D_to_2D.py
    print("\nStep 2: Rendering .jpg frames...")
    result2 = subprocess.run(['python', 'render_3D_to_2D.py'], cwd='/home/danyswr/Render')
    
    if result2.returncode != 0:
        print("ERROR: render_3D_to_2D.py failed!")
        return
    
    print("\n" + "="*60)
    print("RENDER COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    # Show preview first
    preview_ok = preview_rocket()
    
    if preview_ok:
        # Ask user if they want to continue
        print("\nPreview selesai.")
        response = input("Lanjut render? (y/n): ").strip().lower()
        
        if response == 'y' or response == 'yes' or response == '':
            run_full_pipeline()
        else:
            print("Render dibatalkan.")
    else:
        print("Preview gagal, render dibatalkan.")

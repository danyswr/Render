# Rocket 3D Renderer

## Overview
A Python-based 3D rocket renderer using voxel graphics with interactive input. The application creates a 3D rocket model and allows users to define translation paths, scale per point, and rotation with real-time matplotlib visualization.

## Project Structure
- `main.py` - Entry point with interactive input flow
- `rocket_model.py` - 3D voxel rocket model builder
- `transform.py` - 3D transformation handling (rotation + translation)
- `camera.py` - 3D camera positioning and world-to-camera space conversion
- `renderer.py` - Voxel to 2D image rendering with depth buffer
- `visualizer.py` - Real-time matplotlib visualization with TkAgg backend
- `interactive_input.py` - Step-by-step interactive input with confirmation
- `config_manager.py` - Configuration saving/loading (JSON format)

## How to Run
Run the workflow "Rocket 3D Renderer" which executes `python main.py`.

### Interactive Stages:
1. **Translation Path** - Define waypoints with CRUD menu
   - **Add** new points, **Edit** existing points, **Delete** points
   - Red points connected by lines show the path
   - Grid helps measure coordinates
   - Purple camera indicator shows camera position (far from object)
   
2. **Scale per Point** - Set object scale at each position
   - **Edit** scale for individual points
   - **Set All Same** - apply same scale to all points
   - Colored sphere visualization shows orientation
   - Camera indicator shows viewing angle

3. **Rotation per Point** - Configure X/Y/Z rotation at each waypoint
   - **Edit** rotation for individual points
   - **Set All Same** - apply same rotation to all points
   - Colored sphere with axis arrows shows orientation
   - Option for loop rotation

### Menu System
Each stage displays a numbered list and menu:
```
==========================
  DAFTAR TITIK
==========================
  1. START: (0, 0, 0)
  2. P1: (10, 10, 10)
  3. END: (50, 50, 50)
==========================
------------------------------
  OPSI:
------------------------------
  1. Tambah Titik
  2. Edit Titik
  3. Hapus Titik
  4. Konfirmasi
------------------------------
```

### Camera Indicator
All visualization stages show a purple camera indicator:
- Purple sphere labeled "KAMERA" = camera position (positioned far from object)
- Arrow = direction camera is looking toward the object
- Helps users understand the viewing angle for final render

### Output
All outputs are saved to `result/` folder:
- `rocket_frame_XXX.jpg` - Rendered frames at each point
- `rocket_display.png` - Composite display image
- `animation_config.json` - Saved configuration (can be reloaded)

## Dependencies
- numpy - Numerical operations and matrix math
- matplotlib - Real-time visualization (TkAgg) and image saving (Agg)

## Recent Changes
- December 2025: Added camera direction indicator in all visualizations (purple sphere with arrow)
- December 2025: Changed rotation to per-point system (like scale and translation)
- December 2025: Added backward compatibility for legacy config files
- December 2025: Added interactive input with real-time matplotlib visualization
- December 2025: All outputs now saved to result/ folder
- December 2025: Configuration persistence with JSON format

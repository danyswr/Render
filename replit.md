# Rocket 3D Renderer

## Overview
A Python-based 3D rocket renderer using voxel graphics with interactive input. The application creates a 3D rocket model and allows users to define translation paths, scale per point, and rotation with real-time matplotlib visualization.

## Project Structure
- `main.py` - Entry point with interactive input flow
- `rocket_model.py` - 3D voxel rocket model builder
- `transform.py` - 3D transformation handling (rotation + translation)
- `camera.py` - 3D camera with position and rotation support
- `renderer.py` - Voxel to 2D image rendering with depth buffer
- `visualizer.py` - Real-time matplotlib dual-view visualization (Scene + Camera POV)
- `interactive_input.py` - Step-by-step interactive input with confirmation and defaults
- `config_manager.py` - Configuration saving/loading (JSON format) with camera settings

## How to Run
Run the workflow "Rocket 3D Renderer" which executes `python main.py`.

### Interactive Stages:
0. **Camera Setup** - Configure camera position and rotation
   - Position (X, Y, Z) - where camera is located (default: 0, 0, -150)
   - Rotation (X, Y, Z) - camera orientation in degrees
   - Camera is positioned OUTSIDE the grid
   
1. **Translation Path** - Define waypoints with CRUD menu
   - **Add** new points, **Edit** existing points, **Delete** points
   - Red points connected by lines show the path
   - Grid helps measure coordinates

2. **Scale per Point** - Set object scale at each position
   - **Edit** scale for individual points
   - **Set All Same** - apply same scale to all points

3. **Rotation per Point** - Configure X/Y/Z rotation at each waypoint
   - **Edit** rotation for individual points
   - **Set All Same** - apply same rotation to all points

### Dual Matplotlib View
During all stages, TWO matplotlib windows are shown:
- **Left (Scene View)**: 3D scene with grid, objects, and camera indicator
- **Right (Camera POV)**: What the camera sees from its position/rotation

### Default Values
All inputs support pressing Enter for default values:
- Y/n prompts: Enter = Yes (unless marked as y/N)
- Numeric inputs: Enter = shown default value
- Menu choices: Enter = default option (marked with [default])

### Output
All outputs are saved to `result/` folder:
- `rocket_frame_XXX.jpg` - Rendered frames at each point
- `rocket_display.png` - Composite display image
- `animation_config.json` - Saved configuration (can be reloaded)

## Dependencies
- numpy - Numerical operations and matrix math
- matplotlib - Real-time visualization (TkAgg) and image saving (Agg)

## Recent Changes
- December 2025: Added dual matplotlib view (Scene + Camera POV)
- December 2025: Camera now positioned OUTSIDE the grid
- December 2025: Added camera position and rotation controls
- December 2025: All inputs have default values (press Enter to skip)
- December 2025: Camera settings saved in config file

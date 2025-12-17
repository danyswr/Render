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
1. **Translation Path** - Define waypoints (start, waypoints, end) with grid visualization
   - Red points connected by lines show the path
   - Grid helps measure coordinates
2. **Scale per Point** - Set object scale at each position
   - Colored sphere visualization shows orientation (red=front, green=sides, blue=back)
3. **Rotation** - Configure X/Y/Z rotation with sphere preview
   - Colored sphere with axis arrows shows orientation
   - Option for loop rotation

Each stage requires confirmation before proceeding.

### Output
All outputs are saved to `result/` folder:
- `rocket_frame_XXX.jpg` - Rendered frames at each point
- `rocket_display.png` - Composite display image
- `animation_config.json` - Saved configuration (can be reloaded)

## Dependencies
- numpy - Numerical operations and matrix math
- matplotlib - Real-time visualization (TkAgg) and image saving (Agg)

## Recent Changes
- December 2025: Added interactive input with real-time matplotlib visualization
- December 2025: All outputs now saved to result/ folder
- December 2025: Configuration persistence with JSON format

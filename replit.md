# Rocket 3D Renderer

## Overview
A Python-based 3D rocket renderer using voxel graphics. The application creates a 3D rocket model and allows users to apply transformations (rotation and translation) to view the rocket from different perspectives.

## Project Structure
- `main.py` - Entry point with user input interface
- `rocket_model.py` - 3D voxel rocket model builder
- `transform.py` - 3D transformation handling (rotation + translation)
- `camera.py` - 3D camera positioning and world-to-camera space conversion
- `renderer.py` - Voxel to 2D image rendering with depth buffer
- `visualizer.py` - Matplotlib-based visualization utilities
- `interactive_input.py` - Interactive input handling
- `config_manager.py` - Configuration management

## How to Run
Run the workflow "Rocket 3D Renderer" which executes `python main.py`. The console will prompt for:
1. Rotation values (Yaw, Pitch, Roll in degrees)
2. Translation values (X, Y, Z)

After entering values, the renderer generates images saved to:
- `rocket_render.jpg` - Raw render output
- `rocket_display.png` - Displayed image with title

## Dependencies
- numpy - Numerical operations and matrix math
- matplotlib - Image saving and display

## Recent Changes
- December 2025: Configured for Replit environment with Agg backend for matplotlib

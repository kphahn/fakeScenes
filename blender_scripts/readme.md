# Blender scripts

These scripts will only run from within Blender's Python environment. They are not standalone scripts. Execute them from the Blender text editor.

## import_track.py

This script imports a track from `.json` track files, generated with `generate_tracks.py`. The track's origin is placed at the 3D cursor. Placement is done by placing the cones higher than the 3D cursor and then doing a rigid body simulation to drop them onto the ground. This makes the cones align with the ground, even if it's uneven. The camera is animated to follow the track path, where each path coordinate is a keyframe in Blender.

The import track depends on the following Blender setup:

- The scene needs reference cone models, specifically named:
  - `cone_big`
  - `cone_blue`
  - `cone_yellow`
- There needs to be an object named `ground`, which will be used as collision for the rigid body simulation. The ground needs to be large enough to cover the track area. Optionally, it can be uneven to make the cone placement more realistic.
- The scene needs a camera named `lidar`
- There needs to be a collection named `cone_track` where the cones are placed

## run_range_scanner.py

This script generates synthetic LIDAR data using the [Blender Range Scanner](https://github.com/ln-12/blainder-range-scanner) addon. The script steps through each frame and saves the generated LIDAR data as `.npy`. Although the script can be called directly in Blender, it's more convenient to use the `generate_point_clouds.py` Python file in the project root.

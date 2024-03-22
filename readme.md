# FakeScenes

### Generate synthetic LIDAR in the [coneScenes format](https://github.com/Chalmers-Formula-Student/coneScenes)

This is a tool to generate fake LiDAR data for training neural networks to detect FSG cones in a Formula Student track environment.

## Usage

See **First time setup** below for initial setup instructions.

### Generate track layouts

The track layout generator is forked from [EUFS_sim](https://gitlab.com/eufs/eufs_sim), and creates multiple track layouts with cones and a lidar path.
The script has default arguments for the output directory (generated/tracks) and number of tracks to generate, but you can override them with the `--output` and `--num_tracks` arguments.

```bash
python generate_tracks.py --output another/directory --num_tracks 42
```

### Plot track layouts

Use `plot_track_layout.py` to plot the generated track layouts. Call the script with the path to the track layout file:

```bash
python plot_track_layout.py generated/tracks/track_0.json
```

### Import track layout into Blender

Open up the Blender project `scene.blend`. It already has the reference models and configurations needed by the import script. Once in Blender, in the text editor panel, open the script `import_track.py`. Feel free to change the path to the track layout file in the script. Then run the script using the play button in Blender. After a few seconds, the track layout should be imported into the scene. If you want to make a new scene from scratch, see `blender_scripts/readme.md` for what `import_track.py` requires in the Blender scene.

All cones, big, blue, yellow, are placed in the scene. They're dropped from a meter in the air onto the ground, so even if the ground is uneven, the cones will be placed correctly. Additionally, the camera will follow the path set by the track layout, where each path coordinate is a keyframe in Blender.

You'll also notice that the track's center point is at the 3D cursor. The easiest way to move it is to move the 3D cursor and run the script again. You can move everything in Blender without re-importing the track layout, but then you need to offset the camera animation path as well, and maybe re-align the cones with the ground.

Optionally at this point you can add more objects to the scene, like trees, buildings, walls, etc. to make the lidar data more representative of a real track environment.

### Batch generate synthetic LIDAR data

When you're ready with your scene, save it. At this point everything is setup and ready, and you don't need to have the Blender window open.

 You can then run `generate_point_cloud_dataset.py` in your terminal to start generating LIDAR data. The script will step through each frame in the frame range and generate the LIDAR data. Give it the path to the Blender project file and the output directory, like this:

```bash
python generate_point_clouds.py scene.blend --output generated/datasets/example
```

This runs a new instance of Blender in background mode, so even if you have another Blender instance open, it won't interfere with it. The script will print the progress as it goes through the frames.

### Plot LIDAR data

Use `plot_point_cloud.py` to plot the generated LIDAR data. Call the script with the path to the LIDAR data file:

```bash
python plot_point_cloud.py generated/datasets/example/cloud_frames_0_to_0_single.h5py
```

## First time setup

### Blender and Range Scanner

- Install [Blender 3.6 LTI](https://www.blender.org/download/lts/)
- Install the [Blender Range Scanner](https://github.com/ln-12/blainder-range-scanner) addon for blender
- Enable the addon in Blender `preferences -> Addons -> "Range Scanner"`

If you have issues with using the automatic dependency install, try installing the dependencies manually:

- Find the Blender Python executable path in the Blender preferences
  - [Windows] `C:\Program Files\Blender Foundation\Blender 3.6\3.6\python\bin\python.exe`
  - [Mac] `/Applications/Blender.app/Contents/Resources/3.6/python/bin/python3.10`
  - [Linux] `wherever_you_placed_the_blender_folder/3.6/python/bin/python3.10`
- Find the Blender addon folder
  - [Windows] `C:\Users\YOUR_USERNAME\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons`
  - [Mac] `/Users/YOUR_USERNAME/Library/Application\ Support/Blender/3.3/scripts/addons`
  - [Linux] `/home/YOUR_USERNAME/.config/blender/3.6/scripts/addons`
- Finally, install the addon requirements by calling the blender python pip directly
  - `BLENDER_PYTHON_EXECUTABLE -m pip install -r BLENDER_ADDON_FOLDER/range_scanner/requirements.txt`
  - Eg. `C:\Program Files\Blender Foundation\Blender 3.6\3.6\python\bin\python.exe -m pip install -r C:\Users\YOUR_USERNAME\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\range_scanner\requirements.txt`

### Python tools

- Install [Python](https://www.python.org/downloads/) (Tested with 3.12, but should work with 3.8+)
- *[Optional]* Create a virtual environment `python -m venv .venv`. Then activate it:
  - `source .venv/bin/activate` (Linux)
  - `.\.venv\Scripts\activate` (Windows)
- Install the dependencies `pip install -r requirements.txt`

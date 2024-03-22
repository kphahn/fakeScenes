from math import cos, sin
from pathlib import Path
import bpy
import range_scanner
from argparse import ArgumentParser
import os

# ----------------------------------- Setup ---------------------------------- #

if not "FAKESCENE_OUTDIR" in os.environ:
    raise ValueError("FAKESCENE_OUTDIR environment variable not set")

save_dir = Path(os.environ["FAKESCENE_OUTDIR"])

if not save_dir.exists():
    save_dir.mkdir(parents=True)
    (save_dir / "labels").mkdir()
    (save_dir / "pointclouds").mkdir()
print(f"Saving dataset to {save_dir.absolute()}")

start_frame = bpy.context.scene.frame_start
end_frame = bpy.context.scene.frame_end

# ------------------------------ Generate labels ----------------------------- #

blue_cones = [
    obj
    for obj in bpy.data.collections["cone_track"].objects
    if obj.name.startswith("blue_cone.")
]
yellow_cones = [
    obj
    for obj in bpy.data.collections["cone_track"].objects
    if obj.name.startswith("yellow_cone.")
]
big_cones = [
    obj
    for obj in bpy.data.collections["cone_track"].objects
    if obj.name.startswith("big_cone.")
]

for frame in range(start_frame, end_frame):
    bpy.context.scene.frame_set(frame)

    label_data = {"x": [], "y": [], "z": [], "label": []}

    lidar_loc = bpy.context.scene.objects["lidar"].location
    lidar_rot = bpy.context.scene.objects["lidar"].rotation_euler

    for cones, label in [
        (blue_cones, "blue_cone"),
        (yellow_cones, "yellow_cone"),
        (big_cones, "big_cone"),
    ]:
        for cone in cones:
            cone_loc = cone.location
            cone_rot = cone.rotation_euler

            shifted_loc = (
                cone_loc[0] - lidar_loc[0],
                cone_loc[1] - lidar_loc[1],
                cone_loc[2] - lidar_loc[2],
            )
            relative_loc = (
                shifted_loc[0] * cos(-lidar_rot[2])
                - shifted_loc[1] * sin(-lidar_rot[2]),
                shifted_loc[0] * sin(-lidar_rot[2])
                + shifted_loc[1] * cos(-lidar_rot[2]),
                shifted_loc[2],
            )

            label_data["x"].append(relative_loc[0])
            label_data["y"].append(relative_loc[1])
            label_data["z"].append(relative_loc[2])
            label_data["label"].append(label)

    with open(save_dir / "labels" / f"labels_{frame}.csv", "w") as f:
        f.write("x,y,z,label\n")
        for i in range(len(label_data["x"])):
            f.write(
                f"{label_data['x'][i]},{label_data['y'][i]},{label_data['z'][i]},{label_data['label'][i]}\n"
            )

# --------------------------- Generate point clouds -------------------------- #

for frame in range(start_frame, end_frame):
    bpy.context.scene.frame_set(frame)
    lidar = bpy.context.scene.objects["lidar"]
    range_scanner.ui.user_interface.scan_rotating(
        bpy.context,
        # ------------------------------- Lidar Params ------------------------------- #
        scannerObject=lidar,  # Camera object that will act as the LiDAR
        xStepDegree=0.35,  # Horizontal resolution of the LiDAR
        fovX=360,  # Horizontal field of view of the LiDAR
        yStepDegree=0.35,  # Vertical resolution of the LiDAR
        fovY=22.5,  # Vertical field of view of the LiDAR
        rotationsPerSecond=20,
        # ------------------------------ Ray Parameters ------------------------------ #
        reflectivityLower=0.0,
        distanceLower=0.0,
        reflectivityUpper=0.0,
        distanceUpper=99999.9,
        maxReflectionDepth=10,
        # ------------------------------ Animation Params ----------------------------- #
        # Will include LiDAR rotation distortion in the point cloud
        # Tricky to use with existing ipmort script, as the camera speed
        # is one frame per path point. The default framerate in Blender is 24 fps.
        enableAnimation=False,
        frameStart=frame,
        frameEnd=frame,
        frameStep=1,
        frameRate=1,
        # ----------------------------------- Noise ---------------------------------- #
        addNoise=True,
        noiseType="gaussian",
        mu=0.0,
        sigma=0.01,
        noiseAbsoluteOffset=0.0,
        noiseRelativeOffset=0.0,
        # ----------------------------------- Rain ----------------------------------- #
        simulateRain=False,
        rainfallRate=0.0,
        # ------------------------------ Export options ------------------------------ #
        addMesh=False,
        exportLAS=False,
        exportHDF=True,
        exportCSV=False,
        exportPLY=False,
        exportSingleFrames=True,
        dataFilePath=str((save_dir / "pointclouds").absolute()),
        dataFileName="cloud",
        # -------------------------------- Misc/Debug -------------------------------- #
        debugLines=False,
        debugOutput=False,
        outputProgress=True,
        measureTime=False,
        singleRay=False,
        destinationObject=None,
        targetObject=None,
    )

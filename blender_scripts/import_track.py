import bpy
import json
from typing import TypedDict, Callable
from math import atan2, pi
import re
from pathlib import Path

# ---------------------------------------------------------------------------- #
#                                  Parameters                                  #
# ---------------------------------------------------------------------------- #

BLEND_SCENE_PATH = Path(__file__).resolve().parent.parent

# Path to the track data file, must be absolute path
TRACK_DATA_FILE = BLEND_SCENE_PATH / "generated/tracks/track_1.json"

DELETE_OLD_CONES = True
LIDAR_HEIGHT_OVER_CURSOR = 0.7

# Used to drop cones on the ground plane
# If the ground plane is uneven, this value may need to be raised
# to prevent cones from clipping into the ground
CONE_HEIGHT_OFFSET = 1

ADD_CONE_PHYSICS = True
DROP_CONES_ON_GROUND = True

# ---------------------------------------------------------------------------- #

Point2d = tuple[float, float]

class TrackData(TypedDict):
    path: list[Point2d]
    blue_cones: list[Point2d]
    yellow_cones: list[Point2d]
    big_cones: list[Point2d]

def load_track_data(filename: str) -> TrackData:
    with open(filename, "r") as file:
        return json.load(file)

def get_cones_in_scene() -> list[bpy.types.Object]:
    cones = [obj for obj in bpy.data.collections["cone_track"].objects if re.match(r"(?:big|blue|yellow)_cone\.\d+", obj.name)]
    return cones

def populate_world(
        track_data: TrackData,
        add_blue_cone: Callable[[Point2d], None],
        add_yellow_cone: Callable[[Point2d], None],
        add_big_cone: Callable[[Point2d], None],
        set_camera_animation_frame: Callable[[Point2d, float, int], None]
):
    for point in track_data["blue_cones"]:
        add_blue_cone(point)
    for point in track_data["yellow_cones"]:
        add_yellow_cone(point)
    for point in track_data["big_cones"]:
        add_big_cone(point)

    path_pairs = zip(track_data["path"][:-1], track_data["path"][1:])
    xy_direction = [(x0 - x1, y0 - y1) for (x0, y0), (x1, y1) in path_pairs]
    yaw_direction = [atan2(y, x) for (x, y) in xy_direction]
    for i in range(len(yaw_direction)):
        set_camera_animation_frame(track_data["path"][i], yaw_direction[i], i)

try:
    # Reference cone models that will be copied to populate the track
    blue_cone : bpy.types.Object = bpy.context.scene.objects["blue_cone"]
    yellow_cone : bpy.types.Object = bpy.context.scene.objects["yellow_cone"]
    big_cone : bpy.types.Object = bpy.context.scene.objects["big_cone"]

    # Ground plane to drop cones on
    ground : bpy.types.Object = bpy.context.scene.objects["ground"]

    # Camera object that will act as the LiDAR
    camera: bpy.types.Camera = bpy.context.scene.objects["lidar"]

except KeyError as e:
    print(f"Object {e} not found in scene.")
    raise e

cursor_loc = bpy.context.scene.cursor.location
track = load_track_data(TRACK_DATA_FILE)

def add_blue_cone(point: Point2d):
    new_cone = blue_cone.copy()
    new_cone.location = (point[0] + cursor_loc[0], point[1] + cursor_loc[1], cursor_loc[2] + CONE_HEIGHT_OFFSET)
    bpy.data.collections["cone_track"].objects.link(new_cone)

def add_yellow_cone(point: Point2d):
    new_cone = yellow_cone.copy()
    new_cone.location = (point[0] + cursor_loc[0], point[1] + cursor_loc[1], cursor_loc[2] + CONE_HEIGHT_OFFSET)
    bpy.data.collections["cone_track"].objects.link(new_cone)

def add_big_cone(point: Point2d):
    new_cone = big_cone.copy()
    new_cone.location = (point[0] + cursor_loc[0], point[1] + cursor_loc[1], cursor_loc[2] + CONE_HEIGHT_OFFSET)
    bpy.data.collections["cone_track"].objects.link(new_cone)

def set_camera_animation_frame(point: Point2d, yaw: float, frame: int):
    camera.location = (point[0] + cursor_loc[0], point[1] + cursor_loc[1], cursor_loc[2] + LIDAR_HEIGHT_OVER_CURSOR)
    camera.rotation_euler = (pi / 2, 0, yaw + pi / 2)
    camera.keyframe_insert(data_path="location", frame=frame)
    camera.keyframe_insert(data_path="rotation_euler", frame=frame)

if DELETE_OLD_CONES:
    for cone in get_cones_in_scene():
        bpy.data.objects.remove(cone)

if sum([len(track["big_cones"]), len(track["blue_cones"]), len(track["yellow_cones"])]) == 0:
    print("No cones to place on track.")
    exit(0)

populate_world(
    track,
    add_blue_cone,
    add_yellow_cone,
    add_big_cone,
    set_camera_animation_frame
)
bpy.ops.object.select_all(action="DESELECT")

if ADD_CONE_PHYSICS:
    cones = get_cones_in_scene()

    first_cone = cones[0]
    bpy.context.view_layer.objects.active = first_cone
    bpy.ops.rigidbody.object_add()
    first_cone.rigid_body.type = "ACTIVE"
    first_cone.rigid_body.collision_shape = "CONVEX_HULL"
    first_cone.rigid_body.friction = 1.0
    first_cone.rigid_body.restitution = 0.5
    first_cone.rigid_body.linear_damping = 0.1
    first_cone.rigid_body.angular_damping = 0.1
    first_cone.rigid_body.collision_margin = 0.0

    for cone in cones[1:]:
        cone.select_set(True)
    bpy.ops.rigidbody.object_settings_copy()

    bpy.context.view_layer.objects.active = ground
    bpy.ops.rigidbody.object_add()
    ground.rigid_body.type = "PASSIVE"
    ground.rigid_body.collision_shape = "MESH"
    ground.rigid_body.friction = 1.0
    ground.rigid_body.restitution = 0.5
    ground.rigid_body.linear_damping = 0.1
    ground.rigid_body.angular_damping = 0.1
    ground.rigid_body.collision_margin = 0.0
    bpy.ops.object.select_all(action="DESELECT")

    if DROP_CONES_ON_GROUND:
        bpy.context.scene.rigidbody_world.point_cache.frame_start = 0
        bpy.context.scene.rigidbody_world.point_cache.frame_end = 200
        bpy.ops.ptcache.free_bake_all()
        bpy.ops.ptcache.bake_all(bake=True)
        bpy.context.scene.frame_set(200)

        bpy.ops.object.select_all(action="DESELECT")
        for cone in cones:
            cone.select_set(True)
        bpy.ops.object.visual_transform_apply()

        ground.select_set(True)

        bpy.ops.rigidbody.objects_remove()
        bpy.ops.ptcache.free_bake_all()
        bpy.ops.object.select_all(action="DESELECT")

bpy.context.scene.frame_set(0)
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = len(track["path"]) - 1

from pathlib import Path
from subprocess import run
from argparse import ArgumentParser
import os

if os.name == "nt":
    BLENDER_PATH = "C:/Program Files/Blender Foundation/Blender 3.6/blender.exe"
elif os.name == "posix":
    BLENDER_PATH = "/Applications/Blender.app/Contents/Resources/3.6/python/bin/python3.10"
else:
    BLENDER_PATH = None

if BLENDER_PATH is None or not Path(BLENDER_PATH).exists():
    raise ValueError("Blender executable not found. Please set the BLENDER_PATH variable in the script.")

parser = ArgumentParser()
parser.add_argument("scene", type=Path, help="Path to the scene file")
parser.add_argument("-o", "--output", type=Path, help="Directory to save the dataset to", required=True)
args = parser.parse_args()

scene_path = "scene.blend"

env_vars = os.environ.copy()
env_vars["FAKESCENE_OUTDIR"] = str(args.output.absolute())

result = run(
    args=[
        BLENDER_PATH,
        "--debug",
        "--background",
        scene_path,
        "--python",
        "blender_scripts/run_range_scanner.py",
    ],
    env=env_vars,
)

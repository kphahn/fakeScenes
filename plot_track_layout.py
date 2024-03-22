from argparse import ArgumentParser
import json
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_track_layout(track_file: Path, output: Path | None = None):
    if not track_file.exists():
        raise FileNotFoundError(f"Error: {track_file} does not exist")

    with open(track_file, "r") as file:
        track = json.load(file)

    df = pd.DataFrame(
        {
            "x": [
                point[0]
                for point in track["big_cones"]
                + track["blue_cones"]
                + track["yellow_cones"]
            ],
            "y": [
                point[1]
                for point in track["big_cones"]
                + track["blue_cones"]
                + track["yellow_cones"]
            ],
            "color": (
                ["orange"] * len(track["big_cones"])
                + ["blue"] * len(track["blue_cones"])
                + ["yellow"] * len(track["yellow_cones"])
            ),
        }
    )

    fig = px.scatter(
        df,
        x="x",
        y="y",
        color="color",
        color_discrete_map={"orange": "#FF7300", "blue": "#002FFF", "yellow": "#E6D600"},
        size=[7] * len(df),
        size_max=7,
        template="plotly_dark"
    )

    fig.add_trace(
        go.Scatter(
            x=[point[0] for point in track["path"]],
            y=[point[1] for point in track["path"]],
            mode="lines",
            line=dict(color="white", width=2),
        )
    )
    fig.update_layout(yaxis_scaleanchor="x", xaxis_scaleanchor="y", showlegend=False, width=800, height=800)

    if output:
        if output.is_dir():
            output = output / track_file.with_suffix(".png").name

        fig.write_image(str(output))
        print(f"Track layout saved to {output}")
    else:
        fig.show()

def main():
    parser = ArgumentParser()
    parser.add_argument("track_file", type=Path, help="Path to the track.json file")
    parser.add_argument("-o", "--output", type=Path, help="Path to the output image file", default=None)
    args = parser.parse_args()

    plot_track_layout(args.track_file, output=args.output)

if __name__ == "__main__":
    main()
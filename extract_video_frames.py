# Extracts all unextracted MP4 videos in the folder dataset/ into frames
# Written by ChatGPT and James De Ricco

import argparse
from datetime import datetime, timezone
import os
import subprocess
import re


def extract_frames(video_path, frame_filename_ffmpeg_format_string: str):
    # Get the base name of the video (without extension)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    # Create an output folder of the same name as the video
    output_folder = os.path.join(os.path.dirname(video_path), base_name)

    # Check if the output folder already exists
    if not os.path.exists(output_folder):
        # Create the output folder
        os.makedirs(output_folder)
        # Define the command to extract frames using ffmpeg
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            video_path,  # Input video
            "-vf",
            "fps=3,scale=-1:224,crop=224:224",  # Decrease FPS, scale down widescreen video, then evenly crop the left and right sides
            os.path.join(
                output_folder, frame_filename_ffmpeg_format_string
            ),  # Output frames as PNG
        ]

        # Run the ffmpeg command
        print(f"Extracting frames from {video_path} to {output_folder}")
        subprocess.run(ffmpeg_command)
    else:
        print(f"Skipping {video_path}, frames already extracted.")


def recursive_search_and_extract(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(".mp4"):
                video_path = os.path.join(dirpath, filename)
                print(f"video_path: {video_path}")

                # identify label from the video parent folder name
                label = os.path.basename(os.path.normpath(dirpath))

                # parse video filename for videodate, videotime
                d = video_datetime_utc_from_video_filename(filename)

                frame_filename_format = f"frame_label-{label}_time-utc-{d.strftime('%Y-%m-%dT%H-%M-%S')}_number-%04d.png"
                print(frame_filename_format)

                extract_frames(video_path, frame_filename_format)


def video_datetime_utc_from_video_filename(filename):
    # jamescdericco_ivuu11AC2018002F4E192D9_2024-09-24_motion-01e02307-1727201642435_1727201642435.mp4
    start_timestamp = int(re.findall(r"\d+", filename)[-2]) / 1e3
    return datetime.fromtimestamp(start_timestamp).astimezone(timezone.utc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract frames from MP4 videos in a given directory."
    )
    parser.add_argument(
        "root_directory", help="The root directory to search for MP4 videos."
    )
    args = parser.parse_args()

    if os.path.isdir(args.root_directory):
        recursive_search_and_extract(args.root_directory)
    else:
        print(f"{args.root_directory} is not a valid directory.")

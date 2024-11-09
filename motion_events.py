# written by James De Ricco and ChatGPT

import argparse
from datetime import datetime, timedelta
import os
import re


# Frame Filename Format: 'frame_time-utc-2024-11-09T14-24-07_prediction-empty_confidence-percent-99.png'
# Deprecated unsupported format: 'frame_time-2024-10-02T15-54-54_prediction-jacky_confidencepercent-33.png'
def parse_frame_time(frame_filename: str) -> datetime:
    """
    Parse the timestamp in the frame filename and return a datetime object.
    """

    pattern = r"time-utc-(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})"
    match = re.search(pattern, frame_filename)

    if match is None:
        raise SyntaxError(
            f"Failed to parse '{frame_filename}'. It does not match the pattern '{pattern}'."
        )

    time_part = match.groups()[0]
    return datetime.strptime(time_part, "%Y-%m-%dT%H-%M-%S")


def parse_frame_time_from_path(frame_path: str) -> datetime:
    return parse_frame_time(os.path.basename(frame_path))


def group_frame_files_by_motion_event(frame_files: list[str]) -> list[list[str]]:
    """
    Return a list of motion events, which are lists of frames that are three or less seconds apart.
    """
    frame_files.sort(key=lambda f: parse_frame_time_from_path(f))  # Sort by timestamp
    motion_events = []
    current_event = []

    for frame_file in frame_files:
        frame_time = parse_frame_time_from_path(frame_file)

        if current_event:
            last_frame_time = parse_frame_time_from_path(current_event[-1])
            if (frame_time - last_frame_time) <= timedelta(seconds=3):
                current_event.append(frame_file)
            else:
                motion_events.append(current_event)
                current_event = [frame_file]
        else:
            current_event = [frame_file]

    if current_event:
        motion_events.append(current_event)

    return motion_events


if __name__ == "__main__":
    # Get folder path from the command line
    parser = argparse.ArgumentParser(
        description="Group frame files into motion events based on timestamps."
    )
    parser.add_argument(
        "folder_path", type=str, help="Path to the folder containing frame files"
    )

    args = parser.parse_args()

    # List all files in the folder
    frame_files = [f for f in os.listdir(args.folder_path) if f.endswith(".png")]

    # Group files into motion events
    motion_events = group_frame_files_by_motion_event(frame_files)

    # Print the results
    for i, event in enumerate(motion_events, 1):
        print(f"Motion Event {i}:")
        for frame in event:
            print(f"  {frame}")
        print()

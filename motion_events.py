# written by James De Ricco and ChatGPT

import argparse
from datetime import datetime, timedelta
import os


# Frame Filename Format: 'frame_time-2024-10-02T15-54-54_prediction-jacky_confidencepercent-33.png'
def parse_frame_time(frame_time: str) -> datetime:
    """
    Parse the timestamp in the frame filename and return a datetime object.
    """
    # Extract the timestamp from the filename format: 'frame_time-2024-10-02T15-54-54'
    time_part = frame_time.split("_time-")[-1].split("_prediction-")[0]
    return datetime.strptime(time_part, "%Y-%m-%dT%H-%M-%S")


def group_frame_files_by_motion_event(frame_files: list[str]) -> list[list[str]]:
    """
    Return a list of motion events, which are lists of frames that are three or less seconds apart.
    """
    frame_files.sort(key=lambda f: parse_frame_time(f))  # Sort by timestamp
    motion_events = []
    current_event = []

    for frame_file in frame_files:
        frame_time = parse_frame_time(frame_file)

        if current_event:
            last_frame_time = parse_frame_time(current_event[-1])
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

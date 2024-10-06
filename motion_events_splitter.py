import argparse
import os
import shutil
import random
from motion_events import group_frame_files_by_motion_event


def split_items(
    items: list, ratio=0.8, group_func=lambda files: [[f] for f in files]
) -> tuple[list, list]:
    """Splits the list of items into two lists according to the given ratio of left to right items.

    group_func: if specified, keep items in the same group together
    """
    groups = group_func(items)
    left_items = []
    right_items = []

    for group in groups:
        if random.random() < ratio:
            left_items.extend(group)
        else:
            right_items.extend(group)

    return left_items, right_items


def move_files(file_list, destination_directory, dry_run=False):
    """Moves the files from the list to the specified destination directory."""
    if dry_run:
        print(f"mkdir {destination_directory}")
    else:
        os.makedirs(destination_directory, exist_ok=True)

    for file_path in file_list:
        if dry_run:
            print(f"mv {file_path} {destination_directory}")
        else:
            shutil.move(file_path, destination_directory)


def main():
    parser = argparse.ArgumentParser(
        description="Moves files into one of two randomly selected directories according to the given ratio"
    )
    parser.add_argument(
        "source_directory",
        type=str,
        help="Directory with files to be added to the dataset",
    )
    parser.add_argument(
        "train_directory",
        type=str,
        help="Destination for training files",
    )
    parser.add_argument(
        "valid_directory",
        type=str,
        help="Destination for validation files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If specified, no files will be moved. Only display what would happen.",
    )

    args = parser.parse_args()

    # Get all frame .png files from the source directory
    frame_files = [
        os.path.join(args.source_directory, f)
        for f in os.listdir(args.source_directory)
        if f.endswith(".png")
    ]

    # Split into train and valid sets
    train_files, valid_files = split_items(
        frame_files, ratio=0.8, group_func=group_frame_files_by_motion_event
    )

    # Move files to train/ and valid/ directories
    train_dir = args.train_directory
    valid_dir = args.valid_directory

    move_files(train_files, train_dir, dry_run=args.dry_run)
    move_files(valid_files, valid_dir, dry_run=args.dry_run)

    print(f"Moved {len(train_files)} files to {train_dir}")
    print(f"Moved {len(valid_files)} files to {valid_dir}")


if __name__ == "__main__":
    main()

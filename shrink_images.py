import argparse
import os
from PIL import Image

MODEL_INPUT_SIZE = 224 # pixels, length of one axis of the model input tensor

def shrink_image(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        width, height = img.size
        
        # Only shrink images bigger than MODEL_INPUT_SIZE by MODEL_INPUT_SIZE in both dimensions
        if max(width, height) > MODEL_INPUT_SIZE and min(width, height) >= MODEL_INPUT_SIZE:
            # Resize the image with scaling down and cropping to the 1:1 aspect ratio

            crop_size = min(width, height)

            src_top_left_x = int((width - crop_size) / 2)
            src_top_left_y = int((height - crop_size) / 2)
            src_bottom_right_x = src_top_left_x + crop_size
            src_bottom_right_y = src_top_left_y + crop_size

            dest_size = (MODEL_INPUT_SIZE, MODEL_INPUT_SIZE)
            src_box = (src_top_left_x, src_top_left_y, src_bottom_right_x, src_bottom_right_y)
            img_resized = img.resize(dest_size, Image.Resampling.BICUBIC, src_box)
            
            # Save the image back to the original path
            img_resized.save(image_path)
            print(f"Shrank {image_path} to {MODEL_INPUT_SIZE}x{MODEL_INPUT_SIZE}")
        elif width == MODEL_INPUT_SIZE and height == MODEL_INPUT_SIZE:
            print(f"Skipped {image_path}, already {MODEL_INPUT_SIZE}x{MODEL_INPUT_SIZE} px")
        else:
            print(f'Image {image_path} is too small at {width}x{height}. Resizing images smaller than {MODEL_INPUT_SIZE} px in width or height is not supported.')

def recursive_search_and_scale(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.png'):
                image_path = os.path.join(dirpath, filename)
                shrink_image(image_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reduce the size of .png images to the model input tensor dimensions adjusting aspect ratio with center-cropping.')
    parser.add_argument('root_directory', help='The root directory to search for PNG images.')
    args = parser.parse_args()
    
    if os.path.isdir(args.root_directory):
        recursive_search_and_scale(args.root_directory)
    else:
        print(f"{args.root_directory} is not a valid directory.")

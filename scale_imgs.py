import argparse
import os
from PIL import Image

MODEL_INPUT_SIZE = 224 # pixels, length of one axis of the model input tensor

def scale_image(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        width, height = img.size
        
        # Only scale down if the all dimensions are greater than MODEL_INPUT_SIZE pixels
        if min(width, height) > MODEL_INPUT_SIZE:
            # Calculate the new dimensions while maintaining aspect ratio
            new_width, new_height = (MODEL_INPUT_SIZE, int(height / width * MODEL_INPUT_SIZE)) if width < height else (int(width / height * MODEL_INPUT_SIZE), MODEL_INPUT_SIZE)

            # Resize the image
            img_resized = img.resize((new_width, new_height))
            
            # Save the image back to the original path
            img_resized.save(image_path)
            print(f"Scaled {image_path} to {new_width}x{new_height}")
        else:
            print(f"Skipped {image_path}, width or height is already <= {MODEL_INPUT_SIZE} px")

def recursive_search_and_scale(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.png'):
                image_path = os.path.join(dirpath, filename)
                scale_image(image_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scale down all .png image files to closer to the ML model input tensor shape.')
    parser.add_argument('root_directory', help='The root directory to search for PNG images.')
    args = parser.parse_args()
    
    if os.path.isdir(args.root_directory):
        recursive_search_and_scale(args.root_directory)
    else:
        print(f"{args.root_directory} is not a valid directory.")

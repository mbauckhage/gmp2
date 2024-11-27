import os
import json
import logging
import numpy as np
from PIL import Image
from tqdm import tqdm
from skimage.util import view_as_windows



def save_tiling_info(num_x_tiles, num_y_tiles, output_png_path):
    
    tile_info = {
        "num_x_tiles": num_x_tiles,
        "num_y_tiles": num_y_tiles
    }
    json_output_path = os.path.join(output_png_path, '_tile_info.json')
    
    
    with open(json_output_path, 'w') as json_file:
        json.dump(tile_info, json_file)

    logging.info(f"Tile information saved to '{json_output_path}'")
    
    
    
def save_tiles(tiles, output_dir, num_x_tiles, num_y_tiles):
    """
    Saves the tiles with filenames indicating their x and y indices.
    
    Parameters:
    - tiles (list): List of tiles as numpy arrays.
    - output_dir (str): Directory where tiles will be saved.
    - num_x_tiles (int): Number of tiles in the x direction.
    - num_y_tiles (int): Number of tiles in the y direction.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    index = 0
    
            
    for y in range(num_y_tiles):
        for x in range(num_x_tiles):
            tile_image = Image.fromarray(tiles[index])  # Convert numpy array to PIL Image
            
            # If the image is in floating point format, convert it to uint8 (or uint16)
            if tile_image.mode == 'F':
                tile_image = tile_image.convert('I')  # 'I' is for 32-bit integer, or you can convert to 'L' for 8-bit grayscale
            
            tile_path = os.path.join(output_dir, f'tile_{x}_{y}.png')  # Generate filename with x and y indices
            tile_image.save(tile_path)  # Save the image as PNG
            index += 1


import numpy as np
from PIL import Image
from skimage.util import view_as_windows

def generate_tiling(image_path, w_size, overlap=True, custom_overlap=None, normalize=False):
    """
    Generates tiled sub-images from a given image with specified window size and overlap.
    
    Parameters:
    - image_path (str): Path to the input image.
    - w_size (int): Size of the window (width and height in pixels).
    - overlap (bool): If True, tiles will overlap with a default step size of half the window size.
    - custom_overlap (int or None): Specific number of pixels for overlap. Overrides the default overlap behavior.
    - normalize (bool): If True, normalize the image to 0-255.

    Returns:
    - tiles_lst (list): List of tiles as numpy arrays.
    - num_x_tiles (int): Number of tiles in the x direction.
    - num_y_tiles (int): Number of tiles in the y direction.
    """
    win_size = w_size
    in_img = np.array(Image.open(image_path))
    
    # Normalize the image to 0-255 if specified
    if normalize: 
        in_img = ((in_img - in_img.min()) / (in_img.max() - in_img.min()) * 255).astype(np.uint8)
    
    # Calculate the necessary padding to make the image dimensions multiples of the window size
    img_height, img_width = in_img.shape[:2]
    pad_y = (win_size - img_height % win_size) % win_size  # Padding for height
    pad_x = (win_size - img_width % win_size) % win_size   # Padding for width
    
    # Add black (zero) padding to the right and bottom if necessary
    padded_img = np.pad(in_img, ((0, pad_y), (0, pad_x), (0, 0)) if len(in_img.shape) == 3 else ((0, pad_y), (0, pad_x)), 'constant', constant_values=0)
    
    # Now calculate the step size
    if custom_overlap is not None:
        step = win_size - custom_overlap
    elif overlap:
        step = win_size // 2  # Default overlap is half the window size
    else:
        step = win_size

    # Generate tiles using sliding windows
    if len(padded_img.shape) == 2:  # Grayscale image
        tiles = view_as_windows(padded_img, (win_size, win_size), step=step)
    else:  # RGB image
        tiles = view_as_windows(padded_img, (win_size, win_size, 3), step=step)

    # Get the number of tiles in the x and y directions
    num_y_tiles = tiles.shape[0]
    num_x_tiles = tiles.shape[1]

    # Print the number of tiles
    print(f"Number of tiles in y direction: {num_y_tiles}")
    print(f"Number of tiles in x direction: {num_x_tiles}")

    # Create a list of tiles
    tiles_lst = []
    for row in range(tiles.shape[0]):
        for col in range(tiles.shape[1]):
            if len(in_img.shape) == 2:
                tt = tiles[row, col, ...].copy()
            else:
                tt = tiles[row, col, 0, ...].copy()
            tiles_lst.append(tt)
    
    return tiles_lst, num_x_tiles, num_y_tiles

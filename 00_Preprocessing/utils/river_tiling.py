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




    
def generate_tiling(image_path, w_size, overlap=True, custom_overlap=None,normalize=False):
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
    pad_px = win_size // 2
    in_img = np.array(Image.open(image_path))
    
    # Normalize the image to 0-255
    if normalize: in_img = ((in_img - in_img.min()) / (in_img.max() - in_img.min()) * 255).astype(np.uint8)
    
    
    if custom_overlap is not None:
        step = win_size - custom_overlap
    elif overlap:
        step = pad_px
    else:
        step = win_size

    if len(in_img.shape) == 2:
        img_pad = np.pad(in_img, [(pad_px, pad_px), (pad_px, pad_px)], 'edge')
        tiles = view_as_windows(img_pad, (win_size, win_size), step=step)
    else:
        img_pad = np.pad(in_img, [(pad_px, pad_px), (pad_px, pad_px), (0, 0)], 'edge')
        tiles = view_as_windows(img_pad, (win_size, win_size, 3), step=step)
        
    # Get the number of tiles in the x and y directions
    num_y_tiles = tiles.shape[0]
    num_x_tiles = tiles.shape[1]

    # Print the number of tiles
    print(f"Number of tiles in y direction: {num_y_tiles}")
    print(f"Number of tiles in x direction: {num_x_tiles}")


    tiles_lst = []
    for row in range(tiles.shape[0]):
        for col in range(tiles.shape[1]):
            if len(in_img.shape) == 2:
                tt = tiles[row, col, ...].copy()
            else:
                tt = tiles[row, col, 0, ...].copy()
            tiles_lst.append(tt)
    return tiles_lst, num_x_tiles, num_y_tiles
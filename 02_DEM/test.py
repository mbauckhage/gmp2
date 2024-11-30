from utils.dem import subtract_rasters_based_on_coordinates
from utils.raster_interpolation import *
from utils.general_functions import *
import os
from tqdm import tqdm
import logging
from datetime import datetime




base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"



input_dir = "03_resampled/"
output_dir = "04_annoations_squared/"

ensure_directory_exists(os.path.join(base_path, output_dir))


for root, dirs, files in os.walk(os.path.join(base_path, input_dir)):
    for file in files:
        if file.endswith(".tif") and 'map' not in file:
            input = os.path.join(root, file)
            convert_tif_to_png(input, input.replace('.tif', '.png'))
            input_img_path = input.replace(".tif", ".png")
            output_img_path = os.path.join(base_path, output_dir, file.replace('.tif', '_squared.png').replace('stiched_', '').replace('clipped_', ''))
            make_img_square(input_img_path, output_img_path, method="min", align="center")


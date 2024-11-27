
import os
import logging
from datetime import datetime
from utils.general_functions import ensure_directory_exists, clean_logs
from utils.river_tiling import *
import json

# Define paths and parameters
# -----------------------------------------------

date_time = datetime.now().strftime('%Y%m%d_%H%M%S')

#input_raster = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Data/processed_data/stiched_river_1975_clipped.tif"

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_dir = "03_resampled/"
output_dir = "06_river_tiles/"

#output_png_path = f"/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Data/processed_data/annotations/rivers/river_tiles_{date_time}/"

years = [1899] # 1899,1912,1930,1939,1975
hydrology_annotations = ["river","lake","stream"]
img_formats = ['png']

custom_overlap = 0 # number of pixels to overlap
# -----------------------------------------------


# -----------------------------------------------

input_raster = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/01_Segmentation/data/Siegfried.tif"
output_png_path = "/Volumes/T7 Shield/GMP_Data/processed_data/06_river_tiles/test/"
ensure_directory_exists(output_png_path)
            

tiles, num_x_tiles, num_y_tiles = generate_tiling(input_raster, w_size=1000, overlap=False,custom_overlap=custom_overlap, normalize=True)
save_tiles(tiles, output_png_path,num_x_tiles, num_y_tiles)
save_tiling_info(num_x_tiles, num_y_tiles,output_png_path)



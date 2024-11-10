from utils.dem import *
import os
import logging
from datetime import datetime
from utils.general_functions import ensure_directory_exists, clean_logs, save_tiling_info
import json

# Define paths and parameters
# -----------------------------------------------

date_time = datetime.now().strftime('%Y%m%d_%H%M%S')

input_raster = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Data/processed_data/stiched_river_1975_clipped.tif"
output_png_path = f"/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Data/processed_data/annotations/rivers/river_tiles_{date_time}/"


img_formats = ['png']
# -----------------------------------------------






# Setup logging
# -----------------------------------------------
log_directory = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/logs/preprocessing/"
ensure_directory_exists(log_directory)
log_file = os.path.join(log_directory, f"preprocessing_{date_time}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


# run functions
# -----------------------------------------------


for img_format in img_formats:
    logging.info(f"Creating tiles for format '{img_format}'")
    output_png_path_ = output_png_path + img_format + '/'

    ensure_directory_exists(output_png_path)


    tiles, num_x_tiles, num_y_tiles = generate_tiling(input_raster, w_size=300, overlap=False, normalize=True)
    save_tiles(tiles, output_png_path)
    save_tiling_info(num_x_tiles, num_y_tiles,output_png_path)


    
clean_logs(log_directory)
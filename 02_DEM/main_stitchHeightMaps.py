from utils.dem import *
import os
import logging
from datetime import datetime
from utils.general_functions import ensure_directory_exists, clean_logs
import rasterio


# Define paths and parameters
# -----------------------------------------------
tile_dir = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Transfer/tiles_height_map_old_national_1975_20241031_153817/HeightMaps_crs_fix_flip"
output_image_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/final_dem_1975_overlap.png"

# original file name for extent
original_map_file = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/01_Segmentation/data/Siegfried.tif"

filename_starts_with= 'updated_tile'
#filename_starts_with= 'tile'


# Get list of all files in the tile directory
tile_files = os.listdir(tile_dir)



# Setup logging
# -----------------------------------------------
log_directory = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/logs/dem/"
#log_directory = "D:\\mbauckhage\\gmp2"
ensure_directory_exists(log_directory)
log_file = os.path.join(log_directory, f"preprocessing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
    


with rasterio.open(original_map_file) as src:
    original_width = src.width
    original_height = src.height


stitch_tiles_test(tile_dir, output_image_path,original_width, original_height, filename_starts_with=filename_starts_with)

clean_logs(log_directory)
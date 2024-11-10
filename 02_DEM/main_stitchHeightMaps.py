from utils.dem import *
import os
import logging
from datetime import datetime
from utils.general_functions import ensure_directory_exists, clean_logs
import rasterio


# Define paths and parameters
# -----------------------------------------------
tile_dir = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/tiles_height_map_old_national_1975_20241107_174806/heightMaps_flip"
output_image_path = f"/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/final_dem_1975__{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

# original file name for extent
original_map_file = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/height_map_old_national_1975.png"

filename_starts_with= 'updated_tile'
#filename_starts_with= 'tile'

extent_extract = True
left, right,upper, lower = 0, 4000, 0000, 4000


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



# Read the tiles back into a list of arrays
tiles_from_files = read_tiles(tile_dir)

logging.info(f"Number of tiles: {len(tiles_from_files)}")

# Check the shape of the first tile
if tiles_from_files:
    print(f"First tile shape: {tiles_from_files[0].shape}")

tiles_array = np.array(tiles_from_files)
test_pred_dict = {i: tiles_from_files[i] for i in range(len(tiles_array))}

reconstructed_image = reconstruct_tiling(original_map_file, test_pred_dict, output_image_path, w_size=512)


if extent_extract:
    output_cropped_png_path = output_image_path.split('.')[0] + '_cropped.png'
    extract_extent(output_image_path, output_cropped_png_path, left, upper, right, lower)

clean_logs(log_directory)
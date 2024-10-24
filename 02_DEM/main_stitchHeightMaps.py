from utils.dem import *
import os
import logging
from datetime import datetime
from utils.general_functions import ensure_directory_exists


input_geojson_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/01_Segmentation/output/old_national_1975_skeleton.geojson"
output_tiff_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/height_map_old_national_1975.png"
output_tiff_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Transfer/stitched_rivers_1975_clipped.tif"
output_png_path = "output/"


#min_height = get_min_height_from_geojson(input_geojson_path)

#print(min_height)
#geojson_to_tiff(input_geojson_path, output_tiff_path,resolution=0.1, input_crs='EPSG:2056', height_attribute='hoehe')
#geojson_to_png_tiles(input_geojson_path, output_png_path,resolution=0.1, input_crs='EPSG:2056', height_attribute='hoehe',min_nonzero_value=min_height)


import os
import rasterio

tile_dir = "D:\\mbauckhage\\gmp2\\00_Transfer\\tiles_height_map_old_national_1975_processed_241024"
output_image_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Data/processed_data/height_map_from_tiles.png"

filename_starts_with= 'height_map_tile'


# Get list of all files in the tile directory
tile_files = os.listdir(tile_dir)



# Setup logging
# -----------------------------------------------
log_directory = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/logs/dem/"
log_directory = "D:\\mbauckhage\\gmp2"
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
    
"""tile_coords = [tuple(map(int, f.split('.')[0].split('_')[1:])) for f in tile_files if f.startswith('tile')]

# Calculate the number of tiles in x and y directions
num_tiles_x = max(x for _, x in tile_coords) + 1
num_tiles_y = max(y for y, _ in tile_coords) + 1

print(num_tiles_x)
print(num_tiles_y)"""

with rasterio.open(output_tiff_path) as src:
    original_width = src.width
    original_height = src.height


stitch_tiles(tile_dir, output_image_path,original_width, original_height, filename_starts_with=filename_starts_with)


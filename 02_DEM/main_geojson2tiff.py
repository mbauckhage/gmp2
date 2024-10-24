from utils.dem import *
import os
import logging
from datetime import datetime
from utils.general_functions import ensure_directory_exists

# Define paths and parameters
# -----------------------------------------------
input_geojson_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/01_Segmentation/output/old_national_1975_skeleton.geojson"
output_tiff_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/height_map_old_national_1975.png"
output_png_path = f"02_DEM/output/tiles_{output_tiff_path.split('/')[-1].split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}/"
height_attribute = "height"
# -----------------------------------------------






# Setup logging
# -----------------------------------------------
log_directory = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/logs/dem/"
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


# run functions
# -----------------------------------------------
min_height = get_min_height_from_geojson(input_geojson_path, height_attribute)
logging.info(f"Minimum height: {min_height}")

ensure_directory_exists(output_png_path)

geojson_to_tiff(input_geojson_path, output_tiff_path,resolution=0.1, input_crs='EPSG:2056', height_attribute=height_attribute)
geojson_to_png_tiles(input_geojson_path, output_png_path,resolution=0.1, input_crs='EPSG:2056', height_attribute=height_attribute,min_nonzero_value=min_height)

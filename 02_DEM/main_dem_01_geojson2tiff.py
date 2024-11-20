from utils.dem import *
import os
import logging
from datetime import datetime
from utils.general_functions import ensure_directory_exists, clean_logs

# Define paths and parameters
# -----------------------------------------------
base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/00_Segmentation/"

#input_geojson_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/01_Segmentation/output/old_national_1975_skeleton.geojson"
#output_tiff_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/height_map_old_national_1975.png"
#output_png_path = f"02_DEM/output/tiles_{output_tiff_path.split('/')[-1].split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}/"
height_attribute = "height"
#input_raster = output_tiff_path
img_formats = ['tif']


years = [1912] # 1899,1912,1930,1939,1975
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

for year in years:
    
    
    input_geojson_path = f"{base_path}/{year}/skeleton_{year}_heights.geojson"
    output_tiff_path = f"{base_path}/{year}/skeleton_{year}_heights.tif"


    for img_format in img_formats:
        #logging.info(f"Creating tiles for format '{img_format}'")
        logging.info(f"Input geojson: {input_geojson_path}")
        
        geojson_to_tiff(input_geojson_path, output_tiff_path,resolution=1, input_crs='EPSG:2056', height_attribute=height_attribute)
        #tiles = generate_tiling(input_raster, w_size=512)
        #save_tiles(tiles, output_png_path)
        
    clean_logs(log_directory)
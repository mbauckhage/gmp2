
import os
import logging
from datetime import datetime
from utils.general_functions import ensure_directory_exists, clean_logs
from utils.river_tiling import *
import json


"""
DEPRECTAED
This script is used to create tiles from the annotated river images.
"""


# Define paths and parameters
# -----------------------------------------------

date_time = datetime.now().strftime('%Y%m%d_%H%M%S')

#input_raster = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Data/processed_data/stiched_river_1975_clipped.tif"

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_dir = "04_annoations_squared/"
output_dir = "06_river_tiles/"

#output_png_path = f"/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Data/processed_data/annotations/rivers/river_tiles_{date_time}/"

years = [1899,1912,1930,1939,1975] # 
hydrology_annotations = ["river","lake","stream"]
img_formats = ['png']

custom_overlap = 1 # number of pixels to overlap
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

for year in years:
    for img_format in img_formats:
        for annotation in hydrology_annotations:
        
            logging.info(f"Creating tiles for format '{img_format}'")
            
            for filename in os.listdir(base_path + input_dir):
                if str(year) in filename and annotation in filename and not filename.startswith("._") and filename.endswith(img_format):
                    
                    logging.info(f"Creating tiles for {filename}")
                    
                    input_raster = base_path + input_dir + filename
                    output_png_path = base_path + output_dir + f"{annotation}_tiles_{year}/"
                    ensure_directory_exists(output_png_path)
            

                    tiles, num_x_tiles, num_y_tiles = generate_tiling(input_raster, w_size=300, overlap=False,custom_overlap=custom_overlap, normalize=True)
                    save_tiles(tiles, output_png_path,num_x_tiles, num_y_tiles)
                    save_tiling_info(num_x_tiles, num_y_tiles,output_png_path)


clean_logs(log_directory)
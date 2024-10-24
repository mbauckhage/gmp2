from utils.general_functions import ensure_directory_exists, clean_logs
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff




# Split channels of tiff file into binary rasters
# -----------------------------------------------
split_channels = False
input_directory = "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/old_national/annotations/hydrology/LKg_1165/"
input_split_files = ["LKg_1165_1959_EN_predictions.tif", "LKg_1165_1975_predictions.tif","LKg_1165_1987_predictions.tif"]
output_split_dir = '/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/'


# Setup logging
# -----------------------------------------------
log_directory = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/logs/preprocessing/"
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

# -----------------------------------------------
# Run the functions
# -----------------------------------------------

if split_channels:
    ensure_directory_exists(output_split_dir)
    
    for file in input_split_files:
        logging.info(f"Splitting channels of {file}")
        input_raster = os.path.join(input_directory, file)
        filename_parts = file.split('_')
        output_filename = '_'.join(filename_parts[:3]) + '.tif'
        save_channel_as_binary(input_raster, output_split_dir,output_filename)
    
   
        
clean_logs(log_directory)
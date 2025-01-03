from utils.general_functions import ensure_directory_exists, clean_logs
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff


"""
This script is used to split the channels of a tiff file into binary rasters.
"""




# Split channels of tiff file into binary rasters
# -----------------------------------------------
split_channels = True
#input_directory = "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/old_national/annotations/hydrology/LKg_1165/"
input_directory = "/Volumes/T7 Shield/GMP_Data/siegfried/annotations/hydrology/"
additional_dirs = ["rgb_TA_315/","rgb_TA_318/","rgb_TA_329/","rgb_TA_332/"]

#input_split_files = ["rgb_TA_315_1930_predictions.tif"]

years = [1899,1904,1912,1930,1939] #   1878, 1975,1987

#output_split_dir = '/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/'
output_split_dir = "/Volumes/T7 Shield/GMP_Data/siegfried/annotations/fixed_hydrology/"
ensure_directory_exists(output_split_dir)


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

    for additional_dir in additional_dirs:
        ensure_directory_exists(output_split_dir+additional_dir)
        for year in years:
            input_split_files = os.listdir(input_directory+additional_dir)
            for file in input_split_files:
                if str(year) in file and not file.startswith("._"):
                    logging.info(f"Splitting channels of {file}")
                    input_raster = os.path.join(input_directory+additional_dir, file)
                    filename_parts = file.split('_')
                    output_filename = '_'.join(filename_parts[:3]) + '_'+str(year) + '.tif'
                    save_channel_as_binary(input_raster, output_split_dir,output_filename)



   
        
clean_logs(log_directory)
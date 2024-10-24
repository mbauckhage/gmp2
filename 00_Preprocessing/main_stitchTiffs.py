from utils.general_functions import ensure_directory_exists, clean_logs
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff



# Stitch the binary rasters together
# -----------------------------------------------
run_stitch_geotiffs = False

base_path = "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/"
base_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/"
folder_path = "00_Data/processed_data/annotations/hydrology/"

tiff_files = [base_path + folder_path + "LKg_1165/LKg_1165_1975/LKg_1165_1975_river_binary.tif",
              base_path + folder_path + "LKg_1166/LKg_1166_1975/LKg_1166_1975_river_binary.tif",
              base_path + folder_path + "LKg_1185/LKg_1185_1975/LKg_1185_1975_river_binary.tif",
              base_path + folder_path + "LKg_1186/LKg_1186_1975/LKg_1186_1975_river_binary.tif"]  
output_path = "00_Data/processed_data/stiched_river_1975.tif"




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

if run_stitch_geotiffs:
    stitch_geotiffs(tiff_files, output_path)
            

        
clean_logs(log_directory)
from utils.general_functions import ensure_directory_exists, clean_logs,ensure_file_exists
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff
from tqdm import tqdm



# Stitch the binary rasters together
# -----------------------------------------------
run_stitch_geotiffs = True

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/00_annotations/"
#base_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/"
folder_paths = ["rivers"]
years = [1956, 1975, 1987]
lkgs = ["LKg_1165","LKg_1166","LKg_1185","LKg_1186"] # "LKg_1165","LKg_1166","LKg_1185","LKg_1186"
additional = "_binary"


output_base_path = f"/Volumes/T7 Shield/GMP_Data/processed_data/01_stiched/"




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

ensure_directory_exists(base_path,create=False)


if run_stitch_geotiffs:
    
    for folder_path in tqdm(folder_paths):
        ensure_directory_exists(base_path+folder_path, create=False)
        for year in years:
            
            tiff_files = []
            for lkg in lkgs:
                ensure_directory_exists(base_path+folder_path+f"/{lkg}",create=False)
                tiff_files.append(f"{base_path}{folder_path}/{lkg}/{lkg}_{year}{additional}.tif")
            
            
            for file in tiff_files:
                ensure_file_exists(file)
            
            output_path = f"{output_base_path}stiched_{folder_path}_{year}.tif"
            stitch_geotiffs(tiff_files, output_path)
   
        
clean_logs(log_directory)
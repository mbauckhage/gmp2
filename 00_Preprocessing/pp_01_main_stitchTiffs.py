from utils.general_functions import ensure_directory_exists, clean_logs,ensure_file_exists
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from tqdm import tqdm



# Stitch the binary rasters together
# -----------------------------------------------
run_stitch_geotiffs = True

base_path = "/Volumes/T7 Shield/GMP_Data/old_national/map_sheets/" #"/Volumes/T7 Shield/GMP_Data/processed_data/"
#base_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/"
folder_paths = ["lake"]
years = [1956] #   ,1899,1904,1912,1930,1939 1975,1987
lkgs = ["LKg_1165","LKg_1166","LKg_1185","LKg_1186"] #  #  "rgb_TA_315","rgb_TA_318","rgb_TA_329","rgb_TA_332" 
additional = "" #"_predictions" #_binary #_black_ms_5_50
assign_crs_to_files = True

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
                if folder_path != "": ensure_directory_exists(base_path+folder_path+f"/{lkg}",create=False)
                else: ensure_directory_exists(base_path+folder_path+f"{lkg}",create=False)
                
                tif_file_path = f"{base_path}{folder_path}/{lkg}/{lkg}_{year}{additional}.tif"
                tif_file_path = tif_file_path.replace("//","/")
                tiff_files.append(tif_file_path)
            
            
            for file in tiff_files:
                file_exists= ensure_file_exists(file, raise_error=False)
                if not file_exists:
                    logging.error(f"File {file} does not exist")
                    tiff_files.remove(file)
                
                
            if assign_crs_to_files:
                # Reproject all files and assign CRS if missing
                corrected_files = [assign_crs(file) for file in tiff_files]
            else:
                corrected_files = tiff_files
            
            output_path = f"{output_base_path}stiched_{folder_path}_{year}.tif"
            stitch_geotiffs(corrected_files, output_path)
   
        
clean_logs(log_directory)
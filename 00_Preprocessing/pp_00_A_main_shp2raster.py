from utils.general_functions import ensure_directory_exists, clean_logs
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff
from tqdm import tqdm

"""
This script is used to convert shapefiles to rasters.
"""



# polygons to raster
# -----------------------------------------------
get_raster_from_shapefiles = True
overwrite = True
resolution = 1  # 0.5 meters per pixel
base_path = "/Volumes/T7 Shield/GMP_Data/"
maps_dir = "siegfried/"
file_dir = f"{maps_dir}annotations/hydrology/"
output_dir_name ="siegfried/"
# -----------------------------------------------



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


    
if get_raster_from_shapefiles:
    for root, dirs, files in tqdm(os.walk(base_path+file_dir)):
        for file in files:
            
            
            
            
            if file.endswith(".shp") and not file.startswith("._"): 
            
                input = os.path.join(root, file)
                output = input.replace(maps_dir,output_dir_name).replace(".shp","_binary.tif")
                output_directory = os.path.dirname(output)
                ensure_directory_exists(output_directory)
                
                filename = os.path.basename(os.path.dirname(output)) + "_"+file.split(".")[0]+".tif"
                output_raster = os.path.join(output_directory, filename)
                logging.info(f"Creating river depth raster from {str(input)}")
                logging.info(f"Output raster: {str(output_raster)}") 
                
                polygons_to_raster(input, output_raster, resolution,overwrite=overwrite)


            else:
                logging.info(f"Skipping file {str(file)}")
        
clean_logs(log_directory)
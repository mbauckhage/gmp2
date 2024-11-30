from utils.general_functions import ensure_directory_exists, clean_logs,ensure_file_exists
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff





# Clip the raster
# -----------------------------------------------
run_clip_geotiff = True


base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/" #"/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_clipping = "01_stiched/" #"map_sheets/" #"01_stiched/" #"/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/03_Terrain/swissimage2.5m_latest.tif"

output_of_clipping =  "02_clipped" #input_for_clipping.replace(".tif","_clipped.tif")
extent =  "../01_Segmentation/data/Siegfried.tif" # Set your extent here, like [0, 0, 0, 0] or filename to calculate extent from


# Setup logging
# -----------------------------------------------
log_directory = "../logs/preprocessing/"
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


if run_clip_geotiff:
    
    output_dir = base_path + output_of_clipping
    ensure_directory_exists(output_dir)
    
    if isinstance(extent, str):
                extent = get_extent_from_tiff(extent)
    
    for file in os.listdir(base_path + input_for_clipping):
        if file.endswith(".tif") and not file.startswith("._"):
            input = base_path + input_for_clipping + file
            output = output_dir + "/" + file.replace(".tif","_clipped.tif")
            
            if ensure_file_exists(output, raise_error=False):
                logging.info(f"File {output} already exists. Skipping.")

            else:
                logging.info(f"Clipping raster {input} to {output}")
                assert len(extent) == 4, "Extent must contain 4 values"
                clip_geotiff(input, output, extent)
            
        
clean_logs(log_directory)
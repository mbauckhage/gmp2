from utils.general_functions import ensure_directory_exists, clean_logs
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff





# Clip the raster
# -----------------------------------------------
run_clip_geotiff = False
input_for_clipping = "00_Data/processed_data/stiched_river_1975.tif"
#input_for_clipping = base_path + "00_Data/processed_data/annotations/hydrology/LKg_1166/LKg_1166_1975/LKg_1166_1975_river.tif"
output_of_clipping = input_for_clipping.replace(".tif","_clipped.tif")
extent =  "01_Segmentation/data/Siegfried.tif" # Set your extent here, like [0, 0, 0, 0] or filename to calculate extent from


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


if run_clip_geotiff:
    logging.info(f"Clipping raster {input_for_clipping} to {output_of_clipping}")
    if isinstance(extent, str):
        extent = get_extent_from_tiff(extent)
    
    assert len(extent) == 4, "Extent must contain 4 values"
    clip_geotiff(input_for_clipping, output_of_clipping, extent)
            
        
clean_logs(log_directory)
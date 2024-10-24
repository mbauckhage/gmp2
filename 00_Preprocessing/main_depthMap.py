from utils.general_functions import ensure_directory_exists, clean_logs
from utils.preprocessing import *
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff






# Create the river depth raster base on tiff
# -----------------------------------------------
create_river_depth_raster = True
based_on_shapefile = False
overwrite = True
max_depth = 3
base_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/"
folder_path = "00_Data/processed_data/"
input_filename = "stiched_river_1975_clipped.tif"
tiff_files = [base_path + folder_path + input_filename]  
output_path = "00_Data/processed_data/river_depth_raster_1975.tif"


# Create the river depth raster base on shape
# -----------------------------------------------
#base_path = "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/"





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

    
if create_river_depth_raster:
    
    if not based_on_shapefile:
        for file in tiff_files:
            logging.info("Input file: ",file)
            output_raster = file.replace(".tif","_depth.tif")
            depth_raster(file,output_raster,max_depth)
    
    if based_on_shapefile:
        for root, dirs, files in os.walk(base_path):
            for file in files:
                
                
                
                
                
                if file.endswith(".shp"):
                    
                    input = os.path.join(root, file)
                    output = input.replace("old_national","processed_data").replace(".shp",".tif")
                    
                    

                    output_directory = os.path.dirname(output)
                    ensure_directory_exists(output_directory)
                    
                    filename = os.path.basename(os.path.dirname(output)) + "_"+file.split(".")[0]+".tif"
                    output_raster = os.path.join(output_directory, filename)
                    logging.info(f"Creating river depth raster from {str(input)}")
                    logging.info(f"Output raster: {str(output_raster)}")
                    #raster_bounds = get_bounding_box_from_shp(river_shapefile)  # Set your raster bounds
        
                    # Create the river depth raster
                    polygons_to_depth_raster(input, output_raster, resolution, max_depth,overwrite=overwrite)


        
clean_logs(log_directory)
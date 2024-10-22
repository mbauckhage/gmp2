from utils.general_functions import ensure_directory_exists, clean_logs
from utils.preprocessing import polygons_to_depth_raster, get_bounding_box_from_shp,save_channel_as_binary, stitch_geotiffs
import os
import logging
from datetime import datetime
from utils.preprocessing import clip_geotiff,get_extent_from_tiff




# Split channels of tiff file into binary rasters
# -----------------------------------------------
split_channels = True
input_directory = "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/old_national/annotations/hydrology/LKg_1165/"
input_split_files = ["LKg_1165_1959_EN_predictions.tif", "LKg_1165_1975_predictions.tif","LKg_1165_1987_predictions.tif"]
output_split_dir = '/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/'


# Create the river depth raster
# -----------------------------------------------
create_river_depth_raster = False
resolution = 0.5  # 0.5 meters per pixel
max_depth = 2.0  # Maximum depth of 2 meters
base_directory = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/00_Data/old_national/annotations/hydrology/"


# Stitch the binary rasters together
# -----------------------------------------------
run_stitch_geotiffs = False
tiff_files = ["/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/LKg_1165/LKg_1165_1975/LKg_1165_1975_river.tif",
              "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/LKg_1166/LKg_1166_1975/LKg_1166_1975_LKg_1166_1975_river.tif", 
              "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/LKg_1185/LKg_1185_1975/LKg_1185_1975_river.tif", 
              "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/LKg_1186/LKg_1186_1975/LKg_1186_1975_river.tif"]  # Add your file paths here
output_path = "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/stitched_output_rivers.tif"

# Clip the raster
# -----------------------------------------------
run_clip_geotiff = False
input_for_clipping = "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/00_Data/processed_data/annotations/hydrology/stitched_rivers_1975.tif"
output_of_clipping = input_for_clipping.replace(".tif","_clipped.tif")
extent =  "/Volumes/Drobo/00 Studium/02_Master/3_Semester/GMP2/01_Segmentation/data/Siegfried.tif" # Set your extent here, like [0, 0, 0, 0] or filename to calculate extent from


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
        input_raster = os.path.join(input_directory, file)
        filename_parts = file.split('_')
        output_filename = '_'.join(filename_parts[:3]) + '.tif'
        save_channel_as_binary(input_raster, output_split_dir,output_filename)
    
    
    
if create_river_depth_raster:
    
    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if file.endswith(".shp"):
                input = os.path.join(root, file)
                output = input.replace("old_national","processed_data").replace(".shp",".tif")

                output_directory = os.path.dirname(output)
                ensure_directory_exists(output_directory)
                
                filename = os.path.basename(os.path.dirname(output)) + "_"+file.split(".")[0]+".tif"
                output_raster = os.path.join(output_directory, filename)
                #raster_bounds = get_bounding_box_from_shp(river_shapefile)  # Set your raster bounds
    
                # Create the river depth raster
                polygons_to_depth_raster(input, output_raster, resolution, max_depth,overwrite=False)

if run_stitch_geotiffs:
    stitch_geotiffs(tiff_files, output_path)
            

if run_clip_geotiff:
    if isinstance(extent, str):
        extent = get_extent_from_tiff(extent)
    
    assert len(extent) == 4, "Extent must contain 4 values"
    clip_geotiff(input_for_clipping, output_of_clipping, extent)
            
        
clean_logs(log_directory)
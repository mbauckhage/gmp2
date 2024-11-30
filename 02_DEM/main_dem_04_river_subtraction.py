from utils.dem import subtract_rasters_based_on_coordinates
from utils.raster_interpolation import *
from utils.general_functions import *
import os
from tqdm import tqdm
import logging
from datetime import datetime




base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"


years = [1899,1912,1930,1939,1975]


# Setup logging
# -----------------------------------------------
log_directory = "../logs/dem/"
ensure_directory_exists(log_directory)
log_file = os.path.join(log_directory, f"dem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)




for year in tqdm(years):
    
    depth_map_paths = []
    
    path_dem = f"{base_path}/05_DEM/dem_resampled/{year}/height_map_{year}.tif"
    
    dir_depth_maps = f"{base_path}/05_DEM/depth_maps_resampled/"
    files = os.listdir(dir_depth_maps)

    for file in files:
        if str(year) in file:
            logging.info(f"Found depth map for year {year}: {file}")
            path_depth_map = os.path.join(dir_depth_maps, file)
            depth_map_paths.append(path_depth_map)
    
    
    for path_depth_map in depth_map_paths:
        ensure_file_exists(path_depth_map, raise_error=False)
    
    
    

    output_dir = f"{base_path}/05_DEM/dem_with_hydrology/"
    ensure_directory_exists(output_dir)
    output_raster_path = f"{output_dir}dem_{year}.tif"
    subtract_rasters_based_on_coordinates(path_dem,depth_map_paths,output_raster_path)


    convert_tif_to_png(output_raster_path, output_raster_path.replace('.tif', '.png'))
    
    
    input_img_path, output_img_path= output_raster_path.replace(".tif",".png"), output_raster_path.replace('.tif', '_squared.png')
    make_img_square(input_img_path, output_img_path,method="min",align="center")
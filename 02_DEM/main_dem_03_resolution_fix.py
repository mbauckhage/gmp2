import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import os
from utils.general_functions import ensure_directory_exists
from utils.resolution_resample import resample_geotiff


base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/05_DEM/"


different_prefixes = ['dem','depth_maps']

for different_prefix in different_prefixes:

    input_for_masking = different_prefix
    
    new_resolution = (1,1)  

    years = [1899,1912,1930,1939,1975]

    for year in years:

        if different_prefix == 'dem': 
            input_folder = f"{base_path}{input_for_masking}/{year}"
            output_folder = f"{base_path}dem_resampled/{year}/"
        else: 
            input_folder = f"{base_path}{input_for_masking}/"
            output_folder = f"{base_path}depth_maps_resampled/"
        
        
        ensure_directory_exists(output_folder)

        for filename in os.listdir(input_folder):
            if filename.endswith(".tif") and not filename.startswith("._"):
                input_geotiff = os.path.join(input_folder, filename)
                output_geotiff = os.path.join(output_folder, filename)
                resample_geotiff(input_geotiff, output_geotiff, new_resolution, target_crs='EPSG:21781')
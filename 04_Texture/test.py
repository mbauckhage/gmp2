import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import os
from utils.preprocessing import ensure_directory_exists
from utils.resolution_resample import resample_geotiff


base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_masking = "05_DEM/dem/"


new_resolution = (0.5, 0.5)  

input_folder = os.path.join(base_path, input_for_masking)
output_folder = os.path.join(base_path, "05_DEM/dem/resampled/")
ensure_directory_exists(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith(".tif") and not filename.startswith("._"):
        input_geotiff = os.path.join(input_folder, filename)
        output_geotiff = os.path.join(output_folder, filename)
        resample_geotiff(input_geotiff, output_geotiff, new_resolution)
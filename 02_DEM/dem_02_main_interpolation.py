from utils.raster_interpolation import * 
from utils.general_functions import *
from tqdm import tqdm



"""
This script interpolates the height map from the skeleton
"""

# File path
# -----------------------------------------------
base_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/"
base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"

input_dir = '00_Segmentation/'
output_dir = '05_DEM/dem/'



years = [1912] # 1899,1912,1930,1939,1975



# -----------------------------------------------

for year in tqdm(years):
    input_raster_path = f"skeleton_{year}_heights.tif"
    output_raster_path = f"height_map_{year}.tif"


    input_raster_path_ = f"{base_path}{input_dir}{year}/{input_raster_path}"
    output_raster_path_ = f"{base_path}{output_dir}{year}/{output_raster_path}"

    ensure_directory_exists(f"{base_path}{output_dir}{year}")


    interpolate_raster(input_raster_path_, output_raster_path_, method='linear')

#make_img_square(output_raster_path_.replace(".tif",".png"), output_raster_path_.replace('.tif', '_squared.png'))
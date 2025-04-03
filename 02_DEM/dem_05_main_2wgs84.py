from utils.raster_interpolation import * 
from utils.general_functions import *
from tqdm import tqdm



# File path
# -----------------------------------------------
base_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/"
base_path = "/Volumes/T7 Shield/GMP2/00_Data/processed_data/"

input_dir = '05_DEM/dem_with_hydrology'
output_dir = '05_DEM/dem_with_hydrology_wgs84'



years = [1899,1912,1930,1939,1975] # 1899,1912,1930,1939,1975



# -----------------------------------------------

for year in tqdm(years):
    
    ensure_directory_exists(f"{base_path}{output_dir}")
    
    input_path = f"{base_path}{input_dir}/dem_{year}.tif"
    output_path = f"{base_path}{output_dir}/dem_{year}_wgs84.tif"
    # Reproject the raster
    reproject_and_clean_raster(input_path, output_path)
from tqdm import tqdm
import os
from utils.preprocessing import *


base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_dir_dem = "05_DEM/dem_with_hydrology/"
input_dir_textures = "04_Textures/"
output_dir = "04_data_for_unity/"


for input_dir in [input_dir_dem, input_dir_textures]:

    input_folder = base_path + input_dir
    for filename in tqdm(os.listdir(input_folder)):
        if filename.endswith(".tif") and not filename.startswith("._"):
            
            year = filename.split("_")[1].split(".")[0]
            source_file = input_folder + filename
            destination_dir = base_path + output_dir + str(year)
            
            if 'texture' in source_file: 
                destination_dir += f"/{year}_Textures/"
                destination_file = os.path.join(destination_dir, "Tile__0__0.tif")
                os.rename(source_file, destination_file)
                
            if 'dem' in source_file:
                destination_file = os.path.join(destination_dir, f"{year}.tif")
                os.rename(source_file, destination_file)
            
            ensure_directory_exists(destination_dir)
            copy_file(source_file, destination_dir)
            


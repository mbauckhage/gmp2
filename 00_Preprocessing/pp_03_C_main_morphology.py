import os
from utils.preprocessing import ensure_directory_exists, fill_and_connect_surfaces

"""
This script is used to fill holes in the annotated river images.
"""

# Define paths and parameters
# -----------------------------------------------
base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_masking = "02_clipped/"
output_dir = "03_filled_holes/"
new_resolution = (1, 1)  
annotations = ["rivers"]
# -----------------------------------------------


input_folder = os.path.join(base_path, input_for_masking)
output_folder = os.path.join(base_path, output_dir)
ensure_directory_exists(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith(".tif") and not filename.startswith("._") and filename.split("_")[1] in annotations:
        input_geotiff = os.path.join(input_folder, filename)
        output_geotiff = os.path.join(output_folder, filename)
        fill_and_connect_surfaces(input_geotiff, output_geotiff)




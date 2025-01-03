from tqdm import tqdm
from utils.preprocessing import *


"""
This file is used to convert the binary raster files to shapefiles. 
If file exists in the `03_filled_holes` folder, it will be used.
Otherwise, the file in the `02_clipped` folder will be used. 
The output will be saved in the `03_vector_data` folder.
"""

# Define paths and parameters
# -----------------------------------------------

epsg_code=21781

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_filled_holes = "03_filled_holes/"
input_clipped = "02_clipped/"
output_dir = "03_vector_data/"

annotations = {
    "buildings": {
        'tolerance': 2
    },
    "lake": {
        'tolerance': 3
    },
    "rivers": {
        'tolerance': 3
    },
    "vegetation": {
        'tolerance': 5
    },
     "roads": {
        'tolerance': 0.5
    },
}

# -----------------------------------------------



output_folder = os.path.join(base_path, output_dir)
ensure_directory_exists(output_folder)

filled_holes_folder = os.path.join(base_path, input_filled_holes)
clipped_folder = os.path.join(base_path, input_clipped)

for filename in tqdm(os.listdir(clipped_folder)):  # Use the clipped folder as the main file list
    if filename.endswith(".tif") and not filename.startswith("._"):
        
        # Check if the file is available in `03_filled_holes`
        filled_holes_path = os.path.join(filled_holes_folder, filename)
        clipped_path = os.path.join(clipped_folder, filename)
        
        # Select the input file (prioritize filled holes)
        input_geotiff = filled_holes_path if os.path.exists(filled_holes_path) else clipped_path
        
        new_file_name = filename.replace("_clipped", "").replace(".tif", ".shp").replace("stiched_", "")
        annotation = new_file_name.split("_")[0]
        
        if annotation not in annotations.keys(): 
            continue
        
        ensure_directory_exists(os.path.join(output_folder, annotation), print_info=False)
        
        output_shapefile_path = os.path.join(output_folder, annotation, new_file_name)
        
        tolerance = annotations[annotation]['tolerance']

        # Call the binary raster to shapefile function
        binary_raster_to_shp(input_geotiff, output_shapefile_path, epsg_code, tolerance)
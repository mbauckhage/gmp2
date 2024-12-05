from tqdm import tqdm
from utils.preprocessing import *

epsg_code=21781

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_conversion = "02_clipped/"

"""
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
}"""

annotations = {
    "vegetation": {
        'tolerance': 5
    }
}


input_folder = os.path.join(base_path, input_for_conversion)
output_folder = os.path.join(base_path, "03_vector_data/")
ensure_directory_exists(output_folder)

for filename in tqdm(os.listdir(input_folder)):
    if filename.endswith(".tif") and not filename.startswith("._"):
        
        
        input_geotiff = os.path.join(input_folder, filename)
        
        new_file_name = filename.replace("_clipped","").replace(".tif",".shp").replace("stiched_","")
        annotation = new_file_name.split("_")[0]
        
        if annotation not in annotations.keys(): continue
        
        ensure_directory_exists(os.path.join(output_folder,annotation),print_info=False)
        
        output_shapefile_path = output_folder + annotation + "/" + new_file_name
        
        tolerance = annotations[annotation]['tolerance']

        binary_raster_to_shp(input_geotiff,output_shapefile_path, epsg_code, tolerance)







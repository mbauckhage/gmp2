from utils.statistics import process_geojsons


"""
DEPRECATED
This script is used to create the height statistics (min/max height) of the segmentation files.
"""

input_folder = "/Volumes/T7 Shield/GMP_Data/processed_data/00_Segmentation"  
output_json = "/Volumes/T7 Shield/GMP_Data/processed_data/00_Segmentation/height_statistics.json" 


process_geojsons(input_folder, output_json)

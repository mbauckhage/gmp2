from utils.segmentation import assign_heights
import os


"""
Use exisitng contour line heights to assign heights to the skeleton.
"""

# Parameters:
# ---------------------------------------------

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/00_Segmentation/"
overwrite = False
years = [1899]

# ---------------------------------------------

source_geojson = base_path + '1912/skeleton_1912_heights.geojson'

for year in years:
    target_geojson = base_path + f'{year}/skeleton_{year}.geojson'
    output_geojson = base_path + f'{year}/skeleton_{year}_heights.geojson'
    
    if os.path.exists(output_geojson):
        print(f"Warning: {output_geojson} already exists.")
    
    
    if not os.path.exists(target_geojson) or overwrite == True:
    
        assign_heights(source_geojson=source_geojson, target_geojson=target_geojson, output_geojson=output_geojson)


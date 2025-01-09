from utils.select_seed import *
from utils.segmentation import *
from utils.floodfill import *
import cv2
import tkinter as tk
from tkinter import messagebox
from utils.general_functions import *


"""
This script is the main script for the segmentation of the maps.
Start the script, select the seed point and the script will segment the map and save the skeleton as a geojson file.
"""


# Parameters:
# ---------------------------------------------
skeleton_trace_iterations = 500
years = [1904,1912,1930,1939]
years = [2024]
overwrite = False


# Input paths:
# ---------------------------------------------
base_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/"
base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/02_clipped/"
base_path = "/Volumes/T7 Shield/GMP2/Report_Documentation/"

# Output paths:
# ---------------------------------------------
base_path_output = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/01_Segmentation/output/"
base_path_output = "/Volumes/T7 Shield/GMP_Data/processed_data/00_Segmentation/"
base_path = "/Volumes/T7 Shield/GMP2/Report_Documentation/"

# ---------------------------------------------


images = []
seed_points = []
current_years = []
skeleton_img_paths = []
image_file_paths = []
output_paths_geojson = []
 


for year in years:
    
    image_file = f"stiched_map_{year}_clipped.tif"
    output_dir = base_path_output + str(year) + "/"
    
    ensure_file_exists(base_path + image_file)
    ensure_directory_exists(output_dir)

    skeleton_img_path = output_dir + f"skeleton_{year}.png"
    output_path_geojson = output_dir + f"skeleton_{year}.geojson"

    image_file_path = base_path + image_file

    image = cv2.imread(image_file_path, cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    seed_point = select_seed(image)

    assert check_seed_point(seed_point,image), "No seed point was selected."
    
    images.append(image_rgb)
    seed_points.append(seed_point)
    current_years.append(year)
    skeleton_img_paths.append(skeleton_img_path)
    image_file_paths.append(image_file_path)
    output_paths_geojson.append(output_path_geojson)

    
    assert len(images) == len(seed_points), "The number of images and seed points does not match."


for image_rgb,seed_point,current_year,skeleton_img_path,image_file_path,output_path_geojson in zip(images,seed_points,current_years,skeleton_img_paths,image_file_paths,output_paths_geojson):
    
    print(f"Processing image from {current_year}...")

    image_to_process = mask_image(image_rgb)

    flood_result = flood_fill(image_to_process, seed_point, tolerance=0.5)

    connected_result = find_connected_components(flood_result, blob_threshold_size=12, dilate_kernel_size=5)

    skeleton_result = skeletonize_image(connected_result,save_path=skeleton_img_path) 

    skeleton_traces = skeleton_trace(skeleton_img_path,image_file_path,output_path_geojson,skeleton_trace_iterations,overwrite=overwrite)
    
    
print("--> Done")



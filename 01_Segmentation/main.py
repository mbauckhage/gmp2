from utils.select_seed import *
from utils.segmentation import *
from utils.floodfill import *
import cv2
import tkinter as tk
from tkinter import messagebox

# Input paths:
# ---------------------------------------------
image_file_path = 'data/Siegfried.tif'

# Output paths:
# ---------------------------------------------
skeleton_img_path = "output/full_test/skeleton.png"
output_path_geojson = "output/full_test/skeleton.geojson"

# Parameters:
# ---------------------------------------------
skeleton_trace_iterations = 500


# ---------------------------------------------

image = cv2.imread(image_file_path, cv2.IMREAD_COLOR)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

seed_point = select_seed(image)

assert check_seed_point(seed_point,image), "No seed point was selected."

image_to_process = mask_image(image_rgb)

flood_result = flood_fill(image_to_process, seed_point, tolerance=0.5)

connected_result = find_connected_components(flood_result, blob_threshold_size=12, dilate_kernel_size=5)

skeleton_result = skeletonize_image(connected_result,save_path=skeleton_img_path) 

skeleton_traces = skeleton_trace(skeleton_img_path,image_file_path,output_path_geojson,skeleton_trace_iterations)

plt.imshow(skeleton_traces)
plt.show()



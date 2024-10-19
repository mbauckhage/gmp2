import numpy as np
import matplotlib.pyplot as plt
from skimage import color, morphology
from skimage.segmentation import flood, flood_fill
import cv2
import rasterio
import json
from shapely.geometry import LineString
import geopandas as gpd
from skimage.morphology import skeletonize
from trace_skeleton import *
from pyproj import Transformer
from rasterio.crs import CRS
import random

from utils.segmentation import plot_images, crop_image, mask_image, mask_flood_fill
import os


def flood_fill(image, seed_point, tolerance=0.5):
    
    print("--- flood_fill ---")
    
    img_test = color.rgb2hsv(image)
    
    # flood function returns a mask of flooded pixels
    mask = flood(img_test[..., 0], seed_point, tolerance=tolerance)
    
    # Set pixels of mask to new value for hue channel
    img_test[mask, 0] = 0

    # Create a mask for red hue values: low red and high red
    low_red_mask = img_test[..., 2] > 0.4

    # Combine both masks to capture all red pixels (low and high red hues)
    flood_result = low_red_mask 

    return flood_result


def find_connected_components(mask, blob_threshold_size=12, dilate_kernel_size=5):
    
    print("--- find_connected_components ---")

    # Assuming your input image is a boolean mask (True/False or 0/1)
    # Convert the image to uint8 format (0 or 255)
    mask_uint8 = mask.astype(np.uint8) * 255

    # Label connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_uint8, connectivity=8)

    # Create a new image to store the filtered output
    filtered_img = np.zeros_like(mask_uint8)

    # Keep only components larger than blob_threshold_size
    for i in range(1, num_labels):  # Start from 1 to skip the background
        if stats[i, cv2.CC_STAT_AREA] >= blob_threshold_size:
            filtered_img[labels == i] = 255

    # Apply a morphological closing operation to fill small holes        
    kernel = np.ones((dilate_kernel_size,dilate_kernel_size),np.uint8)
    dilated_filtered_img = cv2.dilate(filtered_img, kernel, iterations=1)

    # Show the filtered image
    #plot_images(mask_uint8, filtered_img,dilated_filtered_img, titles=['Original Mask', 'Filtered Mask','Closed Filtered Mask'], height=10)

    return dilated_filtered_img

def skeletonize_image(mask,save_path=None):
    
    print("--- skeletonize_image ---")
    
    # Perform skeletonization to get the centerline of the shapes
    skeleton_lee = morphology.skeletonize(mask,method='lee')

    # remove small blobs using a morphological dilation operation
    kernel = np.ones((5,5),np.uint8)
    skeleton_dilated = cv2.dilate(skeleton_lee.astype(np.uint8), kernel, iterations=3)
    
    # Perform again skeletonization to get the centerline of the shapes
    skeleton2 = morphology.skeletonize(skeleton_dilated)
    
    if save_path:
        plt.imsave(save_path, skeleton2, cmap='gray')
    
    return skeleton2

def plot_skeleton_trace(skeleton_img_path,iterations=999):
    
    print("--- plot_skeleton_trace ---")

    im0 = cv2.imread(skeleton_img_path)
    im = (im0[:,:,0]>128).astype(np.uint8)

    im = thinning(im)

    rects = []
    polys = traceSkeleton(im,0,0,im.shape[1],im.shape[0],10,iterations,rects)

    for l in polys:
        c = (200*random.random(),200*random.random(),200*random.random())
        for i in range(0,len(l)-1):
            cv2.line(im0,(l[i][0],l[i][1]),(l[i+1][0],l[i+1][1]),c)

    plt.imshow(im0)
    
def skeleton_trace(skeleton_img_path,original_img_path,output_path_geojson,iterations=999,overwrite=False):
    
    print("--- skeleton_trace ---")
    
    assert os.path.exists(skeleton_img_path), f"File {skeleton_img_path} not found."
    
    # Check if the output GeoJSON file already exists
    if os.path.exists(output_path_geojson) and not overwrite:
        print(f"File {output_path_geojson} already exists. Please choose a different file name or delete the existing file.")
        return

    # Read the pixel size (resolution) from the TIFF file using rasterio
    with rasterio.open(original_img_path) as src:
        transform = src.transform
        crs = src.crs  # Get the coordinate reference system (CRS)
        pixel_width = transform[0]  # Size of a pixel in the x direction (in meters)
        pixel_height = abs(transform[4])  # Size of a pixel in the y direction (in meters)

        # Get the coordinates of the bottom-left corner (0, height in pixel coordinates)
        bottom_left_x, bottom_left_y = transform * (0, src.height)
        
    # Create a transformer to convert from EPSG:21781 (if that's the original CRS) to EPSG:2056
    transformer = Transformer.from_crs(crs, CRS.from_epsg(2056), always_xy=True)

    # Convert the bottom-left coordinates to EPSG:2056
    bottom_left_x, bottom_left_y = transformer.transform(bottom_left_x, bottom_left_y)

    # Constants to convert image coordinates to EPSG:2056
    LON_CONSTANT = bottom_left_x  # Adjust to the correct EPSG:2056 longitude base
    LAT_CONSTANT = bottom_left_y  # Adjust to the correct EPSG:2056 latitude base


    im0 = cv2.imread(skeleton_img_path)

    # Binarize the skeleton image
    im = (im0[:,:,0] > 128).astype(np.uint8)

    # Get image dimensions
    height, width = im.shape

    # Thin the image
    im = thinning(im)

    # Trace the skeleton to get line coordinates
    rects = []
    polys = traceSkeleton(im, 0, 0, width, height, 10, 500, rects)

    # Convert image coordinates to EPSG:2056 and store in GeoJSON format
    features = []
    for l in polys:
        coordinates = []
        for coord in l:
            # Flip Y axis by subtracting the pixel's y-coordinate from the image height
            flipped_y = height - coord[1]

            # Apply pixel size to convert image coordinates to real-world distances
            scaled_x = coord[0] * pixel_width  # Apply pixel width scaling
            scaled_y = flipped_y * pixel_height  # Apply pixel height scaling
            
            # Convert image coordinates to EPSG:2056 by adding the constants
            lon = scaled_x + LON_CONSTANT  # X-axis (longitude/easting)
            lat = scaled_y + LAT_CONSTANT  # Y-axis (latitude/northing)

            coordinates.append([lon, lat])

        # Create a GeoJSON feature for each line
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            },
            "properties": {
                "color": f"rgb({200*random.random()}, {200*random.random()}, {200*random.random()})"
            }
        }
        features.append(feature)

    # Create GeoJSON structure
    geojson_data = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path_geojson, 'w') as geojson_file:
        json.dump(geojson_data, geojson_file, indent=2)

    print(f"GeoJSON saved as {output_path_geojson}")

    # Optionally, display the image with colored lines
    for l in polys:
        c = (200*random.random(), 200*random.random(), 200*random.random())
        for i in range(0, len(l) - 1):
            cv2.line(im0, (l[i][0], l[i][1]), (l[i+1][0], l[i+1][1]), c)

    return im0


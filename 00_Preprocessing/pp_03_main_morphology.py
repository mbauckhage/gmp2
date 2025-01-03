import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import os
from utils.preprocessing import ensure_directory_exists
import rasterio
import numpy as np
from scipy.ndimage import binary_fill_holes, binary_dilation, binary_erosion
from rasterio.features import shapes
from rasterio.transform import Affine


base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_masking = "02_clipped/"
new_resolution = (1, 1)  

annotations = ["rivers"]

def fill_and_connect_surfaces(input_tiff_path, output_tiff_path, dilation_iterations=3, erosion_iterations=2):
    """
    Reads a GeoTIFF file, connects close surfaces using dilation, fills holes, and writes the result to a new GeoTIFF.
    
    Args:
        input_tiff_path (str): Path to the input GeoTIFF file.
        output_tiff_path (str): Path to save the output GeoTIFF file.
        dilation_iterations (int): Number of iterations for morphological dilation.
        erosion_iterations (int): Number of iterations for morphological erosion (optional).
    """
    # Step 1: Read the input GeoTIFF
    with rasterio.open(input_tiff_path) as src:
        data = src.read(1)  # Read the first band
        meta = src.meta.copy()  # Copy metadata
        transform = src.transform  # GeoTransform
    
    # Step 2: Binarize the raster (assumes binary or threshold data)
    binary_data = (data > 0).astype(np.uint8)
    
    # Step 3: Connect close surfaces using dilation
    dilated_data = binary_dilation(binary_data, iterations=dilation_iterations).astype(np.uint8)
    
    # Step 4: Fill holes using binary_fill_holes
    filled_data = binary_fill_holes(dilated_data).astype(np.uint8)
    
    # Step 5 (Optional): Restore size using erosion
    final_data = binary_erosion(filled_data, iterations=erosion_iterations).astype(np.uint8)
    
    # Step 6: Write the output GeoTIFF
    meta.update(dtype=rasterio.uint8)  # Update metadata to uint8
    with rasterio.open(output_tiff_path, 'w', **meta) as dst:
        dst.write(final_data, 1)  # Write the processed raster to the first band

    print(f"Processed GeoTIFF written to: {output_tiff_path}")





input_folder = os.path.join(base_path, input_for_masking)
output_folder = os.path.join(base_path, "03_filled_holes/")
ensure_directory_exists(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith(".tif") and not filename.startswith("._") and filename.split("_")[1] in annotations:
        input_geotiff = os.path.join(input_folder, filename)
        output_geotiff = os.path.join(output_folder, filename)
        fill_and_connect_surfaces(input_geotiff, output_geotiff)




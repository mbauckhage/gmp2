import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import os
from utils.preprocessing import ensure_directory_exists


base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_masking = "02_clipped/"
new_resolution = (1, 1)  



def resample_geotiff(input_path, output_path, target_resolution):
    """
    Reads a GeoTIFF, changes its resolution, and saves it to a new file.
    
    Parameters:
    - input_path (str): Path to the input GeoTIFF.
    - output_path (str): Path to save the resampled GeoTIFF.
    - target_resolution (tuple): Desired resolution in the form (new_pixel_size_x, new_pixel_size_y).
    """
    with rasterio.open(input_path) as src:
        # Calculate new transform and dimensions based on target resolution
        new_transform, width, height = calculate_default_transform(
            src.crs, src.crs, src.width, src.height, 
            *src.bounds, 
            resolution=target_resolution
        )

        # Define new profile with updated width, height, and transform
        new_profile = src.profile
        new_profile.update({
            'transform': new_transform,
            'width': width,
            'height': height
        })

        # Create the destination file with the new profile
        with rasterio.open(output_path, 'w', **new_profile) as dst:
            for i in range(1, src.count + 1):
                # Resample each band
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=new_transform,
                    dst_crs=src.crs,
                    resampling=Resampling.bilinear
                )
    
    print(f"Resampled GeoTIFF saved at: {output_path}")




input_folder = os.path.join(base_path, input_for_masking)
output_folder = os.path.join(base_path, "03_resampled/")
ensure_directory_exists(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith(".tif") and not filename.startswith("._"):
        input_geotiff = os.path.join(input_folder, filename)
        output_geotiff = os.path.join(output_folder, filename)
        resample_geotiff(input_geotiff, output_geotiff, new_resolution)



import rasterio
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import os



def resample_geotiff(input_path, output_path, target_resolution,target_crs=None):
    """
    Reads a GeoTIFF, changes its resolution, and saves it to a new file.
    
    Parameters:
    - input_path (str): Path to the input GeoTIFF.
    - output_path (str): Path to save the resampled GeoTIFF.
    - target_resolution (tuple): Desired resolution in the form (new_pixel_size_x, new_pixel_size_y).
    """
    with rasterio.open(input_path) as src:
        
        # Determine the source CRS and set the target CRS
        src_crs = src.crs
        target_crs = target_crs if target_crs else src_crs
        
        
        # Calculate new transform and dimensions based on target resolution
        new_transform, width, height = calculate_default_transform(
            src_crs,target_crs, src.width, src.height, 
            *src.bounds, 
            resolution=target_resolution
        )

        # Define new profile with updated width, height, and transform
        new_profile = src.profile
        new_profile.update({
            'crs': target_crs,
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

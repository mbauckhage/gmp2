import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS
import numpy as np


def georeference_png(png_path, reference_geotiff, output_geotiff):
    """
    Georeference a PNG image using corner coordinates and CRS from an existing GeoTIFF.

    Parameters:
        png_path (str): Path to the input PNG file.
        reference_geotiff (str): Path to the reference GeoTIFF file.
        output_geotiff (str): Path to save the georeferenced GeoTIFF file.
    """
    # Read the reference GeoTIFF for georeferencing information
    with rasterio.open(reference_geotiff) as ref:
        ref_bounds = ref.bounds
        ref_crs = ref.crs
        ref_transform = ref.transform
        ref_width = ref.width
        ref_height = ref.height
    
    # Open the PNG file and read its data
    with rasterio.open(png_path) as src:
        png_data = src.read()
        png_height, png_width = src.height, src.width

    # Compute a new transform for the PNG using the reference bounds and the PNG's resolution
    transform = from_bounds(
        ref_bounds.left, ref_bounds.bottom, ref_bounds.right, ref_bounds.top,
        png_width, png_height
    )

    # Write the PNG data as a GeoTIFF with the georeferenced transform and CRS
    with rasterio.open(
        output_geotiff, 'w',
        driver='GTiff',
        height=png_height,
        width=png_width,
        count=png_data.shape[0],
        dtype=png_data.dtype,
        crs=ref_crs,
        transform=transform
    ) as dst:
        dst.write(png_data)

    print(f"Georeferenced GeoTIFF saved at {output_geotiff}")

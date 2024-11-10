import rasterio
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from PIL import Image




def interpolate_raster(input_raster_path, output_raster_path,method='linear',sigma=3):
    # Step 1: Open the input raster file
    with rasterio.open(input_raster_path) as src:
        raster_data = src.read(1)  # Read the first band (grayscale)
        transform = src.transform  # Preserve the original affine transform
        crs = src.crs  # Preserve the original CRS
        width = src.width
        height = src.height

    # Step 2: Identify the pixels that are non-zero (representing contour lines)
    y_indices, x_indices = np.indices(raster_data.shape)
    non_zero_mask = raster_data > 0
    non_zero_x = x_indices[non_zero_mask]
    non_zero_y = y_indices[non_zero_mask]
    non_zero_values = raster_data[non_zero_mask]

    # Step 3: Perform interpolation to fill in the gaps using griddata
    interpolated_raster = griddata(
        (non_zero_x, non_zero_y), non_zero_values,
        (x_indices, y_indices), method=method, fill_value=0
    )

    # Optional: Apply a Gaussian filter to smooth the interpolated raster
    smoothed_raster = gaussian_filter(interpolated_raster, sigma=sigma)

    # Step 4: Save the interpolated raster to a new GeoTIFF file with one band
    with rasterio.open(
        output_raster_path,
        'w',
        driver='GTiff',
        height=smoothed_raster.shape[0],
        width=smoothed_raster.shape[1],
        count=1,  # Single band
        dtype='float32',  # Use float32 for continuous values
        crs=crs,  # Use the original CRS
        transform=transform  # Use the original transform
    ) as dst:
        dst.write(smoothed_raster, 1)  # Write the smoothed raster to the first band

    print(f"Interpolated raster saved to {output_raster_path}")
    

    convert_tif_to_png(output_raster_path, output_raster_path.replace('.tif', '.png'))




def convert_tif_to_png(input_tif_path, output_png_path):
    # Open the TIFF file
    with Image.open(input_tif_path) as img:
        # Convert the image to a mode supported by PNG
        if img.mode == 'F':
            img = img.convert('L')  # Convert to grayscale
        elif img.mode not in ['L', 'RGB']:
            img = img.convert('RGB')  # Convert to RGB if not already in a supported mode
        # Save the image as PNG
        img.save(output_png_path, "PNG")
        print(f"Converted {input_tif_path} to {output_png_path}")



def make_img_square(input_img_path, output_img_path):
    with rasterio.open(input_img_path) as src:
        data = src.read(1)  # Read the first band
        height, width = data.shape

        # Determine the size of the square
        size = max(height, width)

        # Create a new array with the square size and fill with zeros
        square_data = np.zeros((size, size), dtype=data.dtype)

        # Place the original data in the top-left corner of the square array
        square_data[:height, :width] = data

        # Update the metadata to reflect the new dimensions
        meta = src.meta.copy()
        meta.update({
            "height": size,
            "width": size,
            "transform": rasterio.transform.from_bounds(
                src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top,
                size, size
            )
        })

        # Write the square data to a new TIFF file
        with rasterio.open(output_img_path, 'w', **meta) as dst:
            dst.write(square_data, 1)


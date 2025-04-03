import rasterio
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from PIL import Image
from osgeo import gdal, osr




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
    
    min_value = np.min(non_zero_values)
    

    # Step 3: Perform interpolation to fill in the gaps using griddata
    interpolated_raster = griddata(
        (non_zero_x, non_zero_y), non_zero_values,
        (x_indices, y_indices), method=method, fill_value=min_value
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



import numpy as np
import rasterio
from rasterio.transform import from_bounds

def make_img_square(input_img_path, output_img_path, method="max", align="center"):
    """
    Squares an image by either extending or cropping based on the given method.
    
    Parameters:
    - input_img_path (str): Path to the input image.
    - output_img_path (str): Path to save the squared output image.
    - method (str): "max" (pad to the longer side) or "min" (crop to the shorter side).
    - align (str): Alignment when cropping to the shorter side. Options: "left", "center", "right".
    """
    with rasterio.open(input_img_path) as src:
        data = src.read(1)  # Read the first band
        height, width = data.shape

        if method == "max":
            # Square based on the longer side
            size = max(height, width)
            square_data = np.zeros((size, size), dtype=data.dtype)

            # Place the original data in the top-left corner
            square_data[:height, :width] = data

            # Update the metadata
            meta = src.meta.copy()
            meta.update({
                "height": size,
                "width": size,
                "transform": from_bounds(
                    src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top,
                    size, size
                )
            })

        elif method == "min":
            # Square based on the shorter side
            size = min(height, width)

            # Determine the crop offsets
            if align == "left":
                x_offset, y_offset = 0, 0
            elif align == "center":
                x_offset = (width - size) // 2
                y_offset = (height - size) // 2
            elif align == "right":
                x_offset = width - size
                y_offset = height - size
            else:
                raise ValueError("Invalid align value. Choose from 'left', 'center', or 'right'.")

            # Crop the original data
            square_data = data[y_offset:y_offset + size, x_offset:x_offset + size]

            # Update the metadata
            meta = src.meta.copy()
            meta.update({
                "height": size,
                "width": size,
                "transform": from_bounds(
                    src.bounds.left + x_offset * src.transform.a,  # Adjust left bound
                    src.bounds.bottom + y_offset * src.transform.e,  # Adjust bottom bound
                    src.bounds.left + (x_offset + size) * src.transform.a,  # Adjust right bound
                    src.bounds.bottom + (y_offset + size) * src.transform.e,  # Adjust top bound
                    size, size
                )
            })

        else:
            raise ValueError("Invalid method value. Choose 'max' or 'min'.")

        # Write the squared data to a new file
        with rasterio.open(output_img_path, 'w', **meta) as dst:
            dst.write(square_data, 1)

    print(f"Squared image saved at: {output_img_path}")

def reproject_and_clean_raster(input_path, output_path, src_epsg=2056, dst_epsg=4326):
        """ 
        Reproject raster from source EPSG to destination EPSG 
        and replace zero values with the smallest non-zero value.
        """

        # Open source raster
        src_ds = gdal.Open(input_path)
        src_proj = osr.SpatialReference()
        src_proj.ImportFromEPSG(src_epsg)

        dst_proj = osr.SpatialReference()
        dst_proj.ImportFromEPSG(dst_epsg)

        # Reproject the raster
        temp_output_path = output_path.replace(".tif", "_temp.tif")
        gdal.Warp(
            temp_output_path,
            src_ds,
            dstSRS=dst_proj.ExportToWkt(),
            dstNodata=src_ds.GetRasterBand(1).GetNoDataValue(),
            outputType=gdal.GDT_Float32,
            resampleAlg=gdal.GRA_Lanczos  # High-quality resampling
        )

        # Open the reprojected raster and clean zero values
        with rasterio.open(temp_output_path) as src:
            data = src.read(1)

            # Find the smallest nonzero value
            min_nonzero = np.min(data[data > 0]) if np.any(data > 0) else 0

            # Replace zero values with the minimum nonzero value
            data[data == 0] = min_nonzero
            
            # set all borader values to zero
            data[:, 0] = 0
            data[:, -1] = 0
            data[0, :] = 0
            data[-1, :] = 0

            # Write the final cleaned raster
            profile = src.profile
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(data, 1)

        # Remove temporary file
        gdal.Unlink(temp_output_path)

        print(f"Reprojected and cleaned raster saved at: {output_path}")
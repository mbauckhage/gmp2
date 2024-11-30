import rasterio
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from PIL import Image
from rasterio.transform import from_bounds

def make_img_square(input_img_path, output_img_path,method="max", align="center", default_color=(211, 211, 196)):
    with rasterio.open(input_img_path) as src:
        # Read all bands (assuming it's an RGB image)
        data = src.read()  # Shape will be (bands, height, width)
        bands, height, width = data.shape
        
        if method == "max":

            # Determine the size of the square
            size = max(height, width)

            # Create a new array with the square size and fill with the default color
            square_data = np.full((bands, size, size), 0, dtype=data.dtype)
        
            # Fill with default color (convert to the same dtype as the image)
            for i in range(bands):
                square_data[i, :, :] = default_color[i] if i < len(default_color) else 0

            # Place the original data in the top-left corner of the square array
            square_data[:, :height, :width] = data

            # Update the metadata to reflect the new dimensions
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
            square_data = data[:,y_offset:y_offset + size, x_offset:x_offset + size]

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

        # Write the square data to a new output file
        with rasterio.open(output_img_path, 'w', **meta) as dst:
            dst.write(square_data)
    
    print(f"Squared image saved at: {output_img_path}")


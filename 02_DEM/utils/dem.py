import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from shapely.geometry import mapping
import numpy as np
from PIL import Image
import os
import logging
from rasterio.transform import from_origin
from tqdm import tqdm
from skimage.util import view_as_windows
import cv2

import rasterio
import numpy as np
from rasterio.warp import reproject, calculate_default_transform, Resampling
from rasterio.windows import from_bounds


def geojson_to_tiff(geojson_path, tiff_path, resolution=0.5, input_crs='EPSG:2056', height_attribute='hoehe'):
    
    # Read the GeoJSON as a GeoDataFrame
    gdf = gpd.read_file(geojson_path)
    
    # Ensure the GeoDataFrame has a 'hoehe' column
    if height_attribute not in gdf.columns:
        raise ValueError(f"GeoJSON must have a {height_attribute} attribute for heights")
    
    min_height, max_height = get_min_max_height_from_geojson(gdf, height_attribute)
    logging.info(f"Min height: {min_height}, Max height: {max_height}")
    
    # Normalize height values between 0 and 255
    gdf[height_attribute] = (((gdf[height_attribute] - min_height) / (max_height - min_height)) * 255).astype(np.uint8)

    
    # Select only the 'height' attribute and the geometry
    gdf = gdf[[height_attribute, 'geometry']]
    
    # Check validity of each geometry
    gdf['is_valid'] = gdf['geometry'].is_valid
    
    # Show all invalid geometries
    invalid_geometries = gdf[~gdf['is_valid']]
    logging.info(f"Number of invalid geometries: {len(invalid_geometries)}")
    # Remove all features that have 'is_valid' == False
    gdf = gdf[gdf['is_valid']]


    # Set up the bounds of the raster (based on the geometry bounds)
    minx, miny, maxx, maxy = gdf.total_bounds
    logging.info(f"Bounds: {minx, miny, maxx, maxy}")

    # Define the output raster dimensions (based on the finer resolution)
    width = int((maxx - minx) / resolution)
    height = int((maxy - miny) / resolution)

    # Create an affine transform for the raster
    transform = rasterio.transform.from_bounds(minx, miny, maxx, maxy, width, height)

    # Create an empty array to store the raster data
    raster = np.zeros((height, width), dtype=rasterio.uint8)

    # Prepare geometries and corresponding 'hoehe' values for rasterization
    shapes = ((mapping(geom), value) for geom, value in zip(gdf.geometry, gdf[height_attribute]))

    # Rasterize the MultiLineString geometries using the 'hoehe' values
    raster = rasterize(
        shapes=shapes,
        out_shape=raster.shape,
        transform=transform,
        fill=0,  # Background value
        dtype=rasterio.uint8
    )
    
    logging.info(f"Raster data type: {raster.dtype}, min={raster.min()}, max={raster.max()}")


    # Save the raster data to a GeoTIFF with EPSG:2056
    with rasterio.open(
        tiff_path,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=rasterio.uint8,
        crs='EPSG:2056',  # Set the CRS to EPSG:2056
        transform=transform,
    ) as dst:
        dst.write(raster, 1)

def geojson_to_png_tiles(geojson_path, output_dir, resolution=0.5, input_crs='EPSG:2056', height_attribute='hoehe',min_nonzero_value=450,tile_size=512):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the GeoJSON as a GeoDataFrame
    gdf = gpd.read_file(geojson_path)

    # Ensure the GeoDataFrame has a 'hoehe' column
    if height_attribute not in gdf.columns:
        raise ValueError(f"GeoJSON must have a {height_attribute} attribute for heights")
    
     # Select only the 'height' attribute and the geometry
    gdf = gdf[[height_attribute, 'geometry']]
    
    # Check validity of each geometry
    gdf['is_valid'] = gdf['geometry'].is_valid
    
    # Show all invalid geometries
    invalid_geometries = gdf[~gdf['is_valid']]
    logging.info(f"Number of invalid geometries: {len(invalid_geometries)}")
    # Remove all features that have 'is_valid' == False
    gdf = gdf[gdf['is_valid']]
    
    """
    # Check if CRS is set; if not, assign the input CRS (assuming EPSG:4326 if not provided)
    if gdf.crs is None:
        gdf.set_crs(input_crs, inplace=True)
        logging.info(f"CRS was missing. Set to {input_crs}")

    # Reproject the GeoDataFrame to EPSG:2056
    gdf = gdf.to_crs(epsg=2056)"""

    # Set up the bounds of the raster (based on the geometry bounds)
    minx, miny, maxx, maxy = gdf.total_bounds

    # Define the output raster dimensions (based on the finer resolution)
    width = int((maxx - minx) / resolution)
    height = int((maxy - miny) / resolution)

    # Create an affine transform for the raster
    transform = rasterio.transform.from_bounds(minx, miny, maxx, maxy, width, height)

    # Create an empty array to store the raster data
    raster = np.zeros((height, width), dtype=rasterio.float32)

    # Prepare geometries and corresponding 'hoehe' values for rasterization
    shapes = ((mapping(geom), value) for geom, value in zip(gdf.geometry, gdf[height_attribute]))

    # Rasterize the geometries using the 'hoehe' values
    raster = rasterize(
        shapes=shapes,
        out_shape=raster.shape,
        transform=transform,
        fill=0,  # Background value
        dtype=rasterio.float32
    )
    
    # Calculate the maximum value for the normalization
    max_value = raster.max()

    # Normalize the raster to [0, 255] using the provided min_nonzero_value and the raster's maximum value
    raster_normalized = np.where(
        raster > 0,  # Only normalize non-zero values
        (raster - min_nonzero_value) / (max_value - min_nonzero_value) * 255,
        0  # Set background or zero values to 0
    )
    
     # Clip values below 0 to 0, and above 255 to 255
    raster_normalized = np.clip(raster_normalized, 0, 255)

    # Calculate how many 512x512 tiles are needed
    num_tiles_x = int(np.ceil(width / tile_size))
    num_tiles_y = int(np.ceil(height / tile_size))

    # Loop through each tile
    for tile_x in range(num_tiles_x):
        for tile_y in range(num_tiles_y):
            # Calculate the pixel boundaries for the current tile
            start_x = tile_x * tile_size
            start_y = tile_y * tile_size
            end_x = min(start_x + tile_size, width)
            end_y = min(start_y + tile_size, height)

            # Extract the tile from the raster
            tile = raster_normalized[start_y:end_y, start_x:end_x]

            # Create a 512x512 image (pad with zeros if the tile is smaller)
            tile_padded = np.zeros((tile_size, tile_size), dtype=np.uint8)
            tile_padded[:tile.shape[0], :tile.shape[1]] = tile.astype(np.uint8)

            # Convert the tile to a PIL image
            img = Image.fromarray(tile_padded, mode='L')  # 'L' for grayscale

            # Save the image with a filename based on the tile indices
            img.save(os.path.join(output_dir, f'tile_{tile_y}_{tile_x}.png'))


    logging.info(f"Tiles saved to {output_dir}")

def get_min_max_height_from_geojson(gdf, height_attribute='hoehe'):


    # Ensure the GeoDataFrame has a 'hoehe' column
    if height_attribute not in gdf.columns:
        raise ValueError(f"GeoJSON must have a {height_attribute} attribute for heights")

    
    non_zero_heights = gdf[gdf[height_attribute] > 0][height_attribute]
    min_height = non_zero_heights.min()
    max_height = gdf[height_attribute].max()  

    return min_height, max_height

def adjust_heightmap_with_rivers(heightmap_path, river_mask_path, output_path, reduction_value=2.0, falloff_distance=50):
    """
    Adjust heightmap values based on a binary river mask, lowering the riverbed by up to 2 meters.

    Args:
        heightmap_path: Path to the heightmap image (stitched from tiles).
        river_mask_path: Path to the binary river mask image (1 for river, 0 for non-river).
        output_path: Path to save the adjusted heightmap.
        reduction_value: Maximum height reduction at the riverbed.
        falloff_distance: Distance (in pixels) from the riverbed where the effect of lowering falls off to 0.
    """
    # Load the heightmap and river mask
    heightmap = np.array(Image.open(heightmap_path)).astype(np.float32) / 255.0  # Normalized [0, 1]
    river_mask = np.array(Image.open(river_mask_path)).astype(np.float32)  # Binary mask (0 or 1)

    # Create a copy of the heightmap for adjustment
    adjusted_heightmap = heightmap.copy()

    # Lower the heightmap where the river mask is 1
    adjusted_heightmap[river_mask == 1] -= reduction_value / 255.0

    # Ensure that we do not go below 0 in the heightmap
    adjusted_heightmap = np.clip(adjusted_heightmap, 0, 1)

    # Apply a distance-based falloff for areas near the river (blurring the river mask)
    if falloff_distance > 0:
        # Use a distance transform to determine distances from the river edges
        dist_transform = cv2.distanceTransform(1 - river_mask.astype(np.uint8), cv2.DIST_L2, 5)

        # Normalize the distance to [0, 1] within the falloff range
        dist_falloff = np.clip(dist_transform / falloff_distance, 0, 1)

        # Linearly interpolate the heightmap modification based on distance from river
        adjusted_heightmap = np.where(
            (river_mask == 0) & (dist_transform <= falloff_distance), 
            heightmap - (reduction_value / 255.0) * (1 - dist_falloff), 
            adjusted_heightmap
        )

        # Ensure values remain within [0, 1] range
        adjusted_heightmap = np.clip(adjusted_heightmap, 0, 1)

    # Save the adjusted heightmap
    adjusted_heightmap_img = Image.fromarray((adjusted_heightmap * 255).astype(np.uint8), mode='L')
    adjusted_heightmap_img.save(output_path)
    logging.info(f"Adjusted heightmap saved to {output_path}")

def set_crs_for_tiles(reference_dir, input_dir, output_dir):
    # Create output folder if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Loop through all TIFF files in the reference directory
    for filename in os.listdir(reference_dir):
        if filename.endswith(".tif"):  # Check for TIFF files
            # Get the corresponding TIFF file in the input directory
            cor_filename = filename.replace("tile", "height_map_tile")
            corresponding_input_file = os.path.join(input_dir, cor_filename)
            
            # Check if the corresponding input file exists
            if os.path.exists(corresponding_input_file):
                # Open the reference TIFF file to get its transform and CRS
                with rasterio.open(os.path.join(reference_dir, filename)) as src1:
                    reference_transform = src1.transform
                    reference_crs = src1.crs  # Get the CRS

                # Open the corresponding TIFF file to read its data
                with rasterio.open(corresponding_input_file) as src2:
                    data = src2.read(1)  # Read the first band
                    

                # Create a new TIFF file with the updated transform
                updated_tif_path = os.path.join(output_dir, f"updated_{filename}")
                with rasterio.open(
                        updated_tif_path,
                        'w',
                        driver='GTiff',
                        height=data.shape[0],
                        width=data.shape[1],
                        count=1,
                        dtype=data.dtype,
                        crs=reference_crs,  # Use the same CRS as the reference TIFF
                        transform=reference_transform
                ) as dst:
                    dst.write(data, 1)  # Write the data to the new TIFF

                logging.info(f"Updated {filename} saved as {updated_tif_path}")
            else:
                logging.info(f"Corresponding file for {filename} not found in input directory.")

    logging.info("All TIFF files have been updated successfully.")
    
    return output_dir
    
def rotate_and_flip_tif(input_folder, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all TIFF files in the input directory
    for filename in os.listdir(input_folder):
        if (filename.endswith(".tif") or (filename.endswith(".png"))):  # Check for TIFF files
            input_tif_path = os.path.join(input_folder, filename)
            output_tif_path = os.path.join(output_folder, filename)

            # Open the input TIFF file
            with rasterio.open(input_tif_path) as src:
                # Read the data
                data = src.read(1)

                # Rotate the data by 270 degrees
                rotated_data = np.rot90(data, k=1)

                # Flip the data
                flipped_data = np.flipud(rotated_data)

                # Update the metadata to reflect the new dimensions
                meta = src.meta.copy()
                meta.update({
                    "height": flipped_data.shape[0],
                    "width": flipped_data.shape[1],
                    "transform": rasterio.transform.from_bounds(
                        src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top,
                        flipped_data.shape[1], flipped_data.shape[0]
                    )
                })

                # Write the rotated and flipped data to a new TIFF file
                with rasterio.open(output_tif_path, 'w', **meta) as dst:
                    dst.write(flipped_data, 1)

            logging.info(f"Processed {filename} and saved to {output_tif_path}")
    
    return output_folder


def generate_tiling(image_path, w_size, overlap=True, normalize=False):
    win_size = w_size
    pad_px = win_size // 2
    in_img = np.array(Image.open(image_path))
    
    # Normalize the image to 0-255
    if normalize: in_img = ((in_img - in_img.min()) / (in_img.max() - in_img.min()) * 255).astype(np.uint8)
    
    if overlap:
        step = pad_px
    else:
        step = win_size

    if len(in_img.shape) == 2:
        img_pad = np.pad(in_img, [(pad_px, pad_px), (pad_px, pad_px)], 'edge')
        tiles = view_as_windows(img_pad, (win_size, win_size), step=step)
    else:
        img_pad = np.pad(in_img, [(pad_px, pad_px), (pad_px, pad_px), (0, 0)], 'edge')
        tiles = view_as_windows(img_pad, (win_size, win_size, 3), step=step)
        
    # Get the number of tiles in the x and y directions
    num_y_tiles = tiles.shape[0]
    num_x_tiles = tiles.shape[1]

    # Print the number of tiles
    print(f"Number of tiles in y direction: {num_y_tiles}")
    print(f"Number of tiles in x direction: {num_x_tiles}")


    tiles_lst = []
    for row in range(tiles.shape[0]):
        for col in range(tiles.shape[1]):
            if len(in_img.shape) == 2:
                tt = tiles[row, col, ...].copy()
            else:
                tt = tiles[row, col, 0, ...].copy()
            tiles_lst.append(tt)
    return tiles_lst, num_x_tiles, num_y_tiles

def reconstruct_tiling(original_image_path, test_pred_dict, tile_save_path, w_size, image_debug=None, save_image=True):
    in_patches = list(test_pred_dict.keys())
    in_patches.sort()
    patches_images = list(test_pred_dict.values())

    # Convert patches_images to a numpy array
    patches_images = np.array(patches_images)
    logging.info(f"Number of patches: {patches_images.shape[0]}")

    win_size = w_size
    pad_px = win_size // 2

    in_img = np.array(Image.open(original_image_path).convert("RGB"))
    
    if in_img is None:
        print('original image {}'.format(original_image_path))

    new_img = reconstruct_from_patches(patches_images, win_size, pad_px, in_img.shape, np.float32)

    # If the image has more than one channel, only store the first channel
    if new_img.shape[-1] > 1:
        new_img = new_img[:, :, 0]
    if save_image:
        cv2.imwrite(tile_save_path, new_img)

    if image_debug is not None:
        cv2.imwrite(image_debug, new_img * 255)
    
    return new_img

def reconstruct_from_patches(patches_images, patch_size, step_size, image_size_2d, image_dtype):
    i_h, i_w = np.array(image_size_2d[:2]) + (patch_size, patch_size)
    p_h = p_w = patch_size

    # Initialize the reconstructed image array
    img = np.zeros((i_h + p_h // 2, i_w + p_w // 2, 3), dtype=image_dtype)

    numrows = (i_h) // step_size - 1
    numcols = (i_w) // step_size - 1
    expected_patches = numrows * numcols
    
    if patches_images.shape[0] != expected_patches:
        raise ValueError(f"Expected {expected_patches} patches, got {patches_images.shape[0]}")

    patch_offset = step_size // 2
    patch_inner = p_h - step_size
    
    for row in range(numrows):
        for col in range(numcols):
            tt = patches_images[row * numcols + col]
            tt_roi = tt[patch_offset:-patch_offset, patch_offset:-patch_offset]

            # Check if the patch is grayscale
            if len(tt.shape) == 2:  # Grayscale case
                tt_roi = np.stack((tt_roi,)*3, axis=-1)  # Convert to RGB by stacking

            img[row * step_size:row * step_size + patch_inner,
                col * step_size:col * step_size + patch_inner] = tt_roi

    return img[step_size // 2:-(patch_size + step_size // 2), step_size // 2:-(patch_size + step_size // 2), :]


def save_tiles(tiles, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, tile in enumerate(tiles):

        tile_image = Image.fromarray(tile)  # Convert numpy array to PIL Image
        
        # If the image is in floating point format, convert it to uint8 (or uint16)
        if tile_image.mode == 'F':
            tile_image = tile_image.convert('I')  # 'I' is for 32-bit integer, or you can convert to 'L' for 8-bit grayscale
        
        
        tile_path = os.path.join(output_dir, f'tile_{i:04d}.png')  # Generate unique file name
        tile_image.save(tile_path)  # Save the image as PNG


def read_tiles(input_dir):
    tile_images = []
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.png'):
            tile_path = os.path.join(input_dir, filename)
            tile_image = np.array(Image.open(tile_path))  # Read the image and convert to numpy array
            tile_images.append(tile_image)
    return tile_images





def extract_extent(input_png_path, output_png_path, left, upper, right, lower):
    # Open the PNG file
    with Image.open(input_png_path) as img:
        # Crop the image to the specified extent
        cropped_img = img.crop((left, upper, right, lower))
        # Save the cropped image
        cropped_img.save(output_png_path)
        print(f"Extracted extent and saved to {output_png_path}")
        
        


import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import from_bounds
import numpy as np

import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.windows import from_bounds
import logging
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.windows import from_bounds
import logging

def subtract_rasters_based_on_coordinates(dem_path, river_depth_paths, output_path, additional_distance=0):
    """
    Subtracts multiple river depth maps from a DEM, aligning them by their coordinates.
    Optionally subtracts an additional distance at every pixel with non-zero river depth values.
    
    :param dem_path: Path to the DEM GeoTIFF.
    :param river_depth_paths: List of paths to the river depth GeoTIFFs.
    :param output_path: Path to save the resulting GeoTIFF after subtraction.
    :param additional_distance: Distance (in meters) to subtract additionally from non-zero river depth pixels.
    """
    
    # Open the DEM file
    with rasterio.open(dem_path) as dem_src:
        dem_data = dem_src.read(1)
        dem_crs = dem_src.crs
        dem_transform = dem_src.transform
        dem_meta = dem_src.meta
        dem_bounds = dem_src.bounds
    
    # Iterate through each river depth raster and subtract it
    for river_depth_path in river_depth_paths:
        # Open the river depth raster
        with rasterio.open(river_depth_path) as river_src:
            river_depth_data = river_src.read(1)
            river_crs = river_src.crs
            river_transform = river_src.transform
            river_bounds = river_src.bounds
            
            # Check if CRS matches
            if dem_crs != river_crs:
                raise ValueError(f"CRS mismatch: DEM CRS ({dem_crs}) and River Depth CRS ({river_crs}) must be the same.")
            
            # Reproject river depth to match the DEM grid
            reprojected_river_depth = np.empty_like(dem_data, dtype=np.float32)
            reproject(
                river_depth_data,
                reprojected_river_depth,
                src_transform=river_transform,
                src_crs=river_crs,
                dst_transform=dem_transform,
                dst_crs=dem_crs,
                resampling=Resampling.nearest
            )
            
            # Find common bounds and create a cropping window
            common_bounds = (max(dem_bounds[0], river_bounds[0]),  # min x
                             max(dem_bounds[1], river_bounds[1]),  # min y
                             min(dem_bounds[2], river_bounds[2]),  # max x
                             min(dem_bounds[3], river_bounds[3]))  # max y
            window = from_bounds(*common_bounds, transform=dem_transform)
            
            # Crop DEM and reprojected river depth data
            dem_cropped = dem_data[window.toslices()]
            river_depth_cropped = reprojected_river_depth[window.toslices()]
            
            # Match shapes dynamically
            min_rows = min(dem_cropped.shape[0], river_depth_cropped.shape[0])
            min_cols = min(dem_cropped.shape[1], river_depth_cropped.shape[1])
            dem_cropped = dem_cropped[:min_rows, :min_cols]
            river_depth_cropped = river_depth_cropped[:min_rows, :min_cols]
            
            # Subtract the river depth and additional distance from the DEM within the window
            additional_mask = (river_depth_cropped != 0)  # Identify non-zero pixels
            subtraction = river_depth_cropped + (additional_distance * additional_mask)
            dem_cropped -= subtraction
            
            # Update the DEM data within the cropped region
            dem_data[window.toslices()] = np.pad(
                dem_cropped,
                ((0, dem_cropped.shape[0] - min_rows), (0, dem_cropped.shape[1] - min_cols)),
                mode='constant',
                constant_values=0
            )

    # Update metadata and write to output
    dem_meta.update({
        'dtype': 'float32',
        'count': 1  # Single-band raster
    })

    with rasterio.open(output_path, 'w', **dem_meta) as dst:
        dst.write(dem_data, 1)

    logging.info(f"Processed DEM saved at: {output_path}")

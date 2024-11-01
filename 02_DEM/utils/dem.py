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


def create_tiles(input_raster, output_dir, img_format='png', resolution=1, input_crs='EPSG:2056', 
                 height_attribute='hoehe', min_nonzero_value=450, tile_size=512, overlap=256):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the raster file
    with rasterio.open(input_raster) as src:
        raster = src.read(1)  # Read the first band
        width = src.width
        height = src.height
    
    # Calculate the maximum value for normalization
    max_value = raster.max()

    # Normalize the raster to [0, 255]
    raster_normalized = np.where(
        raster > 0,  # Only normalize non-zero values
        (raster - min_nonzero_value) / (max_value - min_nonzero_value) * 255,
        0  # Set background or zero values to 0
    )
    raster_normalized = np.clip(raster_normalized, 0, 255)
    
    # Calculate the step size between tiles based on overlap
    step_size = tile_size - overlap
    
    # Calculate the number of tiles needed in x and y directions with overlap
    num_tiles_x = int(np.ceil((width - overlap) / step_size))
    num_tiles_y = int(np.ceil((height - overlap) / step_size))

    # Loop through each tile
    for tile_x in range(num_tiles_x):
        for tile_y in range(num_tiles_y):
            # Calculate the pixel boundaries for the current tile with overlap
            start_x = tile_x * step_size
            start_y = tile_y * step_size
            end_x = min(start_x + tile_size, width)
            end_y = min(start_y + tile_size, height)
            
            logging.info(f"Processing tile ({tile_y}, {tile_x}): ({start_y}, {end_y}), ({start_x}, {end_x})")

            # Extract the tile from the raster and flip it vertically
            tile = raster_normalized[start_y:end_y, start_x:end_x]
            
            tile = np.flipud(tile)
            

            # Create a tile-sized array with padding where needed
            tile_padded = np.zeros((tile_size, tile_size), dtype=np.uint8)
            tile_padded[-tile.shape[0]:, :tile.shape[1]] = tile.astype(np.uint8)

            #tile_padded = np.flipud(tile_padded)
            
            # Calculate the width and height of one tile in meters
            tile_width_meters = tile_size * src.transform.a
            tile_height_meters = tile_size * abs(src.transform.e)

            logging.info(f"Tile size in meters: {tile_width_meters} x {tile_height_meters}")
            
            if img_format == 'png':
                # Convert the tile to a PIL image and save
                img = Image.fromarray(tile_padded, mode='L')
                img.save(os.path.join(output_dir, f'tile_{tile_y}_{tile_x}.png'))
            
            elif img_format == 'tif':
                # Calculate the transform for the current tile
                transform = from_origin(
                    src.transform.c + start_x * src.transform.a,  # Adjusted west coordinate
                    src.transform.f + start_y * src.transform.e - tile_height_meters,  # Adjusted north coordinate
                    src.transform.a,  # Pixel width
                    src.transform.e   # Pixel height
                )
                # Save the tile as a GeoTIFF
                tile_path = os.path.join(output_dir, f'tile_{tile_y}_{tile_x}.tif')
                with rasterio.open(
                    tile_path,
                    'w',
                    driver='GTiff',
                    height=tile_padded.shape[0],
                    width=tile_padded.shape[1],
                    count=1,
                    dtype=tile_padded.dtype,
                    crs=input_crs,
                    transform=transform,
                ) as dst:
                    dst.write(tile_padded, 1)

    logging.info(f"Tiles saved to {output_dir}")



def stitch_tiles_test(input_dir, output_image, tile_size=512, overlap=256, filename_starts_with='updated_tile'):
    # Gather all tile file names
    tile_files = sorted([
        f for f in os.listdir(input_dir) 
        if f.startswith(filename_starts_with) and (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.tif') or f.endswith('.tiff'))
    ])
    logging.info(f"Found {len(tile_files)} tile files in the input directory")

    # Calculate the number of tiles in x and y based on unique indices in filenames
    num_tiles_x = len(set(int(os.path.splitext(f)[0].split('_')[3]) for f in tile_files))  # unique x values
    num_tiles_y = len(set(int(os.path.splitext(f)[0].split('_')[2]) for f in tile_files))  # unique y values

    logging.info(f"TEST: Number of tiles in x direction: {num_tiles_x}, y direction: {num_tiles_y}")

    # Correctly calculate the dimensions of the stitched image
    stitched_width = (num_tiles_x - 1) * (tile_size - overlap) + tile_size
    stitched_height = (num_tiles_y - 1) * (tile_size - overlap) + tile_size

    logging.info(f"Calculated stitched dimensions: {stitched_width}x{stitched_height}")

    # Initialize cumulative and count arrays for averaging
    cumulative_array = np.zeros((stitched_height, stitched_width), dtype=np.float32)
    count_array = np.zeros((stitched_height, stitched_width), dtype=np.float32)

    # Loop over each tile and place it on the stitched canvas
    for tile_file in tqdm(tile_files):
        # Remove extension and extract tile position from the filename
        base_name = os.path.splitext(tile_file)[0]
        tile_y, tile_x = map(int, base_name.split('_')[2:4])  # from 'updated_tile_y_x'

        # Load the tile image
        tile_path = os.path.join(input_dir, tile_file)
        tile = np.array(Image.open(tile_path))

        # Calculate the position on the stitched image
        start_x = tile_x * (tile_size - overlap)
        start_y = tile_y * (tile_size - overlap)
        end_x = start_x + tile_size
        end_y = start_y + tile_size

        # Boundary check to ensure the tile fits in the stitched array
        if end_x > stitched_width or end_y > stitched_height:
            logging.warning(f"Tile at ({tile_y}, {tile_x}) with position ({start_y}, {end_y}), ({start_x}, {end_x}) exceeds bounds ({stitched_height}, {stitched_width}). Skipping this tile.")
            continue

        # Add the tile to the cumulative array and increment the count array
        cumulative_array[start_y:end_y, start_x:end_x] += tile
        count_array[start_y:end_y, start_x:end_x] += 1

        logging.info(f"Added tile ({tile_y}, {tile_x}) at ({start_y}, {end_y}), ({start_x}, {end_x})")

    # Compute the averaged image by dividing cumulative array by the count array
    stitched_image = np.divide(
        cumulative_array, count_array, out=np.zeros_like(cumulative_array), where=(count_array != 0)
    ).astype(np.uint8)

    # Save the final stitched image
    stitched_img = Image.fromarray(stitched_image, mode='L')
    stitched_img.save(output_image)
    logging.info(f"Stitched image saved as {output_image}")



def geojson_to_tiff(geojson_path, tiff_path, resolution=0.5, input_crs='EPSG:2056', height_attribute='hoehe'):
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
        

    """# Check if CRS is set; if not, assign the input CRS (assuming EPSG:4326 if not provided)
    if gdf.crs is None:
        gdf.set_crs(input_crs, inplace=True)
        logging.info(f"CRS was missing. Set to {input_crs}")

    # Reproject the GeoDataFrame to EPSG:2056
    gdf = gdf.to_crs(epsg=2056)"""


    # Set up the bounds of the raster (based on the geometry bounds)
    minx, miny, maxx, maxy = gdf.total_bounds
    logging.info(f"Bounds: {minx, miny, maxx, maxy}")

    # Define the output raster dimensions (based on the finer resolution)
    width = int((maxx - minx) / resolution)
    height = int((maxy - miny) / resolution)

    # Create an affine transform for the raster
    transform = rasterio.transform.from_bounds(minx, miny, maxx, maxy, width, height)

    # Create an empty array to store the raster data
    raster = np.zeros((height, width), dtype=rasterio.float32)

    # Prepare geometries and corresponding 'hoehe' values for rasterization
    shapes = ((mapping(geom), value) for geom, value in zip(gdf.geometry, gdf[height_attribute]))

    # Rasterize the MultiLineString geometries using the 'hoehe' values
    raster = rasterize(
        shapes=shapes,
        out_shape=raster.shape,
        transform=transform,
        fill=0,  # Background value
        dtype=rasterio.float32
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
        dtype=rasterio.float32,
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

def get_min_height_from_geojson(geojson_path, height_attribute='hoehe'):
    # Read the GeoJSON as a GeoDataFrame
    gdf = gpd.read_file(geojson_path)

    # Ensure the GeoDataFrame has a 'hoehe' column
    if height_attribute not in gdf.columns:
        raise ValueError(f"GeoJSON must have a {height_attribute} attribute for heights")

    # Extract the height column
    heights = gdf[height_attribute]

    # Get the minimum non-zero height value
    min_height = heights[heights > 0].min()

    return min_height


def stitch_tiles(tile_dir, output_image_path, original_width, original_height,filename_starts_with='tile',tile_size=512):
    """
    Stitch 512x512 tiles together to form the original image and remove padding.
    
    Parameters:
    - tile_dir: directory containing the 512x512 tiles
    - output_image_path: path to save the final stitched image
    - original_width: original width of the image (before tiling)
    - original_height: original height of the image (before tiling)
    """
    
    # Get list of all files in the tile directory
    tile_files = sorted(os.listdir(tile_dir))
    
    logging.info(f"Found {len(tile_files)} files in the tile directory")
    
    
    # Initialize a dictionary to store the tiles by their coordinates
    tiles = {}
    
    # Extract tile coordinates from filenames and load the images
    for f in tile_files:
        if f.startswith(filename_starts_with) and (f.endswith('.png') or f.endswith('.jpg') or f.endswith('.tif') or f.endswith('.tiff')):
            logging.info(f"Processing tile: {f}")
            # Extract coordinates from filename (assumed format: tile_y_x.png)
            parts = f.split('_')
            tile_y = int(parts[-2])
            tile_x = int(parts[-1].split('.')[0])
            
            # Load the image and store it in the dictionary
            img = Image.open(os.path.join(tile_dir, f)).transpose(Image.FLIP_TOP_BOTTOM)
            
            # Transpose the image matrix
            #img = img.transpose(Image.Transpose.ROTATE_270)
            # Flip the image horizontally
            #img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            
            tiles[(tile_y, tile_x)] = img
    
    # Calculate how many tiles we have along x and y directions
    num_tiles_x = max(coord[1] for coord in tiles.keys()) + 1
    num_tiles_y = max(coord[0] for coord in tiles.keys()) + 1
    
    # Initialize a large blank array to hold the full stitched image
    stitched_image = np.zeros((num_tiles_y * tile_size, num_tiles_x * tile_size), dtype=np.uint8)
    
    # Paste each tile into the correct position in the stitched image
    for (tile_y, tile_x), img in tiles.items():
        img_array = np.array(img)
        
        start_x = tile_x * tile_size
        start_y = tile_y * tile_size
        
        stitched_image[start_y:start_y + tile_size, start_x:start_x + tile_size] = img_array
    
    # Crop the stitched image to the original width and height (removing any padding)
    #stitched_image_cropped = stitched_image[:original_height, :original_width]
    stitched_image_cropped = stitched_image
    
    # Convert the cropped stitched image back to a PIL image
    final_image = Image.fromarray(stitched_image_cropped)
    
    # Save the final image
    final_image.save(output_image_path)
    
    logging.info(f"Stitched image saved to {output_image_path}")
    logging.info(f"Stitched image saved to {output_image_path}")


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
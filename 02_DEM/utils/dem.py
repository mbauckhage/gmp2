import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from shapely.geometry import mapping
import numpy as np
from PIL import Image
import os
import logging




import os
import numpy as np
import rasterio
from rasterio.transform import from_origin
from PIL import Image

def create_tiles(input_raster, output_dir, img_format='png', resolution=1, input_crs='EPSG:2056', 
                 height_attribute='hoehe', min_nonzero_value=450, tile_size=512):
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
    
    # Calculate the number of tiles needed in x and y directions
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
            
            print(f"Processing tile ({tile_y}, {tile_x}): ({start_y}, {end_y}), ({start_x}, {end_x})")

            # Extract the tile from the raster and flip it vertically
            tile = raster_normalized[start_y:end_y, start_x:end_x]
            
            tile = np.flipud(tile)
            

            # Create a tile-sized array with padding where needed
            tile_padded = np.zeros((tile_size, tile_size), dtype=np.uint8)
            tile_padded[-tile.shape[0]:, :tile.shape[1]] = tile.astype(np.uint8)

            #tile_padded = np.flipud(tile_padded)
            
            
            if img_format == 'png':
                # Convert the tile to a PIL image and save
                img = Image.fromarray(tile_padded, mode='L')
                img.save(os.path.join(output_dir, f'tile_{tile_y}_{tile_x}.png'))
            
            elif img_format == 'tif':
                # Calculate the transform for the current tile
                transform = from_origin(
                    src.transform.c + start_x * src.transform.a,  # Adjusted west coordinate
                    src.transform.f + start_y * src.transform.e,  # Adjusted north coordinate
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

    print(f"Tiles saved to {output_dir}")


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
        print(f"CRS was missing. Set to {input_crs}")

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

def geojson_to_png_tiles(geojson_path, output_dir, resolution=0.5, input_crs='EPSG:2056', height_attribute='hoehe',min_nonzero_value=450):
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
        print(f"CRS was missing. Set to {input_crs}")

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
    num_tiles_x = int(np.ceil(width / 512))
    num_tiles_y = int(np.ceil(height / 512))

    # Loop through each tile
    for tile_x in range(num_tiles_x):
        for tile_y in range(num_tiles_y):
            # Calculate the pixel boundaries for the current tile
            start_x = tile_x * 512
            start_y = tile_y * 512
            end_x = min(start_x + 512, width)
            end_y = min(start_y + 512, height)

            # Extract the tile from the raster
            tile = raster_normalized[start_y:end_y, start_x:end_x]

            # Create a 512x512 image (pad with zeros if the tile is smaller)
            tile_padded = np.zeros((512, 512), dtype=np.uint8)
            tile_padded[:tile.shape[0], :tile.shape[1]] = tile.astype(np.uint8)

            # Convert the tile to a PIL image
            img = Image.fromarray(tile_padded, mode='L')  # 'L' for grayscale

            # Save the image with a filename based on the tile indices
            img.save(os.path.join(output_dir, f'tile_{tile_y}_{tile_x}.png'))


    print(f"Tiles saved to {output_dir}")

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


def stitch_tiles(tile_dir, output_image_path, original_width, original_height,filename_starts_with='tile'):
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
            img = Image.open(os.path.join(tile_dir, f))
            
            # Transpose the image matrix
            img = img.transpose(Image.Transpose.ROTATE_270)
            # Flip the image horizontally
            img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            
            tiles[(tile_y, tile_x)] = img
    
    # Calculate how many tiles we have along x and y directions
    num_tiles_x = max(coord[1] for coord in tiles.keys()) + 1
    num_tiles_y = max(coord[0] for coord in tiles.keys()) + 1
    
    # Initialize a large blank array to hold the full stitched image
    stitched_image = np.zeros((num_tiles_y * 512, num_tiles_x * 512), dtype=np.uint8)
    
    # Paste each tile into the correct position in the stitched image
    for (tile_y, tile_x), img in tiles.items():
        img_array = np.array(img)
        
        start_x = tile_x * 512
        start_y = tile_y * 512
        
        stitched_image[start_y:start_y + 512, start_x:start_x + 512] = img_array
    
    # Crop the stitched image to the original width and height (removing any padding)
    stitched_image_cropped = stitched_image[:original_height, :original_width]
    
    # Convert the cropped stitched image back to a PIL image
    final_image = Image.fromarray(stitched_image_cropped)
    
    # Save the final image
    final_image.save(output_image_path)
    
    print(f"Stitched image saved to {output_image_path}")
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
    print(f"Adjusted heightmap saved to {output_path}")

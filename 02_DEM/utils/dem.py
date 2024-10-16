import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from shapely.geometry import mapping
import numpy as np
from PIL import Image
import os


def geojson_to_tiff(geojson_path, tiff_path, resolution=0.5, input_crs='EPSG:2056', height_attribute='hoehe'):
    # Read the GeoJSON as a GeoDataFrame
    gdf = gpd.read_file(geojson_path)

    # Ensure the GeoDataFrame has a 'hoehe' column
    if height_attribute not in gdf.columns:
        raise ValueError(f"GeoJSON must have a {height_attribute} attribute for heights")

    # Check if CRS is set; if not, assign the input CRS (assuming EPSG:4326 if not provided)
    if gdf.crs is None:
        gdf.set_crs(input_crs, inplace=True)
        print(f"CRS was missing. Set to {input_crs}")

    # Reproject the GeoDataFrame to EPSG:2056
    gdf = gdf.to_crs(epsg=2056)

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

    # Check if CRS is set; if not, assign the input CRS (assuming EPSG:4326 if not provided)
    if gdf.crs is None:
        gdf.set_crs(input_crs, inplace=True)
        print(f"CRS was missing. Set to {input_crs}")

    # Reproject the GeoDataFrame to EPSG:2056
    gdf = gdf.to_crs(epsg=2056)

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



import geopandas as gpd

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

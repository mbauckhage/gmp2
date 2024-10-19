import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from shapely.geometry import LineString
from scipy.ndimage import distance_transform_edt
from rasterio.transform import from_bounds
from shapely.geometry import mapping
import os
import logging

# Use relative import for general_functions
from .general_functions import ensure_directory_exists



import geopandas as gpd
import rasterio
import numpy as np
from rasterio.features import rasterize
from shapely.geometry import mapping
from scipy.ndimage import distance_transform_edt
import logging

def polygons_to_depth_raster(river_shapefile, output_raster, resolution, max_depth=2.0, input_crs='EPSG:21781',overwrite=False):
    """
    Convert polygons (e.g. rivers, lakes) to a raster with depth gradient (deeper in the middle of the rivers).
    
    Parameters:
    - river_shapefile: Path to the river shapefile (polygon)
    - output_raster: Path where the output raster will be saved
    - resolution: Spatial resolution of the output raster
    - max_depth: Maximum depth at the center of the river
    
    Output:
    A raster with depth gradient for riverbeds.
    """
    
    # Check if the output raster already exists and handle the overwrite flag
    if os.path.exists(output_raster):
        if overwrite:
            logging.info(f"{output_raster} already exists and will be overwritten.")
        else:
            logging.info(f"{output_raster} already exists and overwrite is set to False. Exiting.")
            return
    
    
    logging.info(f"Creating river depth raster from {river_shapefile}")
    
    # Load river shapefile as a GeoDataFrame
    gdf = gpd.read_file(river_shapefile)
    logging.info(f"Loaded {len(gdf)} polygons from the shapefile")

    if gdf.crs is None:
        gdf.set_crs(input_crs, inplace=True)
        logging.info(f"CRS was missing. Set to {input_crs}")

    # Filter out geometries that are None or invalid
    valid_gdf = gdf[gdf.geometry.notnull() & gdf.is_valid]
    invalid_count = len(gdf) - len(valid_gdf)
    if invalid_count > 0:
        logging.warning(f"Filtered out {invalid_count} invalid geometries")
    
    if valid_gdf.empty:
        raise ValueError("No valid geometries found in the shapefile")

    # Set up the bounds of the raster (based on the geometry bounds)
    minx, miny, maxx, maxy = valid_gdf.total_bounds

    # Define the output raster dimensions (based on the finer resolution)
    width = int((maxx - minx) / resolution)
    height = int((maxy - miny) / resolution)

    logging.info("Transform raster")
    # Create an affine transform for the raster
    transform = rasterio.transform.from_bounds(minx, miny, maxx, maxy, width, height)

    # Create an empty array to store the raster data
    raster = np.zeros((height, width), dtype=rasterio.float32)

    # Prepare geometries and corresponding 'hoehe' values for rasterization
    shapes = ((mapping(geom), 1) for geom in valid_gdf.geometry)

    logging.info("Rasterize shapes")
    # Rasterize the polygons using a value of 1
    raster = rasterize(
        shapes=shapes,
        out_shape=raster.shape,
        transform=transform,
        fill=0,  # Background value
        dtype=rasterio.float32
    )

    logging.info("Calculate distance to edge")
    # Calculate Euclidean distance to the nearest edge of the river polygons
    distance_to_edge = distance_transform_edt(raster)

    # Normalize the distance to create a gradient from the river edge (0 depth) to the center (max depth)
    max_distance = distance_to_edge.max()
    depth_gradient = max_depth * (distance_to_edge / max_distance)

    # Apply the river mask (depth only inside river polygons)
    river_depth_raster = np.where(raster == 1, depth_gradient, 0)

    logging.info("Write raster to file")
    # Write the depth raster to a GeoTIFF file
    with rasterio.open(
        output_raster,
        'w',
        driver='GTiff',
        height=height,
        width=width,
        count=1,
        dtype=rasterio.float32,
        crs=gdf.crs,
        transform=transform
    ) as dst:
        dst.write(river_depth_raster, 1)

    print(f"River depth raster saved to {output_raster}")
    logging.info(f"River depth raster saved to {output_raster}")


def get_bounding_box_from_shp(shapefile):
    
    # Load the shapefile as a GeoDataFrame
    gdf = gpd.read_file(shapefile)
    # Get the bounding box of the geometries in the shapefile
    minx, miny, maxx, maxy = gdf.total_bounds
    print(f"Bounding box: minx={minx}, miny={miny}, maxx={maxx}, maxy={maxy}")
    return (minx, miny, maxx, maxy)


def save_channel_as_binary(input_raster, output_dir,output_filename,output_crs='EPSG:21781'):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Open the input raster file
    with rasterio.open(input_raster) as src:
        # Read the raster data as a numpy array (all channels)
        raster_data = src.read()  # This will have shape (channels, height, width)

        # Get metadata from the source file
        meta = src.meta.copy()
        
        # Update the CRS to the desired output CRS
        meta.update(crs=output_crs)

        # Loop over each channel and save it as a binary raster
        for channel in range(raster_data.shape[0]):
            # Extract the channel (1-based index for channel)
            channel_data = raster_data[channel]

            # Convert the channel data to binary (0 or 1)
            binary_data = np.where(channel_data > 0, 1, 0).astype(np.uint8)

            # Update the metadata to reflect a single channel output
            meta.update(count=1, dtype=rasterio.uint8)

            # Define output filename based on the channel
            channel_name = ['stream', 'wetland', 'river', 'lake'][channel]
            ensure_directory_exists(output_dir+channel_name+'/'+output_filename.split("_")[0]+"_"+output_filename.split("_")[1])
            output_file = os.path.join(output_dir+channel_name, output_filename)
            print(output_file)
            # Write the binary raster to file
            with rasterio.open(output_file, 'w', **meta) as dst:
                dst.write(binary_data, 1)  # Write the binary data to the first band

            print(f'Saved {channel_name} as binary raster: {output_file}')


import geopandas as gpd
import rasterio
import numpy as np
from rasterio.features import rasterize
from shapely.geometry import mapping

def shape_to_tiff(shapefile_path, tiff_path, resolution=0.5, input_crs='EPSG:2056'):
    """
    Converts a Shapefile to a GeoTIFF raster, where the geometry is rasterized and the heights are taken 
    from a specified attribute.

    Parameters:
    - shapefile_path (str): Path to the input Shapefile.
    - tiff_path (str): Path to save the output GeoTIFF.
    - resolution (float): Resolution of the output raster (in units of the CRS, typically meters).
    - input_crs (str): The coordinate reference system to use if not provided in the Shapefile.
    - height_attribute (str): The attribute from the Shapefile used to fill the raster with heights.
    """

    # Read the Shapefile as a GeoDataFrame
    gdf = gpd.read_file(shapefile_path)


    # Check if CRS is set; if not, assign the input CRS
    if gdf.crs is None:
        gdf.set_crs(input_crs, inplace=True)
        print(f"CRS was missing. Set to {input_crs}")

    # Reproject the GeoDataFrame to EPSG:2056 if needed
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
    shapes = ((mapping(geom), value) for geom, value in zip(gdf.geometry))

    # Rasterize the geometries using the 'hoehe' values
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

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
from rasterio.windows import from_bounds
from rasterio.merge import merge
from rasterio.enums import Resampling
from rasterio.warp import reproject, calculate_default_transform
from rasterio.features import shapes
from shapely.geometry import shape
from shapely.geometry import Polygon
from tqdm import tqdm
import shapefile  # pyshp library
import pyproj  # For handling CRS
import pandas as pd


# Use relative import for general_functions
from .general_functions import ensure_directory_exists



def assign_crs(tiff_file, target_crs='EPSG:21781'):
    with rasterio.open(tiff_file) as src:
        if src.crs is None:
            print(f"Assigning CRS to {tiff_file}")
            transform, width, height = calculate_default_transform(
                src.crs if src.crs else target_crs, target_crs, src.width, src.height, *src.bounds
            )
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': target_crs,
                'transform': transform,
                'width': width,
                'height': height
            })
            # Save the reprojected version
            reprojected_path = tiff_file.replace(".tif", "_reprojected.tif")
            with rasterio.open(reprojected_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=target_crs,
                        resampling=Resampling.nearest
                    )
            return reprojected_path
        else:
            return tiff_file





def polygons_to_raster(river_shapefile, output_raster, resolution, input_crs='EPSG:21781',overwrite=False):
    
    """
    Convert polygons (e.g., rivers, lakes) to a binary raster.

    Parameters:
    - river_shapefile: Path to the river shapefile (polygon).
    - output_raster: Path where the output raster will be saved.
    - resolution: Spatial resolution of the output raster.
    - input_crs: Coordinate reference system of the input shapefile (default is 'EPSG:21781').
    - overwrite: Boolean flag to allow overwriting the output raster if it already exists (default is False).

    Output:
    A binary raster where the polygons are represented with a value of 1 and the background with a value of 0.
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
        logging.warning("No valid geometries found in the shapefile")
        return

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
        dst.write(raster, 1)

    print(f"River depth raster saved to {output_raster}")
    logging.info(f"River depth raster saved to {output_raster}")



def depth_raster(input_raster, output_raster, max_depth=2):
    

    # Read the raster from the GeoTIFF file
    with rasterio.open(input_raster) as src:
        raster = src.read(1)

    logging.info("Calculate distance to edge")
    # Calculate Euclidean distance to the nearest edge of the river polygons
    distance_to_edge = distance_transform_edt(raster)
    depth_gradient = distance_to_edge / 5

    # Cap the depth gradient at max_depth
    depth_gradient = np.clip(depth_gradient, 0, max_depth)


    # Apply the river mask (depth only inside river polygons)
    river_depth_raster = np.where(raster == 1, depth_gradient, 0)

    logging.info(f"Write raster to file {output_raster}")
    # Write the depth raster to a GeoTIFF file
    with rasterio.open(
        output_raster,
        'w',
        driver='GTiff',
        height=raster.shape[0],
        width=raster.shape[1],
        count=1,
        dtype=rasterio.float32,
        crs=src.crs,
        transform=src.transform
    ) as dst:
        dst.write(river_depth_raster, 1)

    logging.info(f"River depth raster saved to {output_raster}")



def polygons_to_depth_raster(river_shapefile, output_raster, resolution, max_depth=2, input_crs='EPSG:21781',overwrite=False):
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
    depth_gradient = distance_to_edge / 5
    
    # Cap the depth gradient at max_depth
    depth_gradient = np.clip(depth_gradient, 0, max_depth)
    

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


        logging.info(f"Raster data shape: {raster_data.shape}")
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

def stitch_geotiffs(tiff_files, output_path, crs='EPSG:21781'):
    """
    Stitches together multiple GeoTIFF files based on their coordinates.
    Fills non-overlapping areas with zeros.
    
    :param tiff_files: List of paths to input GeoTIFF files.
    :param output_path: Path to save the stitched output GeoTIFF file.
    """
    
    logging.info(f"Stitching {len(tiff_files)} GeoTIFF files")
    
    
    for file in tiff_files:
        with rasterio.open(file) as src:
            logging.info(f"\nFile: {file}")
            logging.info(f"CRS: {src.crs}")
            logging.info(f"Transform: {src.transform}")
            logging.info(f"Bounds: {src.bounds}")
            logging.info(f"Width, Height: {src.width}, {src.height}")
            logging.info(f"Is Georeferenced: {'No' if src.crs is None or src.transform == rasterio.Affine.identity() else 'Yes'}\n")

    # List to store opened raster objects
    src_files_to_mosaic = []

    # Open each GeoTIFF file
    for tiff_file in tiff_files:
        src = rasterio.open(tiff_file)
        src_files_to_mosaic.append(src)
    
    # Use `merge` to stitch rasters together
    # fill_value=0 will fill the non-overlapping areas with zero
    mosaic, out_transform = merge(src_files_to_mosaic)
    
    logging.info(f"Read CRS: {src_files_to_mosaic[0].crs}")
    logging.info(f"Set CRS to: {crs}")

    # Update metadata for the output file
    out_meta = src_files_to_mosaic[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform,
        "compress": "lzw",  # Optional: compression to save space
        "crs": crs
    })
    
    # Write the mosaic to the output file
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)
    
    # Close all open source files
    for src in src_files_to_mosaic:
        src.close()
        
    logging.info(f"Stitched GeoTIFF saved to: {output_path}")


def clip_geotiff(input_tiff, output_tiff, clip_extent):
    """
    Reads a GeoTIFF and clips it to the specified extent.
    
    :param input_tiff: Path to the input GeoTIFF file.
    :param output_tiff: Path to save the clipped GeoTIFF file.
    :param clip_extent: Tuple of (min_x, min_y, max_x, max_y) representing the clipping bounds.
    """

    # Open the input GeoTIFF
    with rasterio.open(input_tiff) as src:
        # Get the bounding box (clip extent)
        min_x, min_y, max_x, max_y = clip_extent
        
        # Create a window based on the given bounds
        window = from_bounds(min_x, min_y, max_x, max_y, src.transform)
        
        # Convert the window to integer indices
        row_off = int(window.row_off)
        col_off = int(window.col_off)
        height = int(window.height)
        width = int(window.width)
        
        # Read the windowed data
        clipped_data = src.read(window=window)

        # Update the transform for the clipped window
        clipped_transform = src.window_transform(window)
        
        # Update metadata for the output file
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": height,
            "width": width,
            "transform": clipped_transform
        })
        
        # Write the clipped data to the output file
        with rasterio.open(output_tiff, "w", **out_meta) as dest:
            dest.write(clipped_data)
            
        logging.info(f"Clipped GeoTIFF saved to: {output_tiff}")


def get_extent_from_tiff(tiff_file):
    """
    Get the extent of a GeoTIFF file in the form of (min_x, min_y, max_x, max_y).
    
    :param tiff_file: Path to the input GeoTIFF file.
    :return: Tuple of (min_x, min_y, max_x, max_y) representing the extent.
    """
    
    with rasterio.open(tiff_file) as src:
        bounds = src.bounds
        xmin, ymin, xmax, ymax = bounds.left, bounds.bottom, bounds.right, bounds.top

    clip_extent = (xmin, ymin, xmax, ymax)
    
    return clip_extent



def binary_raster_to_shp(raster_path, shapefile_path, epsg_code=None, tolerance=0.01):
    """
    Converts a binary raster to a shapefile with geometries as MultiPolygonZ and optional CRS.

    Args:
        raster_path (str): Path to the binary raster file.
        shapefile_path (str): Path to save the shapefile.
        epsg_code (int, optional): EPSG code to define the CRS for the output.
        tolerance (float): Tolerance for simplification. Larger values simplify more.
    """
    import rasterio
    from rasterio.features import shapes
    from shapely.geometry import shape, MultiPolygon, Polygon
    import geopandas as gpd

    # Step 1: Read the binary raster
    with rasterio.open(raster_path) as src:
        raster_data = src.read(1)  # Read the first band
        transform = src.transform
        raster_crs = src.crs

    # Step 2: Extract shapes (vectorize)
    shapes_gen = shapes(raster_data, transform=transform)

    # Prepare the geometries list
    geometries = []

    for geom, value in shapes_gen:
        if value:  # Only process regions where value is 1 (binary 'on')
            polygon = shape(geom)

            # Simplify the geometry (reduce vertices and smooth edges)
            simplified_polygon = polygon.simplify(tolerance, preserve_topology=True)

            # Convert to MultiPolygon if necessary
            if isinstance(simplified_polygon, Polygon):
                simplified_polygon = MultiPolygon([simplified_polygon])

            # Convert to MultiPolygonZ (add Z-dimension with a default value of 0.0)
            multipolygonz = MultiPolygon([
                Polygon(
                    # Add Z dimension to exterior coordinates
                    [(x, y, 0.0) for x, y in poly.exterior.coords],
                    # Add Z dimension to each interior ring
                    [[(x, y, 0.0) for x, y in ring.coords] for ring in poly.interiors]
                )
                for poly in simplified_polygon.geoms
            ])

            # Append to geometries list
            geometries.append({"geometry": multipolygonz, "properties": {"value": int(value)}})

    # Step 3: Create GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(geometries)

    # Assign CRS
    if epsg_code:
        gdf.set_crs(epsg=epsg_code, inplace=True)
    elif raster_crs:
        gdf.set_crs(raster_crs, inplace=True)
    else:
        raise ValueError("No CRS information available. Please provide an EPSG code.")

    # Save the GeoDataFrame as a shapefile
    gdf.to_file(shapefile_path)

    print(f"Shapefile saved at: {shapefile_path}")


def prepare_shp_for_unity(input_shapefile, layer_params, output_shapefile=None,print_info=False):
    if output_shapefile is None:
        output_shapefile = input_shapefile

    # Validate input file
    if not os.path.exists(input_shapefile):
        raise FileNotFoundError(f"Input shapefile not found: {input_shapefile}")

    # Read the input shapefile using GeoPandas
    gdf = gpd.read_file(input_shapefile, engine='fiona')

    # Check if the CRS is set correctly. If it's not set, assign the CRS.
    if gdf.crs is None:
        if print_info: print(f"No CRS found. Assigning CRS to EPSG:21781")
        gdf.set_crs(epsg=21781, allow_override=True, inplace=True)
    else:
        if print_info: print(f"CRS already set")

    # Ensure the geometries are Polygons (if needed)
    gdf['geometry'] = gdf['geometry'].apply(lambda geom: geom if isinstance(geom, Polygon) else None)
    
    # Filter out polygons with an area less than the threshold
    gdf = gdf[gdf['geometry'].area >= layer_params['filter_area']]
    
    # Create a new GeoDataFrame with only the desired columns
    layer_attributes = layer_params['attributes']
    new_gdf = gpd.GeoDataFrame({
        'ID': range(1, len(gdf) + 1),  # Assign unique IDs starting from 1
        'LAYER': layer_attributes['layer'],
        'NAME': layer_attributes['name'],
        'building': layer_attributes['building'],
        'place': layer_attributes['place'],
        'leisure': layer_attributes['leisure'],
        'grass': layer_attributes['grass'],
        'geometry': gdf['geometry']  # Retain geometry
    }, crs=gdf.crs)  # Retain CRS

    # Save the modified GeoDataFrame as a new shapefile, which will automatically write the CRS.
    new_gdf.to_file(output_shapefile)

    if print_info: print(f"Modified shapefile saved to {output_shapefile}")



def merge_shapefiles(shapefile_list, output_shapefile, print_info=False):
    """
    Merges multiple shapefiles into one.

    Parameters:
        shapefile_list (list): List of input shapefile paths.
        output_shapefile (str): Path to save the merged shapefile.
    """
    # Check if all files exist
    for shapefile in shapefile_list:
        if not os.path.exists(shapefile):
            raise FileNotFoundError(f"Shapefile not found: {shapefile}")

    # Read and merge shapefiles
    gdfs = []
    for shapefile in shapefile_list:
        gdf = gpd.read_file(shapefile)
        gdfs.append(gdf)

    # Combine all GeoDataFrames
    merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs=gdfs[0].crs)
    
    merged_gdf['ID'] = range(1, len(merged_gdf) + 1)

    # Save the merged shapefile
    merged_gdf.to_file(output_shapefile)
    if print_info: print(f"Merged shapefile saved to {output_shapefile}")


import shutil

def copy_file(source_file, destination_dir):
    """
    Copies a file from source to destination directory.

    Parameters:
        source_file (str): Path to the source file.
        destination_dir (str): Path to the destination directory.
    """
    try:
        # Perform the copy
        shutil.copy(source_file, destination_dir)
        print(f"File copied from {source_file} to {destination_dir}")
    except FileNotFoundError:
        print(f"Source file not found: {source_file}")
    except PermissionError:
        print(f"Permission denied. Could not copy to: {destination_dir}")
    except Exception as e:
        print(f"An error occurred: {e}")



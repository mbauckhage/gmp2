import shutil
import geopandas as gpd
import pandas as pd
import os
from shapely.geometry import Polygon


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
        'waterway': layer_attributes['waterway'],
        'natural': layer_attributes['natural'],
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
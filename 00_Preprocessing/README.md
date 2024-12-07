# Preprocessing

## Stitch Tiff Files

The following file structure is expected:

    .
    ├─ folder_path                   # Compiled files (alternatively `dist`)
    ├── rgb_TA_315
    ├──── rgb_TA_315_1878.tif
    ├──── rgb_TA_315_1899.tif
    ├──── rgb_TA_315_...
    ├── rgb_TA_318
    ├──── rgb_TA_318_1878.tif
    ├──── rgb_TA_318_...

`main_stitchTiff.py`

This script stitches together multiple GeoTIFF files, reprojects them if necessary, and assigns a Coordinate Reference System (CRS) to ensure proper alignment. It processes raster data for specified geographical areas and years, saving the stitched output as new GeoTIFF files.

- Define the paths
- Run the script to process and stitch the files.
- Check the output in the output_base_path directory.
- Review logs for progress and errors.

## Clip Tiff Files

`main_clip.py`

This script clips all file from a proved directory to the extent of a given GeoTIFF.

## Resample Resolution of Tiff Files

`main_fix_resolution.py`

This script resamples GeoTIFF files by changing their resolution and saves the resampled files in a specified output directory. It uses the rasterio library to read, reproject, and resample raster data to a new resolution.

## Split Channels of Image into Binary Rasters

`main_splitChannels.py`

This script splits channels of tiff file into binary rasters.

## Rasterize Shape Files

`main_shp2raster.py`

This script rasterizes shape files.

## Depth Maps for Raster Images and Shapefiles

`main_depthMap.py`

This script takes either raster or shapefile and calculates a depth map. The raster input needs to be binary. A max depth needs to be set.

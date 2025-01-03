# Modelling Historical River Landscape Evolution in Virtual Reality (VR)

## Geomatic Master Project 2

The objective of this project is to develop a virtual reality platform that enables users to journey through time and witness the evolution of river landscapes with immersive experiences. A workflow is to be created and implemented, which shows the process to get from a historical topographic map to a 3D modelled landscape in a VR environment. The workflow should be reproducible and allow to be used for different area of interest and with different historic maps.

The following steps will be implemented:

1. Contour lines image segmentation (_01_Segmentation_)
2. ...

### Preprocessing

#### Rasterize Shape Files

`pp_00_A_main_shp2raster.py`

This script rasterizes shape files.

#### Split Channels of Image into Binary Rasters

`pp_00_B_main_splitChannels.py`

This script splits channels of tiff file into binary rasters.

#### Stitch Tiff Files

`pp_01_main_stitchTiffs.py`

This script stitches together multiple GeoTIFF files, reprojects them if necessary, and assigns a Coordinate Reference System (CRS) to ensure proper alignment. It processes raster data for specified geographical areas and years, saving the stitched output as new GeoTIFF files.

- Define the paths
- Run the script to process and stitch the files.
- Check the output in the output_base_path directory.
- Review logs for progress and errors.

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

#### Clip Tiff Files

`pp_02_main_clip.py`

This script clips all file from a proved directory to the extent of a given GeoTIFF.

#### Optional: Improve Road Annotations

`pp_03_A_main_fixRoads.py`

The roads are not very clean in the binary raster. They are not binary, but have values between 0 and 1.
This script cleans the binary raster by setting all values < 0.65 to 0 and all values >= 0.65 to 1.
This scriipt also applies morphological operations to remove small objects and fill small holes.

#### Resample Resolution of Tiff Files

`pp_03_B_main_fix_resolution.py`

This script resamples GeoTIFF files by changing their resolution and saves the resampled files in a specified output directory. Resampling simplifies subsequent steps and ensures that all files work with the same resolution. It uses the rasterio library to read, reproject, and resample raster data to a new resolution.

#### Optional: Fill small holes in River Annotations

`pp_03_C_main_morphology.py`

#### Convert back to ShapeFile

`pp_03_D_main_raster2shape.py`

All the raster files are converted into vector data (Shapefiles), as the Unity Package `GIS Terrain Loader Pro` takes Shapefiles as input.

"""

#### Depth Maps for Raster Images and Shapefiles

`main_depthMap.py`

This script takes either raster or shapefile and calculates a depth map. The raster input needs to be binary. A max depth needs to be set.
"""

### Unity Preperation

#### Raster and DEM preparation

`pp_05_main_data4unity.py`

This script is used to prepare the textures and DEM for the Unity application to fit the input of the `GIS Terrain Loader Pro`.

#### Vector Data preperation

Vector Data preparation for Unity Package `GIS Terrain Loader Pro`

`pp_05_main_shp4unity.py`

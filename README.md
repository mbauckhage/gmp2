# Modelling Historical River Landscape Evolution in Virtual Reality (VR)

## Geomatic Master Project 2

The objective of this project is to develop a virtual reality platform that enables users to journey through time and witness the evolution of river landscapes with immersive experiences. A workflow is to be created and implemented, which shows the process to get from a historical topographic map to a 3D modelled landscape in a VR environment. The workflow should be reproducible and allow to be used for different area of interest and with different historic maps.

The following steps will are implemented:

- 00_Preprocessing: Preparing all data for further processing steps
- 01_Segmentation: Contour lines image segmentation
- 02_DEM: Creating a DEM based on the extracted contour lines
- 03_Texture: Creating textures based on vector annotaions and texture samples
- 04_Unity_Preperation: prepare data for GIS Terrain Loader Pro in Unity
- 05_Unity: Unity projects for the creation of the landscape and the build of the VR applicaiton

---

### 00 Preprocessing

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

#### Depth Maps for Raster Images and Shapefiles

`pp_04_main_depthMap.py`

This script takes either raster or shapefile and calculates a depth map. The raster input needs to be binary. A max depth needs to be set.

---

### 01 Segmentation of Contour Lines

#### Extracting Contour Lines from Map

`se_00_main_segmentation.py`

This script is the main script for the segmentation of the maps. Start the script, select the seed point and the script will segment the map and save the skeleton as a geojson file.

#### Assigning heights of Contour Lines based on existing contour lines.

`se_01_main_assign_heights.py`

Use exisitng contour line heights to assign heights to the skeleton.

---

### 02 Digital Elevation Model (DEM)

#### Geojson to TIFF

`dem_01_main_geojson2tiff.py`

This script is used to convert a geojson file to a tiff file, which later will be used to create the DEM using grid interpolation.

#### Grid Interpolation

`dem_02_main_interpolation.py`

This script interpolates the height map from the skeleton using grid interpolation.

#### Fix resolutions

`dem_03_main_resolution_fix.py`

This script is used to resample the geotiff files to a new resolution, to allow river subtraction in the following step.

#### River subtraction

`dem_04_main_river_subtraction.py`

This script subtracts the depth maps (rivers, lakes, etc.) from the DEMs and saves the result as a new raster file.

---

### 03 Texture

#### Quill images

`tex_01_main_texture_synthesis.py`

This script is used to quill a texture image to a desired size based on the reference image.

#### Create Terrain Textures

`tex_02_main_create_textures.py`

This script is used to create the textures for the quilt images using vector annoations.

#### Georeference Textures

`tex_03_main_georeference_textures.py`

This script georeferences all PNG files in the input directory using the corner coordinates and CRS from a reference GeoTIFF.

### 04 Unity Preperation

---

#### Raster and DEM preparation

`pp_05_main_data4unity.py`

This script is used to prepare the textures and DEM for the Unity application to fit the input of the `GIS Terrain Loader Pro`.

#### Vector Data preperation

Vector Data preparation for Unity Package `GIS Terrain Loader Pro`

`pp_05_main_shp4unity.py`

### 05 Unity

---

The project `Landscape_Builder` was used to create the temporal landscapes in full-scale and small-scale.

The scripts used are located inside the asset folder: `/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/05_Unity/Landscape_Builder/Assets/Scripts`

The project `VR_Temporal_Landscapes` contains the final VR application.

#### TerrainCreation

The following scripts are used to scale the terrain and its objects:

- `ScalerManager.cs`
- `IScaler.cs`
- `WaterScaler.cs`
- `AdjustTerrainResolution.cs`

The following script is used to create the assign the water texture to a mesh:

- `AssignMeshesToWaterSurface.cs`

#### VR_Interaction

These scripts are used in runtime for the VR application:

- `SceneLoader.cs`
- `TerrainCycler.cs`

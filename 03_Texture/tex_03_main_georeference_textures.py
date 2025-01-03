from tqdm import tqdm
import os
from utils.georeferencing import georeference_png

"""
This script georeferences all PNG files in the input directory using the corner coordinates and CRS from a reference GeoTIFF.
"""




base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_dir = "04_textures/"

reference_geotiff = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/01_Segmentation/data/Siegfried.tif"


input_folder = base_path + input_dir
for filename in tqdm(os.listdir(input_folder)):
    if filename.endswith(".png") and not filename.startswith("._") and not 'squared' in filename:
       
        input_png = os.path.join(input_folder, filename)
        output_geotiff = input_png.replace('.png', '.tif')

        georeference_png(input_png, reference_geotiff, output_geotiff)

from utils.dem import *


input_geojson_path = "data/test_lines.geojson"
output_tiff_path = "output/output_height_raster.tiff"

geojson_to_tiff(input_geojson_path, output_tiff_path,resolution=0.1, input_crs='EPSG:2056', height_attribute='height')
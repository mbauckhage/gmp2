from utils.dem import *


input_geojson_path = "data/test_lines.geojson"
output_tiff_path = "output/output_height_raster.tiff"
output_png_path = "output/"


min_height = get_min_height_from_geojson(input_geojson_path)

print(min_height)
#geojson_to_tiff(input_geojson_path, output_tiff_path,resolution=0.1, input_crs='EPSG:2056', height_attribute='hoehe')
geojson_to_png_tiles(input_geojson_path, output_png_path,resolution=0.1, input_crs='EPSG:2056', height_attribute='hoehe',min_nonzero_value=min_height)
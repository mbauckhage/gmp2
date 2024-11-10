from utils.raster_interpolation import * 
from utils.general_functions import *

# File path
# -----------------------------------------------
base_path = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/"

input_dir = 'raster_contour_lines/'
output_dir = 'dem_interpolation/'

input_raster_path = "height_map_old_national_1975.png"
output_raster_path = "height_map_old_national_1975_interpolated.tif"

# -----------------------------------------------

input_raster_path_ = base_path + input_dir + input_raster_path
output_raster_path_ = base_path + output_dir + output_raster_path

ensure_directory_exists(base_path + output_dir)


interpolate_raster(input_raster_path_, output_raster_path_, method='linear')
make_img_square(output_raster_path_.replace(".tif",".png"), output_raster_path_.replace('.tif', '_squared.png'))
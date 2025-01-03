from utils.dem import *
from utils.general_functions import ensure_directory_exists
from datetime import datetime

# Define the directories
base_dir = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/02_DEM/output/"
#reference_dir = base_dir + "tiles_height_map_old_national_1975_20241031_153817/tif/"
input_dir = base_dir + "tiles_height_map_old_national_1975_20241107_174806/heightMaps/"
#set_crs_output_dir = base_dir + "tiles_height_map_old_national_1975_20241031_153817/HeightMaps_crs_fix/"
set_flip_output_dir = base_dir + "tiles_height_map_old_national_1975_20241107_174806/heightMaps_flip/"



# Setup logging
# -----------------------------------------------
log_directory = "/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/logs/dem/"
ensure_directory_exists(log_directory)
log_file = os.path.join(log_directory, f"preprocessing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

#set_crs_for_tiles(reference_dir, input_dir, set_crs_output_dir)
rotate_and_flip_tif(input_dir, set_flip_output_dir)
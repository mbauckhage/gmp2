from utils.texture_fill import fill_masks, make_black_pixels_transparent
from utils.raster_functions import make_img_square


# Define the paths to the binary masks and quilt images
# -------------------------------------------------------
base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_masking = "03_resampled/"
input_for_quilling = "04_textures/references/"

years = [1899,1912,1930,1939,1975] # 1956,1975,1987 # 


quilt_images_path = ["lake_bed_1_Cut_150_25x25.jpeg",
                     "vegetation_1_Cut_150_25x25.jpeg",
                     "lake_bed_1_Cut_150_25x25.jpeg",
                     "wetland_1_Cut_250_16x16.jpeg",
                     "buildings_1_Cut_300_13x13.jpeg",
                     "road_1_Cut_50_74x74.jpeg"]

# -------------------------------------------------------
# -------------------------------------------------------


for year in years:

    mask_paths = [f"stiched_rivers_{year}_clipped.tif",
                f"stiched_vegetation_{year}_clipped.tif",
                f"stiched_lake_{year}_clipped.tif",
                f"stiched_wetland_{year}_clipped.tif",
                f"stiched_buildings_{year}_clipped.tif",
                f"stiched_roads_{year}_clipped.tif"]


    output_path = base_path + f"04_textures/texture_{year}.png"


    mask_paths_ = [base_path + input_for_masking + mask_path for mask_path in mask_paths]
    quilt_images_paths_ = [base_path + input_for_quilling + quilt_image_path for quilt_image_path in quilt_images_path]


    fill_masks(mask_paths_, quilt_images_paths_, output_path)

    make_img_square(output_path, output_path.replace(".png","_squared.png"),method="min",align="center")


    #input_image_path = "input.png"
    #output_image_path = output_path.replace(".png","_transparent.png")
    #make_black_pixels_transparent(output_path, output_image_path)
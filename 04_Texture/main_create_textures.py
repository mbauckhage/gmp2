from utils.texture_fill import fill_masks, make_black_pixels_transparent


# Define the paths to the binary masks and quilt images
# -------------------------------------------------------
base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_masking = "03_resampled/"
input_for_quilling = "references/"

mask_paths = ["stiched_rivers_1975_clipped.tif",
              "stiched_vegetation_1975_clipped.tif",
              "stiched_lake_1975_clipped.tif",
              "stiched_wetland_1975_clipped.tif",
              "stiched_buildings_1975_clipped.tif",
              "stiched_roads_1975_clipped.tif"]


quilt_images_path = ["river_bed_1_small_Cut_200_19x19.jpeg",
                     "vegetation_1_Cut_150_25x25.jpeg",
                     "lake_bed_1_Cut_150_25x25.jpeg",
                     "wetland_1_Cut_250_16x16.jpeg",
                     "buildings_1_Cut_300_13x13.jpeg",
                     "road_1_Cut_50_74x74.jpeg"]


output_path = base_path + "merged_output_image.png"

# -------------------------------------------------------
# -------------------------------------------------------
mask_paths_ = [base_path + input_for_masking + mask_path for mask_path in mask_paths]
quilt_images_paths_ = [base_path + input_for_quilling + quilt_image_path for quilt_image_path in quilt_images_path]


fill_masks(mask_paths_, quilt_images_paths_, output_path)


# Example usage:
input_image_path = "input.png"
output_image_path = output_path.replace(".png","_transparent.png")
make_black_pixels_transparent(output_path, output_image_path)
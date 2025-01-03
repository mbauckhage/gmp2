from tqdm import tqdm
from utils.preprocessing import *
from scipy.ndimage import binary_opening, binary_closing



"""
The roads are not very clean in the binary raster. They are not binary, but have values between 0 and 1.
This script cleans the binary raster by setting all values < 0.65 to 0 and all values >= 0.65 to 1.
This scriipt also applies morphological operations to remove small objects and fill small holes.
"""


base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_for_conversion = "02_clipped/"

annotations = ["roads"] # "roads"


input_folder = os.path.join(base_path, input_for_conversion)



for filename in tqdm(os.listdir(input_folder)):
    if filename.endswith(".tif") and not filename.startswith("._"):
                
        
        input_geotiff = os.path.join(input_folder, filename)
        
        annotation = filename.split("_")[1]
        
        if annotation not in annotations: continue
        
        print(f"Cleaning raster {input_geotiff}")
        # Open the input raster
        with rasterio.open(input_geotiff) as src:
            # Read the raster data
            data = src.read(1)  # Read the first band
            profile = src.profile  # Copy the metadata/profile
            
             # Set all values > 0 to 1
            data[data < 0.65] = 0
            data[data >= 0.65] = 1

            # Set all values > 0 to 1
            binary_data = (data > 0).astype(np.uint8)

            # Apply morphological operations
            # Opening: Removes small objects (erosion followed by dilation)
            cleaned_data = binary_opening(binary_data, structure=np.ones((3, 3)))

            # Optionally, apply closing to fill small holes
            # cleaned_data = binary_closing(cleaned_data, structure=np.ones((3, 3)))

            # Update the profile to match the data type if needed
            profile.update(dtype=rasterio.uint8)  # Use uint8 for binary values (0 and 1)

            # Write the modified data to a new raster
            with rasterio.open(input_geotiff, "w", **profile) as dst:
                dst.write(cleaned_data, 1)

        print(f"Modified raster saved to {input_geotiff}")





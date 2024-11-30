import rasterio
import numpy as np
from PIL import Image
from tqdm import tqdm


def read_geotiff_mask(mask_path):
    """
    Reads a binary mask from a GeoTIFF file.
    Returns the mask as a numpy array.
    """
    with rasterio.open(mask_path) as src:
        mask = src.read(1)  # Read the first band
    return mask

def read_image(image_path):
    """
    Reads an image file (e.g., a quilted river or vegetation image) into a numpy array.
    """
    image = Image.open(image_path)
    return np.array(image)

def apply_mask(image, mask, replacement_image):
    """
    Replaces pixels in the image based on the mask and the replacement image.
    - image: The original image to be modified (should have the same shape as the mask).
    - mask: Binary mask where 1 indicates the region to be replaced.
    - replacement_image: Image to use as a replacement for the masked pixels.
    Returns a new image with replacements applied.
    """
    # Ensure the replacement image is of the same shape as the mask
    replacement_resized = np.array(replacement_image)
    
    print("Image shape:      ",image.shape)
    print("Mask shape:       ",mask.shape)
    print("Replacement shape:",replacement_resized.shape)
    
    if replacement_resized.shape != mask.shape + (3,):  # Ensure the replacement has 3 channels
        raise ValueError("Replacement image and mask must have the same dimensions.")
    
    # Expand the mask to match the number of channels in the image
    expanded_mask = np.stack([mask] * 3, axis=-1)  # Expand mask from (height, width) to (height, width, 3)
    
    # Create a copy of the original image to avoid modifying it directly
    result_image = np.copy(image)
    
    # Replace masked pixels with the corresponding pixels from the replacement image
    # Normalize the mask to the range 0-1 based on its min and max values
    mask_min = mask.min()
    mask_max = mask.max()
    normalized_mask = (mask - mask_min) / (mask_max - mask_min)
    expanded_mask = np.stack([normalized_mask] * 3, axis=-1)
    result_image[expanded_mask == 1] = replacement_resized[expanded_mask == 1]
    
    return result_image

def fill_masks(binarymasks, quilt_images, output_path,default_color=(211, 211, 196)):
    """
    Merges the masks (e.g. vegetation, river, lakes,...) with their respective quilt images.
    Saves the resulting image as a new file.
    """
    
    assert len(binarymasks) == len(quilt_images), "Number of masks and images must match."
    
    
    # Empty image to start with
    mask1 = read_geotiff_mask(binarymasks[0])
    height, width = mask1.shape
    
    # Initialize the final image with the default color (light warm grey)
    final_image = np.full((height, width, 3), default_color, dtype=np.uint8)


    for mask, quilt_images in tqdm(zip(binarymasks, quilt_images)):
        
        print(f"Processing image: ",mask.split("/")[-1])
        
        # Read the masks
        mask = read_geotiff_mask(mask)
        
        # Read the quilt images
        quilt_image = read_image(quilt_images)
        
        # Ensure the images are the same size as the masks
        quilt_image_resized = np.array(Image.fromarray(quilt_image).resize((width, height)))
        
        # Apply the mask to the final image
        final_image = apply_mask(final_image, mask, quilt_image_resized)

    
    # Save the final image
    final_image_pil = Image.fromarray(final_image)
    final_image_pil.save(output_path)
    print(f"Final image saved at: {output_path}")
    


def make_black_pixels_transparent(input_path, output_path):
    """
    Reads a PNG image, sets all black pixels (0, 0, 0) to transparent, and saves the new image.
    """
    # Open the image
    img = Image.open(input_path).convert("RGBA")
    
    # Convert image to numpy array
    data = np.array(img)
    
    # Extract the RGB channels
    r, g, b, a = data[..., 0], data[..., 1], data[..., 2], data[..., 3]
    
    # Create a mask where all pixels that are pure black will be made transparent
    black_pixels_mask = (r == 0) & (g == 0) & (b == 0)
    
    # Set alpha channel to 0 (transparent) for black pixels
    data[..., 3] = np.where(black_pixels_mask, 0, a)
    
    # Convert the modified array back to an image
    new_img = Image.fromarray(data, mode="RGBA")
    
    # Save the resulting image
    new_img.save(output_path)
    print(f"Image saved with transparent black pixels at: {output_path}")




import numpy as np
import matplotlib.pyplot as plt
from skimage import data, filters, color, morphology
from skimage.segmentation import flood, flood_fill
import cv2

import numpy as np
import matplotlib.pyplot as plt
from skimage import morphology
from skimage.morphology import medial_axis
from skimage.measure import label, regionprops
from shapely.geometry import LineString
import geopandas as gpd
from skimage.morphology import skeletonize



def plot_images(*images, titles=None, cmap='gray', height=10):
    """
    Plots an arbitrary number of images in a subplot.

    Parameters:
    *images: list of numpy.ndarray
        The images to be plotted.
    titles: list of str, optional
        Titles for each subplot. If None, no titles will be displayed.
    cmap: str, optional
        Colormap to be used for displaying the images. Default is 'gray'.
    """
    num_images = len(images)
    plt.figure(figsize=(height, 5 * num_images))

    for i, image in enumerate(images):
        plt.subplot(1, num_images, i + 1)
        plt.imshow(image, cmap=cmap)
        if titles and i < len(titles):
            plt.title(titles[i])
        plt.axis('off')

    plt.tight_layout()
    plt.show()
    
    
def crop_image(img, x, y, w, h):
    return img[y:y+h, x:x+w]


def mask_image(image):
    # Split the image into R, G, B channels
    R, G, B = cv2.split(image)
    threshold_B = 100  # Adjust for Blue channel
    _, thresh_B = cv2.threshold(B, threshold_B, 255, cv2.THRESH_BINARY)

    kernel_1 = np.ones((3,3),np.uint8)
    thresh_B_invert = 255 - thresh_B
    B_dilation = cv2.dilate(thresh_B_invert,kernel_1,iterations = 1)
    B_errosion = cv2.erode(B_dilation,kernel_1,iterations = 1)

    masked_image = cv2.bitwise_and(image, image, mask=thresh_B_invert)
    
    return masked_image


def mask_flood_fill(image, seed=(58, 24), tolerance=0.5):
    """
    Function to perform flood fill on an image starting from a seed point.
    
    Parameters:
    image (ndarray): Input image (grayscale or RGB).
    seed (tuple): Seed point coordinates (row, col).
    tolerance (float): Tolerance value for flood fill.
    
    Returns:
    mask (ndarray): Binary mask of the flooded region.
    """
    
    img_hsv_ = color.rgb2hsv(image)
    img_hsv_copy_ = np.copy(img_hsv_)
    # flood function returns a mask of flooded pixels
    mask = flood(img_hsv_[..., 0], seed, tolerance=tolerance)
    # Set pixels of mask to new value for hue channel
    img_hsv_[mask, 0] = 0
    # Post-processing in order to improve the result
    # Remove white pixels from flag, using saturation channel
    mask_postprocessed_1 = np.logical_and(mask, img_hsv_copy_[..., 1] > 0.05)
    # Remove thin structures with binary opening
    mask_postprocessed_2= morphology.binary_opening(mask_postprocessed_1, np.ones((3, 3)))
    # Fill small holes with binary closing
    mask_postprocessed_3 = morphology.binary_closing(mask_postprocessed_2, morphology.disk(10))
    img_hsv_copy_[mask_postprocessed_3, 0] = 0.5
    

    # Step 6: Create a mask for only hue = 0.5
    mask_hue_05 = img_hsv_[..., 0] == 0.5
    
    return img_hsv_, img_hsv_copy_, mask_hue_05, mask_postprocessed_1, mask_postprocessed_2, mask_postprocessed_3,mask




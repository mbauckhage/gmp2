import cv2
import numpy as np
from matplotlib import pyplot as plt


def crop_img(img, x, y, w, h):
    return img[y:y+h, x:x+w]

# Load the historical map image
image = cv2.imread('data/Siegfried.tif', cv2.IMREAD_COLOR)

# Convert the image to grayscale
#image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Convert the image from BGR (OpenCV default) to RGB
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Split the image into R, G, B channels
R, G, B = cv2.split(image_rgb)



# Step 4: Define the position and size of the crop
x_start = 00  # x-coordinate of the top-left corner
y_start = 0  # y-coordinate of the top-left corner
width = 100    # Width of the crop
height = 100   # Height of the crop

# Step 5: Crop the image using array slicing
cropped_image = crop_img(image_rgb, x_start, y_start, width, height)
#cropped_image_gray = crop_img(image_gray, x_start, y_start, width, height)


import numpy as np
import matplotlib.pyplot as plt
from skimage import io, color

def select_seed(image):
    """
    Function to display the image and allow the user to click on a point to set a seed pixel.
    
    Parameters:
    image (ndarray): Input image (can be grayscale or RGB).
    
    Returns:
    seed_point (tuple): Coordinates of the selected seed pixel (row, col).
    """
    # Convert to grayscale if it's an RGB image
    if len(image.shape) == 3:
        grayscale = color.rgb2gray(image)
    else:
        grayscale = image

    # Set up the plot
    fig, ax = plt.subplots()
    ax.imshow(grayscale, cmap='gray')
    ax.set_title('Click to set the seed pixel')

    # To store the clicked seed point
    seed_point = []

    # Event handler to capture the click event
    def onclick(event):
        # Ensure that the click is within the image bounds
        if event.xdata is not None and event.ydata is not None:
            x, y = int(event.xdata), int(event.ydata)
            seed_point.append((y, x))  # Append row, col format
            ax.plot(x, y, 'ro')  # Mark the seed point on the image
            plt.draw()  # Update the plot immediately
            print(f'Seed point selected: (row={y}, col={x})')

    # Connect the click event to the handler
    cid = fig.canvas.mpl_connect('button_press_event', onclick)

    # Show the plot and wait for interaction
    plt.show()

    # Disconnect the event handler after the plot is closed
    fig.canvas.mpl_disconnect(cid)

    # Return the selected seed point (or None if no point is clicked)
    return seed_point[0] if seed_point else None

# Example usage
# Load the image (replace 'path_to_your_map.tiff' with your image path)
image = cropped_image

# Call the function to select the seed pixel
seed = select_seed(image)

if seed is not None:
    print(f'Seed pixel coordinates: {seed}')
else:
    print('No seed point selected.')

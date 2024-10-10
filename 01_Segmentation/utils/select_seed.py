import matplotlib.pyplot as plt
from skimage import color
import numpy as np
import time
import sys

def select_seed(image):
    """
    Function to display the image and allow the user to click on a point to set a seed pixel.
    
    Parameters:
    image (ndarray): Input image (can be grayscale or RGB).
    
    Returns:
    seed_point (tuple): Coordinates of the selected seed pixel (row, col).
    """
    print("--- select_seed ---")
    
    # Convert to grayscale if it's an RGB image
    if len(image.shape) == 3:
        grayscale = color.rgb2gray(image)
    else:
        grayscale = image

    # Set up the plot
    fig, ax = plt.subplots()
    ax.imshow(grayscale, cmap='gray')
    ax.set_title('Click to set the seed pixel, then close the window')

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
    

    # Close the plot
    plt.close(fig)
    
    
    
    
    # Return the seed point if one was selected
    if seed_point:
        return seed_point[0]
    else:
        return None

def check_seed_point(seed_point,image):
    def check_seed_point(seed_point, image):
        """
        Checks if the provided seed point is acceptable and allows the user to select a new one if necessary.
        Parameters:
        seed_point (tuple): The initial seed point to be checked.
        image (ndarray): The image on which the seed point is to be selected.
        Returns:
        bool: True if a valid seed point is selected, False otherwise.
        The function prompts the user to confirm if the provided seed point is acceptable. If the user responds with 'no',
        it allows the user to select a new seed point until an acceptable one is chosen.
        """
    
    
    
    if seed_point:
        response = input("Is this seed point okay? (yes/no): ").lower().strip()
        while response == 'no':
            print("Select a new point on the map...")
            seed_point = select_seed(image)
            response = input("Is this seed point okay? (yes/no): ").lower().strip()
        print(f"Selected seed point: {seed_point}")   
        return True     
    else:
        print("No seed point was selected.")
        return False
        
        

import numpy as np
import math
from skimage import io, util
import heapq
from skimage.transform import rescale, resize
from PIL import Image
import argparse
from tqdm import tqdm
import os

# from: https://github.com/Devashi-Choudhary/Texture-Synthesis


image_path = "/Volumes/T7 Shield/GMP_Data/processed_data/references/road_1.jpeg"
reference_image_path = "/Volumes/T7 Shield/GMP_Data/processed_data/02_clipped/stiched_vegetation_1975_clipped.tif"

block_size = 50
mode = "Cut"


def randomPatch(texture, block_size):
    h, w, _ = texture.shape
    i = np.random.randint(h - block_size)
    j = np.random.randint(w - block_size)

    return texture[i:i+block_size, j:j+block_size]

def L2OverlapDiff(patch, block_size, overlap, res, y, x):
    error = 0
    if x > 0:
        left = patch[:, :overlap] - res[y:y+block_size, x:x+overlap]
        error += np.sum(left**2)

    if y > 0:
        up   = patch[:overlap, :] - res[y:y+overlap, x:x+block_size]
        error += np.sum(up**2)

    if x > 0 and y > 0:
        corner = patch[:overlap, :overlap] - res[y:y+overlap, x:x+overlap]
        error -= np.sum(corner**2)

    return error
 

def randomBestPatch(texture, block_size, overlap, res, y, x):
    h, w, _ = texture.shape
    errors = np.zeros((h - block_size, w - block_size))

    for i in range(h - block_size):
        for j in range(w - block_size):
            patch = texture[i:i+block_size, j:j+block_size]
            e = L2OverlapDiff(patch, block_size, overlap, res, y, x)
            errors[i, j] = e

    i, j = np.unravel_index(np.argmin(errors), errors.shape)
    return texture[i:i+block_size, j:j+block_size]



def minCutPath(errors):
    # dijkstra's algorithm vertical
    pq = [(error, [i]) for i, error in enumerate(errors[0])]
    heapq.heapify(pq)

    h, w = errors.shape
    seen = set()

    while pq:
        error, path = heapq.heappop(pq)
        curDepth = len(path)
        curIndex = path[-1]

        if curDepth == h:
            return path

        for delta in -1, 0, 1:
            nextIndex = curIndex + delta

            if 0 <= nextIndex < w:
                if (curDepth, nextIndex) not in seen:
                    cumError = error + errors[curDepth, nextIndex]
                    heapq.heappush(pq, (cumError, path + [nextIndex]))
                    seen.add((curDepth, nextIndex))

                    
def minCutPatch(patch, block_size, overlap, res, y, x):
    patch = patch.copy()
    dy, dx, _ = patch.shape
    minCut = np.zeros_like(patch, dtype=bool)

    if x > 0:
        left = patch[:, :overlap] - res[y:y+dy, x:x+overlap]
        leftL2 = np.sum(left**2, axis=2)
        for i, j in enumerate(minCutPath(leftL2)):
            minCut[i, :j] = True

    if y > 0:
        up = patch[:overlap, :] - res[y:y+overlap, x:x+dx]
        upL2 = np.sum(up**2, axis=2)
        for j, i in enumerate(minCutPath(upL2.T)):
            minCut[:i, j] = True

    np.copyto(patch, res[y:y+dy, x:x+dx], where=minCut)

    return patch


def quilt(image_path, block_size, num_block, mode, sequence=False):
    
    print("Quilting...")
    texture = Image.open(image_path)
    texture = util.img_as_float(texture)
    
    print("Texture shape: ", texture.shape)

    overlap = block_size // 6
    num_blockHigh, num_blockWide = num_block

    h = (num_blockHigh * block_size) - (num_blockHigh - 1) * overlap
    w = (num_blockWide * block_size) - (num_blockWide - 1) * overlap

    res = np.zeros((h, w, texture.shape[2]))

    for i in tqdm(range(num_blockHigh)):
        for j in range(num_blockWide):
            y = i * (block_size - overlap)
            x = j * (block_size - overlap)

            if i == 0 and j == 0 or mode == "Random":
                patch = randomPatch(texture, block_size)
            elif mode == "Best":
                patch = randomBestPatch(texture, block_size, overlap, res, y, x)
            elif mode == "Cut":
                patch = randomBestPatch(texture, block_size, overlap, res, y, x)
                patch = minCutPatch(patch, block_size, overlap, res, y, x)
            
            res[y:y+block_size, x:x+block_size] = patch

    
    
    
    
    return res


def calculate_num_block_for_output_size(desired_output_size, block_size, overlap_fraction=6):
    """
    Calculate num_block (number of blocks) to achieve a desired output size based on the block size.
    
    Parameters:
    - desired_output_size: The target output size in pixels (e.g., 3000 pixels).
    - block_size: The size of each block.
    - overlap_fraction: The fraction of the block size that determines the overlap (default is 6, meaning overlap = block_size // 6).
    
    Returns:
    - num_block: The calculated number of blocks.
    """
    overlap = block_size // overlap_fraction

    # Calculate number of blocks for the desired output size
    num_block = math.ceil((desired_output_size + overlap) / (block_size - overlap))

    return num_block




if __name__ == "__main__":
    image_path = image_path
    block_size = block_size
    mode = mode
    
     # Load the reference image to get its dimensions
    reference_image = Image.open(reference_image_path)
    reference_width, reference_height = reference_image.size
    
    # Calculate the desired output size based on the reference image
    desired_output_size = max(reference_width, reference_height)
    
    num_block = calculate_num_block_for_output_size(desired_output_size, block_size)
    print("Number of blocks: ", num_block)
    res = quilt(image_path, block_size, (num_block, num_block), mode)
    
   
    
    # Crop the result based on the dimensions of the reference image
    res = res[:reference_height, :reference_width]
    
    image = Image.fromarray((res * 255).astype(np.uint8))
    
    
    # Convert the result image to RGB before saving
    image_rgb = image.convert("RGB")

    # Save the image
    output_path = image_path.split(".")[0] + f"_{mode}_{block_size}_{num_block}x{num_block}.jpeg"
    image_rgb.save(output_path)
    print(f"Image saved to {output_path}")



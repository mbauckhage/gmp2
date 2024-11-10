import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from shapely.geometry import LineString, mapping
import json

# Load the GeoJSON file
base_path ="/Users/mischabauckhage/Documents/ETH/02_Master/3_Semester/GMP2/gmp2/01_Segmentation/output/"
geojson_path = "old_national_1975_skeleton.geojson"

output_geojson_path = base_path + "interpolated_contours.geojson"


gdf = gpd.read_file(base_path+geojson_path)

# Extract coordinates and heights from contour lines
points = []
values = []
for _, row in gdf.iterrows():
    if isinstance(row.geometry, LineString):
        coords = list(row.geometry.coords)
        height = row['height']  # Make sure 'height' is the attribute in your GeoJSON
        points.extend(coords)
        values.extend([height] * len(coords))

points = np.array(points)
values = np.array(values)

# Create a grid to interpolate onto
min_x, min_y, max_x, max_y = gdf.total_bounds
grid_x, grid_y = np.mgrid[min_x:max_x:500j, min_y:max_y:500j]  # Adjust 500j for resolution

# Perform interpolation (you can try other methods like 'nearest', 'cubic')
grid_z = griddata(points, values, (grid_x, grid_y), method='linear')

# Generate new contour lines from interpolated data
contour_levels = np.arange(np.min(values), np.max(values), 10)  # Adjust the step (e.g., 10) for more contours
plt.figure()
contours = plt.contour(grid_x, grid_y, grid_z, levels=contour_levels)

# Convert matplotlib contours to GeoJSON format
new_contours = []
for collection in contours.collections:
    for path in collection.get_paths():
        coords = path.vertices
        line = LineString(coords)
        if line.is_valid:
            new_contours.append({
                "type": "Feature",
                "geometry": mapping(line),
                "properties": {"height": collection.get_label()},
            })

# Save the new contours to a GeoJSON file

with open(output_geojson_path, 'w') as f:
    json.dump({
        "type": "FeatureCollection",
        "features": new_contours
    }, f)

print(f"Interpolated contours saved to {output_geojson_path}")

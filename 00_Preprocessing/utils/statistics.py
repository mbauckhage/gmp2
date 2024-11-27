
import json
import os

def get_min_max_height(geojson_path):
    """
    Reads a GeoJSON file and extracts the minimum and maximum height values.

    Parameters:
    - geojson_path (str): Path to the GeoJSON file.

    Returns:
    - Tuple (min_height, max_height): Minimum and maximum height values.
    """
    try:
        # Load the GeoJSON file
        with open(geojson_path, 'r') as file:
            geojson_data = json.load(file)

        # Ensure the GeoJSON has features
        if 'features' not in geojson_data or not geojson_data['features']:
            raise ValueError("The GeoJSON file does not contain any features.")

        # Extract height values from features
        heights = []
        for feature in geojson_data['features']:
            # Assume height is stored in the 'properties' section under a key like 'height'
            # Adjust the key as per your GeoJSON structure
            height = feature.get('properties', {}).get('height')
            if height is not None:
                heights.append(height)

        # Check if we found any heights
        if not heights:
            raise ValueError("No height values found in the GeoJSON file.")

        # Calculate min and max
        min_height = min(heights)
        max_height = max(heights)

        return min_height, max_height

    except Exception as e:
        print(f"Error processing {geojson_path}: {e}")
        return None, None

def process_geojsons(input_folder, output_json_path):
    """
    Processes all GeoJSON files in a folder, calculates the min and max height for each file,
    and stores the results in a JSON file.

    Parameters:
    - input_folder (str): Path to the folder containing GeoJSON files.
    - output_json_path (str): Path to save the output JSON file.
    """
    results = {}

    # Walk through all subdirectories
    for root, _, files in os.walk(input_folder):
        for file_name in files:
            if file_name.endswith('.geojson') and "height" in file_name and not file_name.startswith('._'):  # Only process relevant GeoJSON files
                year = os.path.splitext(file_name)[0]  # Use the file name (without extension) as the key
                geojson_path = os.path.join(root, file_name)
                
                # Get min and max heights
                min_height, max_height = get_min_max_height(geojson_path)
                if min_height is not None and max_height is not None:
                    results[year] = {
                        "min_height": min_height,
                        "max_height": max_height,
                        "difference": max_height - min_height,
                        "difference_with_rivers": max_height - min_height + 4  # Add 4 for rivers
                    }
            else:
                print(f"Skipping file: {file_name}")
    
    # Save results to a JSON file
    with open(output_json_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)
    print(f"Results saved to {output_json_path}")
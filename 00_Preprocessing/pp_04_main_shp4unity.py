from utils.preprocessing import *
import json

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_dir = "03_vector_data/"

output_dir = "04_data_for_unity/"




layer_params_building = {
    'attributes': {
        'name': 'Building',
        'building': 'building',
        'waterway': '',
        'natural': '',
        'grass': '',
        'layer': 'Unknown Area Type',
    },
    'filter_area': 5
}

layer_params_water = {
    'attributes':
        {
        'name': 'Water',
        'building': '',
        'waterway': 'waterway',
        'natural': '',
        'grass': '',
        'layer': 'Unknown Area Type'
        },
    'filter_area': 5
}


layer_params_forest = {
    'attributes':
        {
            'name': 'Forest',
            'building': '',
            'waterway': '',
            'natural': 'forest',
            'grass': '',
            'layer': 'Unknown Area Type'
        },
    'filter_area': 5
}


layer_params_grass = {
    'attributes':
        {
            'name': 'Grass',
            'building': '',
            'waterway': '',
            'natural': '',
            'grass': 'common',
            'layer': 'Unknown Area Type'
        },
    'filter_area': 5
}


#annotations = ["buildings","lake","rivers","vegetation","vegetation"] # ,"lake","rivers", "roads"
layer_params = [layer_params_building,layer_params_water,layer_params_water,layer_params_forest,layer_params_grass] # ,layer_params_water,layer_params_forest,layer_params_building
years_to_exclude = []


annotations = {
    "buildings": {
        "input_annotation": "buildings",
        "layer_params": layer_params_building,
        "output_annotation": "buildings"
    },
    "lake": {
         "input_annotation": "lake",
        "layer_params": layer_params_water,
        "output_annotation": "lake"
    },
    "rivers": {
         "input_annotation": "rivers",
        "layer_params": layer_params_water,
        "output_annotation": "rivers"
    },
    "vegetation": {
         "input_annotation": "vegetation",
        "layer_params": layer_params_forest,
        "output_annotation": "forest"
    },
    "grass": {
         "input_annotation": "vegetation",
        "layer_params": layer_params_grass,
        "output_annotation": "grass"
    }
}


files_list = {}

for annotation_key in annotations.keys():
    
    input_annotation = annotations[annotation_key]["input_annotation"]
    output_annotation = annotations[annotation_key]["output_annotation"]
    layer_param = annotations[annotation_key]["layer_params"]
    
    input_folder = base_path +  input_dir + input_annotation + "/"
    output_folder = base_path + input_dir + output_annotation + "/"
    
    ensure_directory_exists(output_folder)
    
    for filename in tqdm(os.listdir(input_folder),desc=f"Processing {output_annotation}"):
        if filename.endswith(".shp") and not filename.startswith("._"):
            
            
            file_annotation = filename.split("_")[0]
            year = int(filename.split("_")[1].split(".")[0])
            
            input_shp = os.path.join(input_folder, filename)
            output_shp = os.path.join(output_folder, output_annotation + "_" + str(year) + ".shp")
            
            if file_annotation not in annotations: continue
            if year in years_to_exclude: continue
            
            if str(year) in files_list.keys():
                file_list_to_append = list(files_list[str(year)])
                file_list_to_append.append(output_shp)
                files_list[str(year)] = file_list_to_append
            
            elif str(year) not in files_list.keys():
                files_list[str(year)] = [output_shp]
                      
            prepare_shp_for_unity(input_shp,layer_param,output_shp)

            with open(base_path + output_dir + 'files_list.json', 'w') as json_file:
                json.dump(files_list, json_file)

for key in files_list.keys():
    

    year_dir = base_path + output_dir + f"{key}/{key}_VectorData"
    ensure_directory_exists(year_dir,print_info=False)        
    shp_for_unity_path = year_dir + "/Area.shp"

    #print(f"Processing {files_list[key][0].split('/')[-1]}")
    merge_shapefiles(files_list[key], shp_for_unity_path)
    

        


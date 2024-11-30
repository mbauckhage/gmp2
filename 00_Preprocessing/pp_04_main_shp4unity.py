from utils.preprocessing import *

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_dir = "03_vector_data/"

output_dir = "04_data_for_unity/"




layer_params_building = {
    'name': 'Building',
    'building': 'building',
    'place': '',
    'leisure': '',
    'layer': 'Unknown Area Type'
}

layer_params_water = {
    'name': 'Water',
    'building': '',
    'place': 'waterway',
    'leisure': '',
    'layer': 'Unknown Area Type'
}


layer_params_forst = {
    'name': 'Forest',
    'building': '',
    'place': '',
    'leisure': 'forest',
    'layer': 'Unknown Area Type'
}


annotations = ["buildings","lake","rivers"] # ,"lake","rivers", "roads"
layer_params = [layer_params_building,layer_params_water,layer_params_water] # ,layer_params_water,layer_params_forst,layer_params_building
years_to_exclude = []



files_list = {}

for annotation, layer_param in zip(annotations,layer_params):
    input_folder = base_path +  input_dir + annotation + "/"
    
    for filename in tqdm(os.listdir(input_folder)):
        if filename.endswith(".shp") and not filename.startswith("._"):
            
            
            input_shp = os.path.join(input_folder, filename)
            
            annotation = filename.split("_")[0]
            year = int(filename.split("_")[1].split(".")[0])
            
            if annotation not in annotations: continue
            if year in years_to_exclude: continue
            
            if str(year) in files_list.keys():
                file_list_to_append = list(files_list[str(year)])
                file_list_to_append.append(input_shp)
                files_list[year] = file_list_to_append
            
            elif str(year) not in files_list.keys():
                files_list[str(year)] = [input_shp]
                      
            prepare_shp_for_unity(input_shp,layer_param)

for key in files_list.keys():

    year_dir = base_path + output_dir + f"{key}/{key}_VectorData"
    ensure_directory_exists(year_dir)        
    shp_for_unity_path = year_dir + "/Area.shp"

    print(f"Processing {files_list[key]}")
    merge_shapefiles(files_list[key], shp_for_unity_path)
    

        


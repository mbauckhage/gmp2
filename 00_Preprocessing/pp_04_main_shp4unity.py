from utils.preprocessing import *

base_path = "/Volumes/T7 Shield/GMP_Data/processed_data/"
input_dir = "03_vector_data/"

annotations = ["buildings"] # ,"lake","rivers", "roads"
years_to_exclude = []



for annotation in annotations:
    input_folder = base_path +  input_dir + annotation + "/"
    
    for filename in tqdm(os.listdir(input_folder)):
        if filename.endswith(".shp") and not filename.startswith("._"):
            
            
            input_shp = os.path.join(input_folder, filename)
            
            annotation = filename.split("_")[0]
            year = int(filename.split("_")[1].split(".")[0])
            
            if annotation not in annotations: continue
            if year in years_to_exclude: continue
            
            print(f"Processing {input_shp}")
            prepare_shp_for_unity(input_shp)
        


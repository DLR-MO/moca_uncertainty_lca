from utils import *
import time
import pandas as pd

# time tracking
start_time = time.time()

# find the correct project output folder
lyfe_config, airlyfe_config = read_config()
dpath_project = os.path.realpath(os.path.join(
        os.path.realpath(os.path.dirname(os.path.dirname(__file__))), 'projects', lyfe_config.get('General', 'projectName')
    ))
output_folder_path = os.path.realpath(os.path.join(dpath_project, 'outputs'))

# read the file D250-TF_eco.xlsx from the outputs folder and get the data from the sheet "Individual LCAs"
data = pd.read_excel(os.path.join(output_folder_path, 'D250-TF_eco.xlsx'), sheet_name='Individual LCAs', skiprows=3, usecols='B:AG')

# read each row of the data and print it
for index, row in data.iterrows():
    name = row.values[0]
    key = row.values[1]
    database = row.values[2]
    
    
    identifier = f"lca_{index+1}_info = '{name}; {database}; {key}'"
    
    values_list = [value for value in row.values[4:]]
    
    values = f"lca_{index+1} = {', '.join(map(str, values_list))}"
    
    
    print(identifier)
    print(values)

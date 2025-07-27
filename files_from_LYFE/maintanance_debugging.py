from brightway2 import *
import time

from lca_sensitivity_analysis import perform_lca, write_json_file, set_filename

# time tracking
start_time = time.time()
    
# initialize the project and brightway infrastructure
projects.set_current('workstation_project') # ADJUST THIS TO THE BRIGHWAY PROJECT YOU WANT TO USE
bw2setup()

# specify the output file name
filename_output = set_filename("test_results.json")

# specify the database to be used
database_name = 'maintenance_activities' # ADJUST THIS TO THE DATABASE YOU WANT TO USE
db = Database(database_name)

# initialize the list of demands
demand_list = []
    
# loop through every activity in the databse and save its key and databse for the LCA later
for act in db:
    demand = {}
    demand['name'] = act._data['name'] #str(list(act.keys())[0]).split("'")[1]
    demand['key'] = act.key[1]
    demand['database'] = database_name
    
    demand_list.append(demand)  
            
# loop over all FUs, calculate baseline LCA score and perform sensitivity analysis      
i=0
for demand in demand_list:
    i += 1
        
    # perform the baseline LCA
    demand['score_baseline'] = perform_lca(demand)
    print("Baseline impact", i, "out of", len(demand_list), ":", demand['score_baseline'], "kg CO2-eq")
               
# write the results to an output file "test_results.json"
write_json_file(demand_list, filename_output)
        
# time tracking    
end_time = time.time()

duration = end_time - start_time
duration_minutes = duration // 60
duration_seconds = duration % 60

print("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes".format(duration, duration_minutes, int(duration_seconds)))
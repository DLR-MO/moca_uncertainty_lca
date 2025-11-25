# # make the code in the src folder accessible
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# # import the code from the src folder
# import monte_carlo

# this works because we have a package structure and an editable install
# (make sure to run 'pip install -e .' in the repository root first)
from uncertainty_lca import monte_carlo

# import standard modules
import os
import time
from datetime import timedelta
import json

import brightway2 as bw


def test_lca_monte_carlo():
    # start a timer for time-tracking
    start_time = time.time()
    
    # setting up Brightway
    brightway_project = "MOCA_test_project" # change me!
    bw.projects.set_current(brightway_project)
    
    # specify the LCIA method / characterisation model
    lcia_method_name = 'EF v3.1 no LT'
    lcia_methods = [method for method in bw.methods if lcia_method_name in str(method)]    
    
    # here, the impact categories are renamed to a more readable format
    key_list = []
    for method in lcia_methods:
        impact_cat = str(method[1])
        impact_unit = str(bw.methods[method]['unit'])
        key_list.append(impact_cat + ' [' + impact_unit + ']')
        
    # this is where you tell the code what to perform the Monte Carlo Simulation on 
    # you can add more demands to the list if you want to perform the Monte Carlo Simulation on multiple demands
    # each demand is a dictionary with the following keys:
    # - name: the name of the demand activity
    # - key: the key of the demand activity in the database
    # - database: the name of the database where the demand activity is stored
    
    # to adapt this to your code, simple replace "A-Check" with the name of your demand activity, "6b833f545a364efbac180f95710d34c8" with the key of your demand activity, and "maintenance_D250-TF" with the name of the database where your demand activity is stored
    demand_list = []
    demand = {
        "name": "LH2 Tank Replacement",  # change me!
        "key": "492e355ed3f74034b6d49b0240ff7800",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand) 
        
    # specify the number of iterations for the Monte Carlo simulation
    iterations = 25 # change me!
    
    # set up paths
    # specify a path to write the output files in later (change this if you want to write the output files somewhere other than the current directory)
    folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")
    
    # specify the names of the two output files of the full demand list:
    # 1. lca_monte_carlo.json: contains the full results of the Monte Carlo simulation for all demands
    # 2. lca_monte_carlo_statistics.json: contains only the statistics of the Monte Carlo simulation for all demands
    # there will also be a separate file for each demand containing the full results of the Monte Carlo simulation
    filename_output_json       = os.path.join(folder_path, "lca_monte_carlo.json")
    filename_output_short_json = os.path.join(folder_path, "lca_monte_carlo_statistics.json")

    print(f"This machine has {os.cpu_count()} logical cores, using {min(os.cpu_count(), 60)} cores for parallel processing.")  
    
    # loop over all demands in the demand_list and perform the Monte Carlo simulation
    for i, demand in enumerate(demand_list):
        
        # this calls the parallelised function that performs the Monte Carlo simulation
        monte_carlo.perform_monte_carlo(demand, lcia_methods, key_list, brightway_project, iterations=iterations)
        
        # if there is old LCA data in the demand dictionary, it is removed before writing the results to a file
        if 'lca_results' in demand:
            del demand['lca_results']
            
        with open(os.path.join(folder_path, "lca_" + str(demand['name']).replace(" ","_") + "_monte_carlo.json"), 'w') as file:
            json.dump(demand, file, indent=4)
    
        
    with open(filename_output_json, 'w') as file:
        json.dump(demand_list, file, indent=4) 
        
    for demand in demand_list:
        del demand['mc_results']
    with open(filename_output_short_json, 'w') as file:
        json.dump(demand_list, file, indent=4)

    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    dur_timedelta = timedelta(seconds=int(duration))
    
    print(f"Time elapsed: {duration:.2f} seconds = {duration // 60:.0f}:{int(duration % 60):02} minutes = {dur_timedelta}")
    
# this is the main function that is called when you press run
if __name__ == "__main__": 
    test_lca_monte_carlo()
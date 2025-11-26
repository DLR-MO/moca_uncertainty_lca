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

import brightway2 as bw


def test_lca_monte_carlo():
    # start a timer for time-tracking
    start_time = time.time()
    
    # setting up Brightway
    bw.projects.set_current("MOCA_test_project")  # change me!
    
    # specify the LCIA method / characterisation model
    lcia_method_name = 'EF v3.1 no LT'  # change me!
        
    # this is where you tell the code what to perform the Monte Carlo Simulation on 
    # you can add more demands to the list if you want to perform the Monte Carlo Simulation on multiple demands
    # each demand is a dictionary with the following keys:
    # - name: the name of the demand activity
    # - key: the key of the demand activity in the database
    # - database: the name of the database where the demand activity is stored
    
    demand_list = []
    demand_dict = {
        "name": "LH2 Tank Replacement",  # change me!
        "key": "492e355ed3f74034b6d49b0240ff7800",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand_dict) 
        
    # specify the number of iterations for the Monte Carlo simulation
    iterations = 25 # change me!
    
    print(f"This machine has {os.cpu_count()} logical cores, using {min(os.cpu_count(), 60)} cores for parallel processing.")  
    
    # loop over all demands in the demand_list and perform the Monte Carlo simulation
    for i, demand_dict in enumerate(demand_list):
        
        demand = bw.Database(demand_dict['database']).get(demand_dict['key'])
        
        # this calls the parallelised function that performs the Monte Carlo simulation
        demand_dict['mc_results'] = monte_carlo.parallel_monte_carlo(demand, lcia_method_name, iterations=iterations)
        demand_dict['mc_statistics'] = monte_carlo.calculate_statistics(demand_dict['mc_results'], lcia_method_name)
            
        # create a results file for the current demand
        monte_carlo.write_json(os.path.join(folder_path, "lca_" + str(demand_dict['name']).replace(" ","_") + "_monte_carlo.json"), demand_dict)
           
    # the results are written to a results folder
    folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")
    
    # specify the names of the two output files of the full demand list:
    # 1. lca_monte_carlo.json: contains the full results of the Monte Carlo simulation for all demands
    # 2. lca_monte_carlo_statistics.json: contains only the statistics of the Monte Carlo simulation for all demands
    # there will also be a separate file for each demand containing the full results of the Monte Carlo simulation
    filename_output_json = os.path.join(folder_path, "lca_monte_carlo.json")
    filename_output_short_json = os.path.join(folder_path, "lca_monte_carlo_statistics.json")
    
    # write the full results to a file
    monte_carlo.write_json(filename_output_json, demand_list)
    
    # delete the full Monte Carlo results from each demand dictionary before writing the statistics to a separate file
    for demand_dict in demand_list:
        del demand_dict['mc_results']
    monte_carlo.write_json(filename_output_short_json, demand_list)

    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    dur_timedelta = timedelta(seconds=int(duration))
    
    print(f"Time elapsed: {duration:.2f} seconds = {duration // 60:.0f}:{int(duration % 60):02} minutes = {dur_timedelta}")
    
# this is the main function that is called when you press run
if __name__ == "__main__": 
    test_lca_monte_carlo()
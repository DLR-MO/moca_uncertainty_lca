# # make the code in the src folder accessible
# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# # import the code from the src folder
# import monte_carlo

# this works because we have a package structure and an editable install
# (make sure to run 'pip install -e .' in the repository root first)
from uncertainty_lca import monte_carlo as mc

# import standard modules
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
    # iterations = 25 # change me!   
    
    # loop over all demands in the demand_list and perform the Monte Carlo simulation
    for i, demand_dict in enumerate(demand_list):
        
        demand = {bw.Database(demand_dict['database']).get(demand_dict['key']): 1}
        
        # mc = monte_carlo.MariasParallelMonteCarloLCA(demand, lcia_method_name, iterations)
        # mc.execute_parallel_monte_carlo()
        # mc_results = mc.mc_results
        
        mc_lca = mc.MonteCarloLCA(demand, lcia_method_name)
        mc_lca.execute_monte_carlo(iterations=50)
        mc_results = mc_lca.mc_results
        # mc_lca.print_stats()
        mc_lca.results_to_json()
        # mc_lca.stats_to_json(identifier='name')
        
        # this calls the parallelised function that performs the Monte Carlo simulation
        # mc_results = mc.parallel_monte_carlo(demand, lcia_method_name, iterations=iterations)
        # mc_stats = mc.calculate_statistics(mc_results, lcia_method_name)
            
        # create a results file for the current demand
        # monte_carlo.write_json(f"mc_results_{str(demand_dict['name']).replace(' ','_')}_monte_carlo.json", demand_dict | mc_results)
        # monte_carlo.write_json(f"mc_stats_{str(demand_dict['name']).replace(' ','_')}_monte_carlo.json", demand_dict | mc_stats)
    
    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    dur_timedelta = timedelta(seconds=int(duration))
    
    print(f"Time elapsed: {duration:.2f} seconds = {duration // 60:.0f}:{int(duration % 60):02} minutes = {dur_timedelta}")
    
# this is the main function that is called when you press run
if __name__ == "__main__": 
    test_lca_monte_carlo()
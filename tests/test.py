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
        
        # build the demand dictionary for the Monte Carlo LCA
        demand = {bw.Database(demand_dict['database']).get(demand_dict['key']): 1}
        
        # initialize the Monte Carlo LCA
        mc_lca = mc.MonteCarloLCA(demand, lcia_method_name)
        
        # execute the Monte Carlo simulation
        mc_lca.execute_monte_carlo(iterations=25)
        
        # retrieve the results and write them to files
        mc_results = mc_lca.mc_results
        # mc_lca.print_stats()
        mc_lca.results_to_json()
        mc_lca.stats_to_json()
    
    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    dur_timedelta = timedelta(seconds=int(duration))
    
    print(f"Time elapsed: {duration:.2f} seconds = {duration // 60:.0f}:{int(duration % 60):02} minutes = {dur_timedelta}")
    
# this is the main function that is called when you press run
if __name__ == "__main__": 
    test_lca_monte_carlo()
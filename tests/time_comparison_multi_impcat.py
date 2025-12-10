import uncertainty_lca as ulca

# import standard modules
import time
from datetime import timedelta

import brightway2 as bw
import json

def run_uncertainty_lca():
    # start a timer for time-tracking
    start_time = time.time()
        
    # initialize the Monte Carlo LCA
    mc_lca = ulca.MonteCarloLCA(demand, lcia_method_name=lcia_method_name)
    
    # execute the Monte Carlo simulation
    mc_lca.execute_monte_carlo(iterations=100)
    
    # retrieve the results and write them to files
    mc_results = mc_lca.mc_results
    # mc_lca.print_stats()
    mc_lca.results_to_json(filename="ulca_mc_results.json")
    mc_lca.stats_to_json(filename="ulca_mc_stats.json")
    
    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    dur_timedelta = timedelta(seconds=int(duration))
    
    print(f"Time elapsed for uncertainty_lca: {duration:.2f} seconds = {duration // 60:.0f}:{int(duration % 60):02} minutes = {dur_timedelta}")
    
def run_brightway():
    # start a timer for time-tracking
    start_time = time.time()
    
    # find all methods that belong to the specified characterisation model
    methods = [
        method for method in bw.methods if method[0] == lcia_method_name
    ]
        
    # execute the Monte Carlo simulation
    mc_results = {}
    for method in methods:
        
        # initialize the Monte Carlo LCA
        mc_lca = bw.MonteCarloLCA(demand, method)
        
        impact_cat = str(method[1])
        impact_unit = str(bw.methods[method]['unit'])
        key = impact_cat + ' [' + impact_unit + ']'
        
        mc_results[key] = []
        for _ in range(100):
            mc_results[key].append(next(mc_lca))
            
    json.dump(mc_results, open("results\\bw_mc_results.json", "w"), indent=4)
    
    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    dur_timedelta = timedelta(seconds=int(duration))
    
    print(f"Time elapsed for brightway2: {duration:.2f} seconds = {duration // 60:.0f}:{int(duration % 60):02} minutes = {dur_timedelta}")
    
# this is the main function that is called when you press run
if __name__ == "__main__": 
    
    # setting up Brightway
    bw.projects.set_current("MOCA_test_project")  # change me!
    
    # specify the LCIA method / characterisation model
    lcia_method_name = 'EF v3.1 no LT'  
        
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
    
    # build the demand dictionary for the Monte Carlo LCA
    demand = {bw.Database(demand_dict['database']).get(demand_dict['key']): 1}
    
    run_uncertainty_lca()
    run_brightway()

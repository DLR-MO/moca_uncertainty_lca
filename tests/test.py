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
import time


def test_lca_monte_carlo():
    # start a timer for time-tracking
    start_time = time.time()
    
    # specify the Brightway project name
    brightway_project = "MOCA_test_project" # change me!
    
    # specify the LCIA method / characterisation model
    lcia_method_name = 'EF v3.1 no LT'
    
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
    # demand = {
    #     "name": "Leakage Test",  # change me!
    #     "key": "f02b85a5af3c481482d9448b8f076b81",  # change me!
    #     "database": "maintenance_D250_TF_MHEP"  # change me!
    # }
    # demand_list.append(demand)
        
    # specify the number of iterations for the Monte Carlo simulation
    iterations = 25 # change me!

    # with Profile() as profile:
    monte_carlo.parallel_lca(brightway_project, demand_list, lcia_method_name, iterations)
        # (
        #     Stats(profile)
        #     .strip_dirs()
        #     .sort_stats(SortKey.CALLS)
        #     .print_stats()
        # )

    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    duration_minutes = duration // 60
    duration_seconds = duration % 60
    duration_hours = duration_minutes // 60

    print("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes = {:.0f}:{:.0f}:{:02}".format(duration, duration_minutes, int(duration_seconds), duration_hours, duration_minutes % 60, int(duration_seconds)))
    
# this is the main function that is called when you press run
if __name__ == "__main__": 
    test_lca_monte_carlo()
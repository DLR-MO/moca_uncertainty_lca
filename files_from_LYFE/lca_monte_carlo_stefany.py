# import brightway
import brightway2 as bw

# import standard python libraries
import time
import os
import json
import numpy as np

# import multiprocessing libraries and a library to make progress bars (tqdm)
import tqdm
from multiprocessing import Pool, cpu_count, Manager, Queue

# this is the function where the actual Monte Carlo simulation is performed
def monte_carlo_worker(args):
    """
    Worker function for Monte Carlo simulation. Each worker will perform a subset of the iterations.
    
    Args:
        args: Tuple containing the following elements:
            demand: Dictionary containing the demand activity.
            lcia_methods: List of LCIA methods.
            key_list: List of keys for the LCIA methods.
            brightway_project: Name of the Brightway project.
            iterations: Number of iterations to perform.
            progress_queue: Queue for reporting progress.
            
    Returns:
        mc_results: Dictionary containing the Monte Carlo results      
    """
    demand, lcia_methods, key_list, brightway_project, iterations, progress_queue = args
    
    # re-initialize the project and Brightway infrastructure within the worker
    # this is needed for the parallelisation because Brightway is not thread-safe
    bw.projects.set_current(brightway_project) 
    
    # load the demand activity
    demand_activity = bw.Database(demand['database']).get(demand['key'])
    
    # each worker will perform a subset of the iterations
    mc_results = {key: [] for key in key_list}
    
    # this is performing the actual Monte Carlo simulation
    for _ in range(iterations):
        
        # initialize the Monte Carlo object
        monte_carlo = bw.MonteCarloLCA({demand_activity: 1}, method=lcia_methods[0])
        
        # load data and rebuild matrices
        monte_carlo.load_data()
        monte_carlo.rebuild_technosphere_matrix(monte_carlo.tech_rng.next())
        monte_carlo.rebuild_biosphere_matrix(monte_carlo.bio_rng.next())
        monte_carlo.build_demand_array()
        
        # perform the LCI (this takes a lot of time and is therefore only performed once for all impact categories)
        monte_carlo.lci_calculation()
        
        # loop over impact categories to perform the LCIA
        for i, method in enumerate(lcia_methods):
            
            # switch the LCIA method, reload data and rebuild the characterization matrix
            monte_carlo.switch_method(method)
            monte_carlo.load_data()
            monte_carlo.rebuild_characterization_matrix(monte_carlo.cf_rng.next())
            
            # perform the actual LCIA and store the results
            monte_carlo.lcia_calculation()
            mc_results[key_list[i]].append(monte_carlo.score)
        
        # Report progress for each iteration
        progress_queue.put(1)

    return mc_results

# this function acts as a wrapper for the Monte Carlo simulation itself and handles parallelisation
def perform_monte_carlo(demand, lcia_methods, key_list, brightway_project, iterations):
    """
    Perform Monte Carlo simulation for a given demand activity.
    
    Args:
        demand: Dictionary containing the demand activity.
        lcia_methods: List of LCIA methods.
        key_list: List of keys for the LCIA methods.
        brightway_project: Name of the Brightway project.
        iterations: Number of iterations to perform.
        
    Returns:
        demand: Dictionary containing the demand activity with the Monte Carlo results and statistics.
    """
    
    # determine the number of cores to use for parallel processing
    # the maximum number of cores is limited to 60 here to prevent overloading the system with too many parallel processes
    num_cores = min(cpu_count(), 60) 
    
    # split the iterations across multiple cores
    iterations_per_core = iterations // num_cores

    # initialize a progress queue for reporting progress
    manager = Manager()
    progress_queue = manager.Queue()
    
    # create a list of arguments for the worker processes
    args = [(demand, lcia_methods, key_list, brightway_project, iterations_per_core, progress_queue) for _ in range(num_cores)]
        
    print(f"Performing Monte Carlo simulation for demand: {demand['name']}")
    
    # perform the parallelised Monte Carlo Simulation 
    with tqdm.tqdm(total=iterations, desc=f"Current progress") as pbar:
        with Pool(num_cores) as pool:
            
            # start the worker processes
            pool_result = pool.map_async(monte_carlo_worker, args)
            
            # update the progress bar based on messages from the worker processes
            while not pool_result.ready():
                while not progress_queue.empty():
                    pbar.update(progress_queue.get())

            # wait for all worker processes to finish
            pool_result.get()  
    
    # combine results from all processes
    combined_results = {key: [] for key in key_list}
    for result in pool_result.get():
        for key in key_list:
            combined_results[key].extend(result[key])
    
    # calculate statistics
    mc_statistics = {}
    for i in range(len(lcia_methods)):
        percentiles = {
            "5": np.percentile(combined_results[key_list[i]], 5),
            "10": np.percentile(combined_results[key_list[i]], 10),
            "25": np.percentile(combined_results[key_list[i]], 25),
            "50": np.percentile(combined_results[key_list[i]], 50),
            "75": np.percentile(combined_results[key_list[i]], 75),
            "90": np.percentile(combined_results[key_list[i]], 90),
            "95": np.percentile(combined_results[key_list[i]], 95)
        }

        mc_statistics[key_list[i]] = {
            "mean": np.mean(combined_results[key_list[i]]),
            "std": np.std(combined_results[key_list[i]]),
            "min": float(np.min(combined_results[key_list[i]])),
            "max": float(np.max(combined_results[key_list[i]])),
            "percentiles": percentiles
        }
    
    # write the results back to the demand dictionary
    demand['mc_results'] = combined_results
    demand['mc_statistics'] = mc_statistics

    return demand

# this is the main function that is called when you press run
if __name__ == "__main__": 
    
    # start a timer for time-tracking
    start_time = time.time()
    
    # specify a path to write the output files in later (change this if you want to write the output files somewhere other than the current directory)
    folder_path = os.path.dirname(os.path.realpath(__file__))
    
    # specify the names of the two output files of the full demand list:
    # 1. lca_monte_carlo.json: contains the full results of the Monte Carlo simulation for all demands
    # 2. lca_monte_carlo_statistics.json: contains only the statistics of the Monte Carlo simulation for all demands
    # there will also be a separate file for each demand containing the full results of the Monte Carlo simulation
    filename_output_json       = os.path.join(folder_path, "lca_monte_carlo.json")
    filename_output_short_json = os.path.join(folder_path, "lca_monte_carlo_statistics.json")
    
    # this is where you tell the code what to perform the Monte Carlo Simulation on 
    # you can add more demands to the list if you want to perform the Monte Carlo Simulation on multiple demands
    # each demand is a dictionary with the following keys:
    # - name: the name of the demand activity
    # - key: the key of the demand activity in the database
    # - database: the name of the database where the demand activity is stored
    
    # to adapt this to your code, simple replace "A-Check" with the name of your demand activity, "6b833f545a364efbac180f95710d34c8" with the key of your demand activity, and "maintenance_D250-TF" with the name of the database where your demand activity is stored
    demand_list = []
    demand = {
        "name": "High-Pressure Pump",  # change me!
        "key": "7aca29b120b341ffbb9ba2569b5740c9",  # change me!
        "database": "maintenance_D250_TP_MHEP"  # change me!
    }
    demand_list.append(demand) 
    demand = {
        "name": "Leakage Test",  # change me!
        "key": "f02b85a5af3c481482d9448b8f076b81",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    demand = {
        "name": "Check Valves 1",  # change me!
        "key": "999a371700094c7ab9768f817ed09005",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    demand = {
        "name": "Check Valves 2",  # change me!
        "key": "999a371700094c7ab9768f817ed09007",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    demand = {
        "name": "Tank and LH2 Distribution Systems 1",  # change me!
        "key": "999a371700094c7ab9768f817ed09015",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    demand = {
        "name": "Tank and LH2 Distribution Systems 2",  # change me!
        "key": "999a371700094c7ab9768f817ed09016",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    demand = {
        "name": "Tank and LH2 Distribution Systems 3",  # change me!
        "key": "999a371700094c7ab9768f817ed09017",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    demand = {
        "name": "Structure 1",  # change me!
        "key": "e2dbb85e5a2c494e85d25fec2ead17bf",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    demand = {
        "name": "Structure 2",  # change me!
        "key": "e2dbb85e5a2c494e85d25fec2ead17cg",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    demand = {
        "name": "LH2 Tank Replacement",  # change me!
        "key": "492e355ed3f74034b6d49b0240ff7800",  # change me!
        "database": "maintenance_D250_TF_MHEP"  # change me!
    }
    demand_list.append(demand)
    
    # specify the number of iterations for the Monte Carlo simulation
    iterations = 5000 # change me!
    
    print(f"This machine has {os.cpu_count()} logical cores, using {min(cpu_count(), 60)} cores for parallel processing.")
    
    # setting up Brightway
    brightway_project = "EXACT2_backup_v5" # change me!
    bw.projects.set_current(brightway_project)
    bw.bw2setup()
    
    # specify the LCIA methods to use for the Monte Carlo simulation
    lcia_method_name = 'EF v3.1 no LT'
    lcia_methods = [method for method in bw.methods if lcia_method_name in str(method)]
    
    # here, the impact categories are renamed to a more readable format
    key_list = []
    for method in lcia_methods:
        impact_cat = str(method[1])
        impact_unit = str(bw.methods[method]['unit'])
        key_list.append(impact_cat + ' [' + impact_unit + ']')
    
    # loop over all demands in the demand_list and perform the Monte Carlo simulation
    for i, demand in enumerate(demand_list):
        
        # this calls the parallelised function that performs the Monte Carlo simulation
        perform_monte_carlo(demand, lcia_methods, key_list, brightway_project, iterations=iterations)
        
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
    duration_minutes = duration // 60
    duration_seconds = duration % 60
    duration_hours = duration_minutes // 60

    print("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes = {:.0f}:{:.0f}:{:02}".format(duration, duration_minutes, int(duration_seconds), duration_hours, duration_minutes % 60, int(duration_seconds)))

from brightway2 import *
import time
import os
import json
import numpy as np
import pandas as pd
from utils import *
import tqdm
from multiprocessing import Pool, cpu_count, Manager, Queue

def monte_carlo_worker(args):
    demand, lcia_methods, key_list, brightway_project, iterations, progress_queue = args
    
    # Re-initialize the project and Brightway infrastructure within the worker
    projects.set_current(brightway_project) 
    
    # Load the demand activity
    demand_activity = Database(demand['database']).get(demand['key'])
    
    # Each worker will perform a subset of the iterations
    mc_results = {key: [] for key in key_list}
    
    for _ in range(iterations):
        monte_carlo = MonteCarloLCA({demand_activity: 1}, method=lcia_methods[0])
        monte_carlo.load_data()
        monte_carlo.rebuild_technosphere_matrix(monte_carlo.tech_rng.next())
        monte_carlo.rebuild_biosphere_matrix(monte_carlo.bio_rng.next())
        monte_carlo.build_demand_array()

        monte_carlo.lci_calculation()

        for i, method in enumerate(lcia_methods):
            monte_carlo.switch_method(method)
            monte_carlo.load_data()
            monte_carlo.rebuild_characterization_matrix(monte_carlo.cf_rng.next())
            monte_carlo.lcia_calculation()
            mc_results[key_list[i]].append(monte_carlo.score)
        
        # Report progress for each iteration
        progress_queue.put(1)

    return mc_results


def perform_monte_carlo(demand, lcia_methods, key_list, brightway_project, iterations):
    num_cores = min(cpu_count(), 60) 
    
    # Split the iterations across multiple cores
    iterations_per_core = iterations // num_cores

    manager = Manager()
    progress_queue = manager.Queue()
    
    args = [(demand, lcia_methods, key_list, brightway_project, iterations_per_core, progress_queue) for _ in range(num_cores)]
    
    stamp = str(dt.datetime.now().strftime('%H:%M:%S'))
    
    tprint(f"Performing Monte Carlo simulation for demand: {demand['name']}")
    with tqdm.tqdm(total=iterations, desc=f"{stamp} | Current progress") as pbar:
        with Pool(num_cores) as pool:
            pool_result = pool.map_async(monte_carlo_worker, args)
            
            # Update the progress bar based on messages from the worker processes
            while not pool_result.ready():
                while not progress_queue.empty():
                    pbar.update(progress_queue.get())
    
            pool_result.get()  # To re-raise any exceptions from the workers
    
    # Combine results from all processes
    combined_results = {key: [] for key in key_list}
    for result in pool_result.get():
        for key in key_list:
            combined_results[key].extend(result[key])
    
    # Calculate statistics
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
    
    demand['mc_results'] = combined_results
    demand['mc_statistics'] = mc_statistics

    return demand


if __name__ == "__main__": 
    start_time = time.time()

    filename_input = set_filename("referencecase_eco.xlsx")
    filename_output_json = set_filename("lca_monte_carlo.json")
    filename_output_short_json = set_filename("lca_monte_carlo_statistics.json")
    filename_output_csv = set_filename("lca_monte_carlo.csv")
    
    # read in the data from the output file
    input_data = pd.read_excel(filename_input, sheet_name='Individual LCAs', header=3, usecols='B:ZZZ')
    
    # transform the pandas dataframe into a nested dictionary
    demand_list = [
        {
            'name': row['Name'],
            'key': row['Key'],
            'database': row['Database'],
            'lca_results': {k: v for k, v in row.iloc[4:].items() if not pd.isna(v)}
        }
        for _, row in input_data.iterrows()
    ]
    
    # demand_list = []
    # demand = {
    #     "name": "D-Check",
    #     "key": "93992c7630c84aafa77f3dfe6a79fafc",
    #     "database": "maintenance_D250-TF"
    # }
    # demand_list.append(demand)
    
    iterations = 10000
    
    tprint(f"This machine has {os.cpu_count()} logical cores, using {min(cpu_count(), 60)} cores for parallel processing.")
    
    lyfe_config, airlyfe_config = read_config()
    brightway_project = airlyfe_config.get('LCA', 'brightway_projectname')
    projects.set_current(brightway_project)
    bw2setup()
    
    lcia_method_name = airlyfe_config.get('LCA', 'lcia_method')
    lcia_methods = [method for method in methods if lcia_method_name in str(method)]
    
    key_list = []
    for method in lcia_methods:
        impact_cat = str(method[1])
        impact_unit = str(methods[method]['unit'])
        key_list.append(impact_cat + ' [' + impact_unit + ']')
    
    for i, demand in enumerate(demand_list):
        
        try:
            perform_monte_carlo(demand, lcia_methods, key_list, brightway_project, iterations=iterations)
            
            if 'lca_results' in demand:
                del demand['lca_results']
                
            with open(set_filename("lca_" + str(i+1) + "_monte_carlo.json"), 'w') as file:
                json.dump(demand, file, indent=4)
        
        # if something goes wrong, print the error and continue with the next demand
        except Exception as e:
            tprint(f"Error for demand {demand['name']}: {e}")
            continue
    
    with open(filename_output_json, 'w') as file:
        json.dump(demand_list, file, indent=4) 
        
    for demand in demand_list:
        if 'mc_results' in demand:
            del demand['mc_results']
    with open(filename_output_short_json, 'w') as file:
        json.dump(demand_list, file, indent=4)
         
    end_time = time.time()
    duration = end_time - start_time
    duration_minutes = duration // 60
    duration_seconds = duration % 60

    tprint("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes".format(duration, duration_minutes, int(duration_seconds)))

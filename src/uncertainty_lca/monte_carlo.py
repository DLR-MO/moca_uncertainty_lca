# import brightway
import brightway2 as bw

# import standard python libraries
import numpy as np
import json
import os

# import multiprocessing libraries and a library to make progress bars (tqdm)
import tqdm
from multiprocessing import Pool, cpu_count, Manager, Queue

def get_lcia_methods(lcia_method_name):
    """
    Get LCIA methods and their keys based on the provided method name.
    
    Args:
        lcia_method_name: Name of the LCIA method (e.g., 'EF v3.1 no LT').
        
    Returns:
        lcia_methods: List of LCIA methods.
        key_list: List of keys for the LCIA methods.
    """
    
    lcia_methods = [method for method in bw.methods if lcia_method_name in str(method)]    
    
    # here, the impact categories are renamed to a more readable format
    key_list = []
    for method in lcia_methods:
        impact_cat = str(method[1])
        impact_unit = str(bw.methods[method]['unit'])
        key_list.append(impact_cat + ' [' + impact_unit + ']')

    return lcia_methods, key_list

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
    
    # each worker will perform a subset of the iterations
    mc_results = {key: [] for key in key_list}
    monte_carlo = bw.MonteCarloLCA({demand: 1}, method=lcia_methods[0])
        
    # load data and rebuild matrices
    monte_carlo.load_data()
    
    
    # this is performing the actual Monte Carlo simulation
    for _ in range(iterations):
        monte_carlo.rebuild_technosphere_matrix(monte_carlo.tech_rng.next())
        monte_carlo.rebuild_biosphere_matrix(monte_carlo.bio_rng.next())
        monte_carlo.build_demand_array()
        # initialize the Monte Carlo object
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

def calculate_statistics(mc_results, lcia_method_name):
    """
    Calculate statistics for Monte Carlo results.
    
    Args:
        mc_results: Dictionary containing the Monte Carlo results.
        lcia_method_name: Name of the LCIA method.
        
    Returns:
        mc_statistics: Dictionary containing the calculated statistics.
    """
    
    lcia_methods, key_list = get_lcia_methods(lcia_method_name)
    
    # calculate statistics
    mc_statistics = {}
    for i in range(len(lcia_methods)):
        percentiles = {
            "5": np.percentile(mc_results[key_list[i]], 5),
            "10": np.percentile(mc_results[key_list[i]], 10),
            "25": np.percentile(mc_results[key_list[i]], 25),
            "50": np.percentile(mc_results[key_list[i]], 50),
            "75": np.percentile(mc_results[key_list[i]], 75),
            "90": np.percentile(mc_results[key_list[i]], 90),
            "95": np.percentile(mc_results[key_list[i]], 95)
        }
        mc_statistics[key_list[i]] = {
            "mean": np.mean(mc_results[key_list[i]]),
            "std": np.std(mc_results[key_list[i]]),
            "min": float(np.min(mc_results[key_list[i]])),
            "max": float(np.max(mc_results[key_list[i]])),
            "percentiles": percentiles
        }
        
    return mc_statistics

# this function acts as a wrapper for the Monte Carlo simulation itself and handles parallelisation
def parallel_monte_carlo(demand, lcia_method_name, iterations):
    """
    Perform Monte Carlo simulation for a given demand activity.
    
    Args:
        demand: Dictionary containing the demand activity.
        lcia_method_name: Name of the LCIA method.
        iterations: Number of iterations to perform.
        
    Returns:
        combined_results: Dictionary containing the combined Monte Carlo results from all processes.
    """
    
    lcia_methods, key_list = get_lcia_methods(lcia_method_name)
    
    brightway_project = bw.projects.current
    
    # determine the number of cores to use for parallel processing
    # the maximum number of cores is limited to 60 here to prevent overloading the system with too many parallel processes
    num_cores = min(cpu_count(), 60) 
    print(f"This machine has {cpu_count()} logical cores, using {num_cores} cores for parallel processing.") 
    
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
    
    return combined_results    
    
def write_json(filename, dict_to_write, folder_path=None):
    """
    Write a dictionary to a JSON file.
    
    Args:
        filename: Name of the JSON file.
        dict_to_write: Dictionary to write to the JSON file.
        folder_path: Optional path to the folder where the JSON file will be saved. If None, a default "results" folder is used.
    """
    
    if folder_path is None:
        # specify the path to the output folder that the results will be written to
        folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "results")
    
    with open(os.path.join(folder_path, filename), 'w') as file:
        json.dump(dict_to_write, file, indent=4)
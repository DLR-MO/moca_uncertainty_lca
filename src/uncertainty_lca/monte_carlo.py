# import brightway
from copy import deepcopy
import brightway2 as bw

# import standard python libraries
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
    blueprint = bw.MonteCarloLCA({demand_activity: 1}, method=lcia_methods[0])
        
    # load data and rebuild matrices
    blueprint.load_data()
    
    
    # this is performing the actual Monte Carlo simulation
    for _ in range(iterations):
        working_copy = deepcopy(blueprint)
        working_copy.rebuild_technosphere_matrix(blueprint.tech_rng.next())
        working_copy.rebuild_biosphere_matrix(blueprint.bio_rng.next())
        working_copy.build_demand_array()
        # initialize the Monte Carlo object
        # perform the LCI (this takes a lot of time and is therefore only performed once for all impact categories)
        working_copy.lci_calculation()
        
        # loop over impact categories to perform the LCIA
        for i, method in enumerate(lcia_methods):
            # switch the LCIA method, reload data and rebuild the characterization matrix
            working_copy.switch_method(method)
            working_copy.load_data()
            working_copy.rebuild_characterization_matrix(working_copy.cf_rng.next())
            
            # perform the actual LCIA and store the results
            working_copy.lcia_calculation()
            mc_results[key_list[i]].append(working_copy.score)
        
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
    

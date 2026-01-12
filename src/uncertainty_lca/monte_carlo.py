# import brightway
import brightway2 as bw

# import standard python libraries
import numpy as np
import pandas as pd
import json
import os

# import multiprocessing libraries and a library to make progress bars (tqdm)
from stats_arrays import MCRandomNumberGenerator
import tqdm
from multiprocessing import Pool, cpu_count, Manager

# for logging
import logging
from contextlib import contextmanager

@contextmanager
def silence_logger(logger_name, level=logging.WARNING):
    logger = logging.getLogger(logger_name)
    old_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)

class MonteCarloLCA(bw.LCA):
    
    def __init__(self, demand, lcia_method_name=None, lcia_methods=None, iterations=None, run_parallel=True, num_cores=None):
        """
        Initialize the MonteCarloLCA class.
        
        Parameters
        ----------
            demand : dict
                Dictionary specifying the demand activity.
            lcia_method_name : str, optional
                Name of the LCIA method (e.g., 'EF v3.1 no LT').
            lcia_methods : list, optional
                List of LCIA methods. If provided, 'lcia_method_name' is ignored. Default is None.
            iterations : int, optional
                Number of iterations for the Monte Carlo simulation. Default is None.
            run_parallel : bool, optional
                Whether to run the Monte Carlo simulation in parallel. Default is True.
            num_cores : int, optional
                Number of CPU cores to use for parallel processing. Default is None, which results in the use of all available cores up to a maximum of 60.
        """
        
        # initialize the parent LCA class
        super().__init__(demand)
        
        self.iterations = iterations
        self.run_parallel = run_parallel
        
        self.demand_act = list(demand.keys())[0]
        self.iterations = iterations
        
        self.brightway_project = bw.projects.current 
        
        # using more than 60 cores or more than exist does not work
        max_cores = min(cpu_count(), 60)
        
        self.num_cores = (
            min(num_cores, max_cores)
            if num_cores is not None
            else max_cores
        )
        
        if lcia_methods is None:
            assert lcia_method_name is not None, "Either 'lcia_method_name' or 'lcia_methods' must be provided."
            self.lcia_methods, self.key_list = get_lcia_methods(lcia_method_name)
        else:
            if isinstance(lcia_methods, tuple):
                self.lcia_methods = [lcia_methods]
            elif isinstance(lcia_methods, list):
                self.lcia_methods = lcia_methods
            else:
                raise ValueError("'lcia_methods' must be a tuple or a list of tuples.")
            self.key_list = get_key_list(self.lcia_methods)
            
    @property
    def mc_results(self):
        """
        Property to access Monte Carlo results after simulation.
        """
        
        assert hasattr(self, '_mc_results'), "Monte Carlo simulation has not been executed yet. Please call 'execute_monte_carlo()' first."
        return self._mc_results
        
    def mc_lci_preparation(self, iterations):
        """
        Function to prepare the LCI for Monte Carlo simulation. This includes loading LCI data, generating random numbers, and building the demand array.
        """
        
        # load LCI data
        self.load_lci_data()
        
        # generate random numbers for technosphere and biosphere matrices
        self.tech_rng = MCRandomNumberGenerator(self.tech_params, seed=self.seed)
        self.bio_rng = MCRandomNumberGenerator(self.bio_params, seed=self.seed)
        self.random_tech = self.tech_rng.generate(iterations)
        self.random_bio = self.bio_rng.generate(iterations)
        
        # build the demand array
        self.build_demand_array()
        
    
    def mc_lci_calculation(self, slice_index):
        """
        Function to perform the LCI for one Monte Carlo iteration. This includes rebuilding the technosphere and biosphere matrices with random values.
        """
        
        assert hasattr(self, 'random_tech'), "Random numbers for technosphere matrix not found. Please run 'mc_lci_preparation()' first."
        assert hasattr(self, 'random_bio'), "Random numbers for biosphere matrix not found. Please run 'mc_lci_preparation()' first."
        
        # rebuild the technosphere and biosphere matrices with random values
        self.rebuild_technosphere_matrix(self.random_tech[:,slice_index]) 
        self.rebuild_biosphere_matrix(self.random_bio[:,slice_index]) 
        
        # perform the LCI 
        self.lci_calculation()
        
    def mc_lcia_calculation(self):
        """
        Function to perform the LCIA for one Monte Carlo iteration. This includes loading LCIA data, generating random numbers for the characterization matrix, rebuilding it, and performing the LCIA calculation.
        """
        
        # load LCIA data
        self.load_lcia_data()
        
        # generate random numbers for characterization matrix and rebuild it
        self.cf_rng = MCRandomNumberGenerator(self.cf_params, seed=self.seed)
        self.rebuild_characterization_matrix(self.cf_rng.next())  
        
        # perform the LCIA 
        self.lcia_calculation()
        
    def execute_monte_carlo(self, iterations=None):
        """
        Function to perform a Monte Carlo simulation. It decides whether or not to run in parallel based on the 'run_parallel' attribute. Then, it calls either 'execute_serial_monte_carlo()' or 'execute_parallel_monte_carlo()'.
        
        Parameters
        ----------
            iterations : int, optional
                Number of iterations for the Monte Carlo simulation. If None, the number of iterations provided during initialization is used.        
        """
        
        # determine the number of iterations and make sure it is valid
        if iterations is not None:
            self.iterations = int(iterations)
        if self.iterations is None:
            raise ValueError("Number of iterations must be provided either at when initialising the MonteCarloLCA or when calling 'execute_monte_carlo(iterations=...)'.")
        assert self.iterations > 0, "Number of iterations must be a positive integer."
        
        if self.run_parallel:
            self.execute_parallel_monte_carlo(iterations=self.iterations)
        else:
            self.execute_serial_monte_carlo(iterations=self.iterations)
        
    def execute_serial_monte_carlo(self, iterations):
        """
        Function to perform a Monte Carlo simulation.
        
        Parameters
        ----------
            iterations : int
                Number of iterations for the Monte Carlo simulation.
        """
        
        # each worker will perform a subset of the iterations
        mc_results = {key: [] for key in self.key_list}
                    
        # load data and rebuild matrices
        self.mc_lci_preparation(iterations)
        
        # this is performing the actual Monte Carlo simulation
        for j in tqdm.tqdm(range(iterations), desc="Current progress"):
                    
            # perform the LCI (this takes a lot of time and is therefore only performed once for all impact categories)
            self.mc_lci_calculation(slice_index=j)
            
            # loop over impact categories to perform the LCIA
            for i, method in enumerate(self.lcia_methods):
                # switch the LCIA method, reload data and rebuild the characterization matrix
                with silence_logger("bw2calc"):
                    self.switch_method(method)
                self.mc_lcia_calculation()
                
                mc_results[self.key_list[i]].append(self.score)
                
        self._mc_results = mc_results    
    
    def _split_iterations(self, iterations, num_workers):
        """
        Split the total number of iterations into nearly equal parts for each worker.
        """
        
        base = iterations // num_workers
        remainder = iterations % num_workers
        return [base + (1 if i < remainder else 0) for i in range(num_workers)]

    def execute_parallel_monte_carlo(self, iterations):
        """
        Function to perform a parallelised Monte Carlo simulation.
        
        Parameters
        ----------
            iterations : int
                Number of iterations for the Monte Carlo simulation.
        
        """
        
        # make sure that we do not create more workers than iterations
        num_workers = min(self.num_cores, iterations) 
        
        # split the iterations across multiple workers
        iterations_per_worker = self._split_iterations(iterations, num_workers)
        
        print(f"This machine has {cpu_count()} logical cores, using {num_workers} cores for parallel processing.")
        
        # initialize a progress queue for reporting progress
        manager = Manager()
        progress_queue = manager.Queue()
        
        # create a list of arguments for the worker processes
        args = [(iterations_per_worker[i], progress_queue) for i in range(num_workers)]
            
        print(f"Performing Monte Carlo simulation for demand: {self.demand_act['name']}")
        
        # perform the parallelised Monte Carlo Simulation 
        with tqdm.tqdm(total=iterations, desc=f"Current progress") as pbar:
            with Pool(num_workers) as pool:
                
                # start the worker processes
                pool_result = pool.map_async(self.monte_carlo_worker, args)
                
                # update the progress bar based on messages from the worker processes
                while not pool_result.ready():
                    while not progress_queue.empty():
                        pbar.update(progress_queue.get())

                # wait for all worker processes to finish
                pool_result.get()  
        
        # combine results from all processes
        combined_results = {key: [] for key in self.key_list}
        for result in pool_result.get():
            for key in self.key_list:
                combined_results[key].extend(result[key])
        
        self._mc_results = combined_results
        
    def monte_carlo_worker(self, args):
        """
        Worker function for Monte Carlo simulation. Each worker will perform a subset of the iterations.
        
        Parameters
        ----------
            args : tuple
                Tuple containing the following elements:
            iterations : int
                Number of iterations to perform in this worker.
            progress_queue : Queue
                Queue for reporting progress.
                
        Returns
        -------
            mc_results : dict
                Dictionary containing the Monte Carlo results      
        """
        iterations, progress_queue = args
        
        # re-initialize the project and Brightway infrastructure within the worker
        # this is needed for the parallelisation because Brightway is not thread-safe
        bw.projects.set_current(self.brightway_project) 
        
        # each worker will perform a subset of the iterations
        worker_mc_results = {key: [] for key in self.key_list}
            
        # load data and rebuild matrices
        self.mc_lci_preparation(iterations)
        
        # this is performing the actual Monte Carlo simulation
        for j in range(iterations):
                    
            # perform the LCI (this takes a lot of time and is therefore only performed once for all impact categories)
            self.mc_lci_calculation(slice_index=j)
            
            # loop over impact categories to perform the LCIA
            for i, method in enumerate(self.lcia_methods):
                # switch the LCIA method, reload data and rebuild the characterization matrix
                self.switch_method(method)
                self.mc_lcia_calculation()
                
                worker_mc_results[self.key_list[i]].append(self.score)
            
            # Report progress for each iteration
            progress_queue.put(1)

        return worker_mc_results
    
    def results_to_json(self, filename=None, identifier='name', folder_path=None):
        """
        Save Monte Carlo results to a JSON file.
        
        Parameters
        ----------
            filename : str, optional
                Name of the JSON file to save the results. If None, a default filename based on the demand activity name is used.
            identifier : str, optional
                Identifier to use for the filename. Default is 'name', i.e. the name of the demand activity.
            folder_path : str, optional
                Path to the folder where the JSON file will be saved. Default is None.
        """
        
        info_dict = {
            'name': self.demand_act['name'],
            'code': self.demand_act['code'],
            'database': self.demand_act['database']
        }
        
        if filename is None:
            assert identifier in self.demand_act, f"Identifier '{identifier}' not found in demand activity."
        
            write_json(f"mc_results_{str(self.demand_act[identifier]).replace(' ','_')}_monte_carlo.json", info_dict | self._mc_results, folder_path=folder_path)
        else:
            write_json(filename, info_dict | self._mc_results, folder_path=folder_path)
        
    def stats_to_json(self, filename=None, identifier='name', folder_path=None):
        """
        Save Monte Carlo statistics to a JSON file.
        
        Parameters
        ----------
            identifier : str, optional
                Identifier to use for the filename. Default is 'name', i.e. the name of the demand activity.
            folder_path : str, optional
                Path to the folder where the JSON file will be saved. Default is None.
        """
        
        
        statistics = calculate_statistics(self._mc_results, lcia_methods=self.lcia_methods, key_list=self.key_list)
        
        info_dict = {
            'name': self.demand_act['name'],
            'code': self.demand_act['code'],
            'database': self.demand_act['database']
        }
        
        if filename is None:
            assert identifier in self.demand_act, f"Identifier '{identifier}' not found in demand activity."
            
            write_json(f"mc_stats_{str(self.demand_act[identifier]).replace(' ','_')}_monte_carlo.json", info_dict | statistics, folder_path=folder_path)
        else: 
            write_json(filename, info_dict | statistics, folder_path=folder_path)
            
    def get_results_dataframe(self, method=None):
        """
        Return Monte Carlo results as a Pandas DataFrame.
        Useful for integration with Activity Browser.

        Rows correspond to Monte Carlo iterations.
        Columns correspond to LCIA methods (impact categories).

        Returns
        -------
        pandas.DataFrame
            DataFrame of shape (iterations, n_methods)
        """
        
        results = self.mc_results
        
        idx = self.lcia_methods.index(method)
        key = self.key_list[idx]
        
        return pd.DataFrame({key: results[key]})
        

        data = {
            key: results[key]
            for key in self.key_list
        }

        return pd.DataFrame(data)

def get_lcia_methods(lcia_method_name, get_keys=False):
    """
    Get LCIA methods and their keys based on the provided method name.
    
    Parameters
    ----------
        lcia_method_name : str
            Name of the LCIA method (e.g., 'EF v3.1 no LT').
        
    Returns
    -------
        lcia_methods : list
            List of LCIA methods. 
        key_list : list
            List of keys for the LCIA methods.
    """
    
    lcia_methods = [method for method in bw.methods if lcia_method_name in str(method)]  
    key_list = get_key_list(lcia_methods)
    
    return lcia_methods, key_list
    
def get_key_list(lcia_methods):
    """
    Get a list of keys for the provided LCIA methods.
    
    Parameters
    ----------
        lcia_methods : list
            List of LCIA methods.
            
    Returns
    -------
        key_list : list
            List of keys for the LCIA methods.
    """
    
    # here, the impact categories are renamed to a more readable format
    key_list = []
    for method in lcia_methods:
        impact_cat = str(method[1])
        impact_unit = str(bw.methods[method]['unit'])
        key_list.append(impact_cat + ' [' + impact_unit + ']')

    return key_list

def calculate_statistics(mc_results, lcia_method_name=None, lcia_methods=None, key_list=None):
    """
    Calculate statistics for Monte Carlo results.
    
    Parameters
    ----------
        mc_results : dict
            Dictionary containing the Monte Carlo results.
        lcia_methods : list
            List of LCIA methods.
        key_list : list
            List of keys for the LCIA methods.
        
    Returns
    -------
        mc_statistics : dict
            Dictionary containing the calculated statistics.
    """
    
    if lcia_methods is None:
        assert lcia_method_name is not None, "Either 'lcia_method_name' or 'lcia_methods' must be provided."
        lcia_methods, key_list = get_lcia_methods(lcia_method_name)
    else:
        assert key_list is not None, "key_list must be provided if lcia_method_name is not provided."
    
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
    
def write_json(filename, dict_to_write, folder_path=None):
    """
    Write a dictionary to a JSON file.
    
    Parameters
    ----------
    filename : str
        Name of the JSON file to write.
    dict_to_write : dict
        Dictionary to write to the JSON file.
    folder_path : str, optional
        Path to the folder where the JSON file will be saved. If None, a default "results" folder is used.
       
    """
    
    if folder_path is None:
        folder_path = os.path.join(os.getcwd(), "results")
        
    # create the folder if it does not exist
    os.makedirs(folder_path, exist_ok=True)
    
    with open(os.path.join(folder_path, filename), 'w') as file:
        json.dump(dict_to_write, file, indent=4)
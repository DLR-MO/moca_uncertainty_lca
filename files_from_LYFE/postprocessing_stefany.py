# import standard libraries
import json
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# import the library that is needed for the fitting itself
from scipy import stats

# ignore RuntimeWarnings 
import warnings
warnings.filterwarnings("ignore")

# this is the function to perform fitting of the distributions
def fit_distributions(data):
    """
    This function fits different distributions to the data and calculates the mean squared error.
    The best fit distribution is chosen based on the lowest mean squared error.
    The results are saved in an Excel file called 'distribution_fitting.xlsx'.
    
    Args:
        data (list): a list of dictionaries, where each dictionary corresponds to a demand
        
    Returns:
        None
    """
    
    # set the list of distributions to be used for fitting
    # you can change this and include and distribution from scipy.stats that you like!
    distributions = [stats.cauchy, stats.norm, stats.lognorm, stats.skewnorm, stats.alpha, stats.beta, stats.gamma]

    # Create a Pandas Excel writer object
    with pd.ExcelWriter(os.path.join(os.path.dirname(os.path.realpath(__file__)),'distribution_fitting.xlsx')) as writer:
        for demand in data:

            # Create a DataFrame to store the errors of the distributions
            errors_df = pd.DataFrame(index=[dist.name for dist in distributions])
            demand['distribution_results'] = {}

            for impact_category, values in demand['mc_results'].items():

                # correctly format input values and filter out outliers
                values = np.array(values)
                values = values[(values >= 0) & (values <= (values.mean() + values.std()))]

                # initialize the list of distribution results for the impact_category
                demand['distribution_results'][impact_category] = []
                
                # iterate over the distributions from scipy.stats
                for distribution in distributions:          

                    try:
                        # Fit the distribution to the data using the mean and standard deviation as initial parameters
                        params = distribution.fit(values,
                                                  loc=demand['mc_statistics'][impact_category]['mean'],
                                                  scale=demand['mc_statistics'][impact_category]['std'])

                        # Generate fitted distribution values (PDF) at specific points
                        x = np.linspace(min(values), max(values), len(values))
                        pdf_values = distribution.pdf(x, *params[:-2], loc=params[-2], scale=params[-1])

                        # Calculate histogram of the data (normalized to match the PDF scale)
                        hist, bin_edges = np.histogram(values, bins='auto', density=True)
                        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

                        # Calculate the mean squared error
                        error = np.mean((pdf_values - np.interp(x, bin_centers, hist)) ** 2)
                        
                        # Store the error in the DataFrame
                        errors_df.loc[distribution.name, impact_category] = error
                        
                        demand['distribution_results'][impact_category].append({
                            'distribution': distribution.name,
                            'params': params,
                            'error': error
                        })

                    # if the distribution fitting fails, store NaN in the DataFrame and try the next distribution
                    except:
                        errors_df.loc[distribution.name, impact_category] = np.nan
                
                # count how many times each distribution has the lowest error
                lowest_errors = errors_df.idxmin(axis=0)
                distribution_counts = lowest_errors.value_counts()
                
                # append the counts to the errors_df
                errors_df['best fit'] = distribution_counts
                
                # reorder the errors_df to put the best_fit column at the beginning of the DataFrame
                errors_df = errors_df[['best fit'] + [col for col in errors_df.columns if col != 'best fit']]

            # Write the errors DataFrame to a new sheet in the Excel file
            errors_df.to_excel(writer, sheet_name=demand['name'][-30:])
            n_skiprows_error_df = errors_df.shape[0]
            
            # find the distribution with the highest count of best fits
            best_fit = errors_df['best fit'].idxmax()
            print(f"The best fit for the demand {demand['name']} is {best_fit}")
            
            # find the index of the best fit distribution in the list of distributions
            best_fit_index = errors_df.index.get_loc(best_fit)
            demand['best_fit'] = {
                'distribution': best_fit,
                'params': {}
            }
            
            # if the best fit distribution does not converge for all impact categories, pick the next best fit
            def pick_next_best_fit(demand, errors_df, best_fit):
                try:
                    
                    errors_df.drop(best_fit, axis=0, inplace=True)
                    best_fit = errors_df['best fit'].idxmax()
                    best_fit_index = errors_df.index.get_loc(best_fit)
                    
                    print(f"Warning: Some impact categories do not converge for previous fit, trying {best_fit} now")
                    
                    demand['best_fit'] = {
                        'distribution': best_fit,
                        'params': {}
                    }
                    for impact_category, results in demand['distribution_results'].items():
                        demand['best_fit']['params'][impact_category] = results[best_fit_index]['params']
                        
                # if the next best fit does not work either, recursively try the next best fit
                except:
                    pick_next_best_fit(demand, errors_df, best_fit)
                            
            try:
                for impact_category, results in demand['distribution_results'].items():
                    demand['best_fit']['params'][impact_category] = results[best_fit_index]['params']
                    
            # if for some impact categories, the overall best fit distribution does not converge,
            # the second best fit distribution is chosen (iteratively, if necessary)
            except:
                pick_next_best_fit(demand, errors_df, best_fit)                  
            
            # write the name of the best fit to excel
            best_fit_df = pd.DataFrame({'best_fit': [demand['best_fit']['distribution']]})
            best_fit_df.to_excel(writer, sheet_name=demand['name'][-30:], startrow=n_skiprows_error_df + 2, index=False)
            
            # create a list of index names for the best fit parameters
            if demand['best_fit']['distribution'] in ('cauchy','norm'):
                index_list = ['loc', 'scale']
            elif demand['best_fit']['distribution'] == 'lognorm':
                index_list = ['s', 'loc', 'scale']
            elif demand['best_fit']['distribution'] in ('skewnorm', 'alpha', 'gamma'):
                index_list = ['a', 'loc', 'scale']
            elif demand['best_fit']['distribution'] == 'beta':
                index_list = ['a', 'b', 'loc', 'scale']
            else:
                raise ValueError(f"Unknown distribution {demand['best_fit']['distribution']}")
            
            # write the best fit parameters for each impact_category to excel
            params_df = pd.DataFrame(demand['best_fit']['params'])
            params_df.set_index(pd.Index(index_list), inplace=True)
            params_df.to_excel(writer, sheet_name=demand['name'][-30:],
                               startrow=n_skiprows_error_df + best_fit_df.shape[0] + 4,
                               startcol=1)             

# this is a very rudementary plotting function, you can customize it to your needs
# it is not very nice definitely (sorry about that!), but it should give you a starting point
def plotting(data):
    """
    This function creates a histogram of the data and plots the best fit distribution on top of it.
    The plots are saved in a folder called 'plots' in the same directory as the script.
    
    Args:
        data (list): a list of dictionaries, where each dictionary corresponds to a demand
    """
    
    # create a folder for the plots
    plot_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'plots')
    if not os.path.exists(plot_folder):
        os.makedirs(plot_folder)
        
    for demand in data:        
        for impact_category, values in demand['mc_results'].items():
                
                plt.figure(figsize=(10, 6))
                # correctly format input values and filter out outliers
                values = np.array(values)
                values = values[(values >= 0) & (values <= (values.mean() + values.std()))]
                
                # plot the histogram of the data
                plt.hist(values, bins='auto', density=True, alpha=0.5, label='Histogram')
                
                # plot the best fit distribution
                distribution = getattr(stats, demand['best_fit']['distribution'])
                params = demand['best_fit']['params'][impact_category]
                x = np.linspace(min(values), max(values), len(values))
                pdf_values = distribution.pdf(x, *params[:-2], loc=params[-2], scale=params[-1])
                plt.plot(x, pdf_values, label=demand['best_fit']['distribution'])
                
                # check for any weird characters in the impact category and replace them with underscores
                impact_category = ''.join(e for e in impact_category if e.isalnum() or e.isspace())
                
                if demand['name'] == 'Aircraft':
                    plt.title(f"{demand['name']} - {demand['database']}\n - {impact_category}")
                plt.title(f"{demand['name']} - {impact_category}")
                plt.xlabel("Impact score")
                plt.ylabel("Density")
                plt.legend()
                if demand['name'] == 'Aircraft':
                    plt.savefig(os.path.join(plot_folder, f"{demand['name']}_{demand['database']}_{impact_category}.png"))#
                else:
                    plt.savefig(os.path.join(plot_folder, f"{demand['name']}_{impact_category}.png"))
                plt.close()
             

### this is where the code is actually executed

# time tracking
start_time = time.time()

# find the current folder path
folder_path = os.path.dirname(os.path.realpath(__file__))

# create a list of input files that is sorted correctly from "lca_1_monte_carlo.json" to "lca_n_monte_carlo.json"
input_file_list = [file for file in os.listdir(folder_path) if file.startswith("lca_") and file.endswith("_monte_carlo.json") and file != "lca_monte_carlo.json"]

# sort the list alphabetically to ensure the files are processed in the correct order
input_file_list.sort()

# read the data from the json files
data = []
for file in input_file_list:
    with open(os.path.join(folder_path, file), 'r') as file:
        data.append(json.load(file))
        
print(f"Successfully read the data from {len(data)} files in the folder {folder_path}")

# call the function to fit the data
fit_distributions(data)

# call the function to perform some simple plotting
plotting(data)

# time tracking
end_time = time.time()

duration = end_time - start_time
duration_minutes = duration // 60
duration_seconds = duration % 60

print("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes".format(duration, duration_minutes, int(duration_seconds)))

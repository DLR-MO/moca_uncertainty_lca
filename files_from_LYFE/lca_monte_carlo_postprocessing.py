import json
import os
import time
import numpy as np
import scipy.stats as stats
import pandas as pd
import matplotlib.pyplot as plt
from utils import *

# ignore RuntimeWarnings
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.font_manager as fm
fm.fontManager.addfont('C://Users//hoel_m0//AppData//Local//Microsoft//Windows//Fonts//latin-modern-roman.mroman12-regular.otf')

def fit_distributions(data):
    
    # set the list of distributions to be used for fitting
    distributions = [stats.cauchy, stats.norm, stats.skewnorm, stats.alpha, stats.beta, stats.gamma] # stats.lognorm, 

    # Create a Pandas Excel writer object
    with pd.ExcelWriter(set_filename('distribution_fitting.xlsx')) as writer:
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
            errors_df.to_excel(writer, sheet_name=demand['name_plots'][-30:])
            n_skiprows_error_df = errors_df.shape[0]
            
            # find the distribution with the highest count of best fits
            best_fit = errors_df['best fit'].idxmax()
            tprint(f"The best fit for the demand {demand['name_plots']} is {best_fit}")
            
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
                    
                    tprint(f"Warning: Some impact categories do not converge for previous fit, trying {best_fit} now")
                    
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
            params_df.to_excel(writer, sheet_name=demand['name_plots'][-30:],
                               startrow=n_skiprows_error_df + best_fit_df.shape[0] + 4,
                               startcol=1)


def create_sampling_setup_from_json(data, output_file):
    # Create ConfigParser and read the sampling_setup.ini file
    sampling_setup = ExtendedConfigParser() 
    sampling_setup.read(output_file) 

    # make sure to overwrite the [LCA] section in the file or add it if it does not exist
    if sampling_setup.has_section('LCA'):
        sampling_setup.remove_section('LCA')
        tprint("Found [LCA] section in the file. Will overwrite it now.")
    else:
        tprint("No [LCA] section found in the file. Adding it now.")

    sampling_setup.add_section('LCA')

    # iterate over the demands and write the information to the sampling_setup.ini file
    for i, demand in enumerate(data):

        # initialze the lists for the mean and standard deviation values        
        mean_list = []
        std_list = []
        
        # iterate over the impact categories and append the mean and standard deviation values to the lists
        for impact_category in demand['mc_statistics']:
            mean_list.append(demand['mc_statistics'][impact_category]['mean'])
            std_list.append(demand['mc_statistics'][impact_category]['std'])

        # write the identifier and distribution type
        sampling_setup.set(section='LCA', option='lca_' + str(i+1) + '_info',
                           value="'" + demand['name'] + '; ' + demand['database'] + '; ' + demand['key'] + "'")
        sampling_setup.set(section='LCA', option='lca_' + str(i+1) + '_distr',
                           value=demand['best_fit']['distribution'])

        for j in range(len(mean_list)):
            # write the mean and standard deviation parameters for each impact category after the other
            sampling_setup.setlist(section='LCA', option='lca_' + str(i+1) + '_loc',
                                   value=[str(mean_list[j])], mode='extend')
            sampling_setup.setlist(section='LCA', option='lca_' + str(i+1) + '_scale',
                                   value=[str(std_list[j])], mode='extend')
            
            # depending on the distribution type, write the additional parameters
            if demand['best_fit']['distribution'] in ('skewnorm', 'alpha', 'gamma'):
                sampling_setup.setlist(section='LCA', option='lca_' + str(i+1) + '_shape_a',
                                       value=[str(demand['best_fit']['params'][list(demand['mc_statistics'].keys())[j]][0])], mode='extend')
            elif demand['best_fit']['distribution'] == 'beta':
                sampling_setup.setlist(section='LCA', option='lca_' + str(i+1) + '_shape_a',
                                        value=[str(demand['best_fit']['params'][list(demand['mc_statistics'].keys())[j]][0])], mode='extend')
                sampling_setup.setlist(section='LCA', option='lca_' + str(i+1) + '_shape_b',
                                        value=[str(demand['best_fit']['params'][list(demand['mc_statistics'].keys())[j]][1])], mode='extend')
            elif demand['best_fit']['distribution'] == 'lognorm':
                sampling_setup.setlist(section='LCA', option='lca_' + str(i+1) + '_shape_s',
                                        value=[str(demand['best_fit']['params'][list(demand['mc_statistics'].keys())[j]][0])], mode='extend')
            else:
                pass
            
    # write the new sampling_setup.ini file
    with open(output_file, 'w') as file:
        sampling_setup.write(file)

    tprint(f"Finished writing the new sampling_setup.ini file to the folder {os.path.dirname(output_file)}")
    
def plot_convergence(data):
    # for each demand, take the data for climate change and plot the convergence of the Monte Carlo simulation
    
    # change the font to LM Roman 12
    plt.rcParams['font.family'] = 'Latin Modern Roman'
    # make the font size larger
    plt.rcParams.update({'font.size': 19})
    
    # plot settings
    dpi_setting = 600

    # custom define colours
    blue = '#00668d'
    light_blue = '#0099CE'
    green = '#73a237'
    light_green = '#9cc045'
    gray = '#686867'
    light_gray = '#b2b2b2'
    
    for demand in data:
        
        try:
            plotting_data = demand['mc_results']['climate change no LT [kg CO2-Eq]']
            final_mean = demand['mc_statistics']['climate change no LT [kg CO2-Eq]']['mean']
            final_std = demand['mc_statistics']['climate change no LT [kg CO2-Eq]']['std']
        except KeyError:
            plotting_data = demand['mc_results']['climate change [kg CO2-Eq]']
            final_mean = demand['mc_statistics']['climate change [kg CO2-Eq]']['mean']
            final_std = demand['mc_statistics']['climate change [kg CO2-Eq]']['std']
                
        # plot the results of the Monte Carlo simulation
        plt.figure(figsize=(6,5))
        
        # for the labels
        plt.scatter(np.arange(1, len(plotting_data)+1), plotting_data, color=gray, alpha=0.5, s=6, linewidth=0, label='Simulation Results')
        plt.axhline(y=final_mean, color=blue, linestyle='--', label='Mean Value', linewidth=2)
        
        # fill the area between the mean and the mean ± std along the whole width of the plot
        plt.fill_between(np.arange(1, len(plotting_data)+1), final_mean - final_std, final_mean + final_std, color=light_green, alpha=0.5, linewidth=0, label='Mean ± Standard Deviation')
        # plt.plot(np.arange(1, len(plotting_data)+1), plotting_data, label='Simulation Results')
        # plot the results as points instead of lines
        plt.scatter(np.arange(1, len(plotting_data)+1), plotting_data, color=gray, alpha=0.5, s=6, linewidth=0)
        plt.axhline(y=final_mean, color=blue, linestyle='--', linewidth=2)
        # plt.axhline(y=final_mean + final_std, color=green, linestyle='--', label='Mean ± Standard Deviation', linewidth=2)
        # plt.axhline(y=final_mean - final_std, color=green, linestyle='--', linewidth=2)
        plt.xlabel('Number of Iterations')
        
        plt.ylabel('CC Impact [kg CO2-Eq]')
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        
        # plt.title(f'Results of Monte Carlo Simulation for {demand["name_plots"]}')
        
        # set the x axis to between 0 and 10,000
        plt.xlim(0, len(plotting_data) + 1)
        
        plt.legend(fontsize=17)
        plt.tight_layout()
        plt.savefig(set_filename(f'results_{demand["name_files"]}.png', folder='outputs'), dpi=dpi_setting)
        
        # plot the convergence of the Monte Carlo simulation
        # calculate the convergence of the mean and standard deviation of the results and plot it how it changes with each additional datapoint
        # plot the mean with an axis on the left side and the std with an axis on the right side
        
        mean_values = np.array([np.mean(plotting_data[:i]) for i in range(1, len(plotting_data)+1)]) 
        std_values = np.array([np.std(plotting_data[:i]) for i in range(1, len(plotting_data)+1)])

        # Plot mean on the left y-axis
        fig, ax1 = plt.subplots(figsize=(6, 5))

        color = blue
        ax1.set_xlabel('Number of Iterations')
        ax1.set_ylabel('Mean Value [kg CO2-Eq]', color=color)
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        ax1.plot(np.arange(1, len(plotting_data)+1), mean_values, label='Mean Value', color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.axhline(y=final_mean, linestyle='--', label='Final Mean Value')

        # Create a second y-axis for the standard deviation
        ax2 = ax1.twinx()  
        color = green
        ax2.set_ylabel('Standard Deviation [kg CO2-Eq]', color=color)  
        plt.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        ax2.plot(np.arange(1, len(plotting_data)+1), std_values, label='Standard Deviation', color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.axhline(y=final_std, color=color, linestyle='--', label='Final Standard Deviation')

        # Add the title and layout adjustments
        # plt.title(f'Convergence of Monte Carlo Simulation for {demand["name_plots"]}')
        fig.tight_layout()

        # Save the figure
        plt.savefig(set_filename(f'convergence_{demand["name_files"]}.png', folder='outputs'), dpi=dpi_setting)
        
        tprint(f"Successfully plotted the convergence of the Monte Carlo simulation for {demand['name_plots']}")
        
        

# time tracking
start_time = time.time()

# find the correct project output folder
lyfe_config, airlyfe_config = read_config()
dpath_project = os.path.realpath(os.path.join(
        os.path.realpath(os.path.dirname(os.path.dirname(__file__))), 'projects', lyfe_config.get('General', 'projectName')
    ))
output_folder_path = os.path.realpath(os.path.join(dpath_project, 'outputs'))

# create a list of input files that is sorted correctly from "lca_1_monte_carlo.json" to "lca_n_monte_carlo.json"
# the files need to be in the outputs folder
input_file_list = [file for file in os.listdir(output_folder_path) if file.startswith("lca_") and file.endswith("_monte_carlo.json")]
input_file_list.sort(key=lambda x: int(x.split('_')[1]))

# set the output file
output_file = set_filename("sampling_setup.ini", folder="inputs")

# read the data from the json files
data = []
for file in input_file_list:
    with open(os.path.join(output_folder_path, file), 'r') as file:
        data.append(json.load(file))
        
# read the file 'Overview_Individual_LCAs.xlsx' and get the name_plots and name_files for each demand
# this is necessary to correctly name the plots and output files
overview_file = set_filename("Overview_Individual_LCAs.xlsx", folder="inputs")
overview_data = pd.read_excel(overview_file)

for demand in data:
    demand['name_plots'] = overview_data.loc[overview_data['Demand name'].str.lower() == demand['name'].lower(), 'Name for Plots'].values[0]
    demand['name_files'] = overview_data.loc[overview_data['Demand name'].str.lower() == demand['name'].lower(), 'Name for Files'].values[0]

tprint(f"Successfully read the data from {len(data)} files in the folder {output_folder_path}")

# filter out outliers in the data that are more than 6 standard deviations away from the mean
for demand in data:
    for impact_category, values in demand['mc_results'].items():
        values = np.array(values)
        mean = values.mean()
        std = values.std()
        demand['mc_results'][impact_category] = values[(values >= 0) & (values <= (mean + 6 * std))]
        
        # recalculate the statistics for the filtered data
        demand['mc_statistics'][impact_category] = {
            'mean': demand['mc_results'][impact_category].mean(),
            'std': demand['mc_results'][impact_category].std()
        }       
        
tprint("Successfully filtered out outliers in the data")

# call the functions
plot_convergence(data)
# fit_distributions(data)
# create_sampling_setup_from_json(data, output_file)

# time tracking
end_time = time.time()

duration = end_time - start_time
duration_minutes = duration // 60
duration_seconds = duration % 60

tprint("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes".format(duration, duration_minutes, int(duration_seconds)))

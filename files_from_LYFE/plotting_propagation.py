import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import json
import time

from utils import *

import matplotlib.font_manager as fm
fm.fontManager.addfont('C://Users//hoel_m0//AppData//Local//Microsoft//Windows//Fonts//latin-modern-roman.mroman12-regular.otf')

# time tracking
start_time = time.time()

# ------------------- Read the input data -------------------

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

# read the data from the json files
data = []
for file in input_file_list:
    with open(os.path.join(output_folder_path, file), 'r') as file:
        data.append(json.load(file))
        
# only take the first 23 demands
data = data[:23]
        
# read the file 'Overview_Individual_LCAs.xlsx' and get the name_plots and name_files for each demand
# this is necessary to correctly name the plots and output files
overview_file = set_filename("Overview_Individual_LCAs.xlsx", folder="inputs")
overview_data = pd.read_excel(overview_file)

# read the min-mean-max propagation data from 'mmm_propagation_TF.xlsx', sheets "Minima" and "Maxima"
mmm_file = set_filename("mmm_propagation_TF.xlsx", folder="outputs")
minimum_data = pd.read_excel(mmm_file, sheet_name="Minima")
maximum_data = pd.read_excel(mmm_file, sheet_name="Maxima")

for demand in data:
    demand['name_plots'] = overview_data.loc[overview_data['Demand name'].str.lower() == demand['name'].lower(), 'Name for Plots'].values[0]
    demand['name_files'] = overview_data.loc[overview_data['Demand name'].str.lower() == demand['name'].lower(), 'Name for Files'].values[0]
    demand['deterministic_result'] = overview_data.loc[overview_data['Demand name'].str.lower() == demand['name'].lower(), 'Deterministic result (CC)'].values[0]
    demand['minimum_result'] = minimum_data.loc[minimum_data['demand'].str.lower() == demand['name'].lower(), 'CC'].values[0]
    demand['maximum_result'] = maximum_data.loc[maximum_data['demand'].str.lower() == demand['name'].lower(), 'CC'].values[0]

tprint(f"Successfully read the data from {len(data)} files in the folder {output_folder_path}")

# filter out outliers in the data that are more than 6 standard deviations away from the mean
for demand in data:
    for impact_category, values in demand['mc_results'].items():
        values = np.array(values)
        mean = values.mean()
        std = values.std()
        demand['mc_results'][impact_category] = values[(values >= 0) & (values <= (mean + 4 * std))]
        
        # recalculate the statistics for the filtered data
        demand['mc_statistics'][impact_category] = {
            'mean': demand['mc_results'][impact_category].mean(),
            'std': demand['mc_results'][impact_category].std()
        }       
        
tprint("Successfully filtered out outliers in the data")

# ------------------- Set up the plot -------------------

# set the font to 'Frutiger 45 Light'
plt.rcParams['font.family'] = 'Frutiger'
plt.rcParams['font.weight'] = 'light'

# custom define colours
blue = '#00668d'
light_blue = '#0099CE'
yellow = '#e0B02e'
green = '#73a237'
light_green = '#9cc045'
gray = '#686867'

# set up the plot
plt.figure(figsize=(10, 6))


# ----- Extract the data and crate the violin and box plot -----

for demand in data:
    if 'climate change [kg CO2-Eq]' in demand['mc_results']:
        demand['mc_results']['climate change no LT [kg CO2-Eq]'] = demand['mc_results']['climate change [kg CO2-Eq]']

plotting_data = [demand['mc_results']['climate change no LT [kg CO2-Eq]'] for demand in data]

# normalise the plotting data to the deterministic result
for i, demand in enumerate(data):
    if demand['deterministic_result'] == 0:
        demand['deterministic_result'] = 0.000001
    plotting_data[i] = [result / demand['deterministic_result'] * 100 for result in plotting_data[i]]

# set up positioning of Monte Carlo (on the left, reused for box plot)
positions = [i - 0.2 for i in range(len(data))]

# Create the half violin plot
parts = plt.violinplot(plotting_data, positions, showextrema=False)

for i, pc in enumerate(parts['bodies']):
    path = pc.get_paths()[0]
    vertices = path.vertices
    
    # Only keep the left half
    vertices[:, 0] = np.clip(vertices[:, 0], -np.inf, np.median(vertices[:, 0]))
    pc.set_verts([vertices])
    pc.set_facecolor(light_blue)
    
# settings for the box plot
flierprops = dict(marker='o', markerfacecolor=light_blue, markersize=3, markeredgecolor='none')
whiskerprops = dict(color=light_blue)
boxprops = dict(color=light_blue)
medianprops = dict(color=light_blue)
capsprops = dict(color=light_blue)

# Create the box plot
# plt.boxplot(plotting_data, positions=positions, widths=0.19, whis=[5, 95], notch=False, flierprops=flierprops, boxprops=boxprops, medianprops=medianprops, whiskerprops=whiskerprops, capprops=capsprops)


# # ------------------- Load Data -------------------

# # load the accumulated data
# monte_carlo_df = pd.read_csv(set_filename('monte_carlo_result2.csv'))
# min_mean_max_df = pd.read_csv(set_filename('min_mean_max.csv'))

# # normalize data to the original score
# monte_carlo_df['min_norm'] = monte_carlo_df["5th Percentile"] / monte_carlo_df['Original Score [kg CO2-eq]'] * 100
# monte_carlo_df['max_norm'] = monte_carlo_df["95th Percentile"] / monte_carlo_df['Original Score [kg CO2-eq]'] * 100
# monte_carlo_df['mean_norm'] = monte_carlo_df['Mean'] / monte_carlo_df['Original Score [kg CO2-eq]'] * 100
# monte_carlo_df['original_score_norm'] = 100

# min_mean_max_df['min_norm'] = min_mean_max_df['Minimum'] / min_mean_max_df['Original Score [kg CO2-eq]'] * 100
# min_mean_max_df['max_norm'] = min_mean_max_df['Maximum'] / min_mean_max_df['Original Score [kg CO2-eq]'] * 100
# min_mean_max_df['original_score_norm'] = 100

# # load the individual MC results from json file
# with open(set_filename('monte_carlo_result2.json'), 'r') as file:
#     monte_carlo_json = json.load(file)
    
# mc_results = [
#     [result / demand['score'] * 100 for result in demand['mc_results']]
#     for demand in monte_carlo_json
# ]

# # remove any data points that are below 0 and indicate the number of datapoints that have been removed
# for i, results in enumerate(mc_results):
#     removed = 0
#     for j, result in enumerate(results):
#         if result < 0:
#             # do not set to zero, but remove the data point
#             mc_results[i][j] = mc_results[i][j+1]
#             removed += 1
#     if removed > 0:
#         print("Removed", removed, "data point(s) below 0 for demand", monte_carlo_json[i]['name'])

    
# ----------------- Whiskers Plot ----------------

    
# # plot Monte Carlo 
# for i, row in monte_carlo_df.iterrows():
#     plt.plot([i - 0.1, i - 0.1], [row['min_norm'], row['max_norm']], color=light_blue, label='Monte Carlo' if i == 0 else "", zorder=1)
#     plt.scatter(i - 0.1, row['min_norm'], color=light_blue, marker='_', zorder=1)
#     plt.scatter(i - 0.1, row['max_norm'], color=light_blue, marker='_', zorder=1)
#     plt.scatter(i - 0.1, row['mean_norm'], color=light_blue, marker='.', zorder=1)
    
# plot min-mean-max data
for i, demand in enumerate(data):
    demand['min_norm'] = demand['minimum_result'] / demand['deterministic_result'] * 100
    demand['max_norm'] = demand['maximum_result'] / demand['deterministic_result'] * 100
    
    plt.plot([i - 0.1, i - 0.1], [demand['min_norm'], demand['max_norm']], color=light_green, zorder=1)
    plt.scatter(i - 0.1, demand['min_norm'], color=light_green, marker='_', zorder=1)
    plt.scatter(i - 0.1, demand['max_norm'], color=light_green, marker='_', zorder=1)
    
    # plot deterministic result
    plt.scatter(i, 100, color=gray, marker='o', zorder=2)
    
# # plot Min-Mean-Max data
# for i, row in min_mean_max_df.iterrows():
#     plt.plot([i + 0.15, i + 0.15], [row['min_norm'], row['max_norm']], color=light_green, zorder=1)
#     plt.scatter(i + 0.15, row['min_norm'], color=light_green, marker='_', zorder=1)
#     plt.scatter(i + 0.15, row['max_norm'], color=light_green, marker='_', zorder=1)

#     # plot original score
#     plt.scatter(i, row['original_score_norm'], color=gray, marker='o', zorder=2)

# ------------------- Legend -------------------

# manually add Monte Carlo legend entry
line_mc = Line2D([0], [0], color=light_blue, label='Monte Carlo')
line_mmm = Line2D([0], [0], color=light_green, label='Min-Max')
scores_scatter = Line2D([0], [0], color="w", markerfacecolor=gray, marker='o', label='Original Score')

# add labels and legend
plt.ylabel('Normalized Scores [%]')
plt.legend(handles=[line_mc, line_mmm, scores_scatter], loc='upper right')

#set y axis range to 0 to 500
plt.ylim(0, 300)
    
# set demand names as x-ticks
labels = [demand['name_plots'] for demand in data]
plt.xticks(range(len(plotting_data)), labels=labels, rotation=90, va='top')

# ------------------- Save and Show -------------------

plt.tight_layout()
plt.savefig(set_filename('uncertainty_propagation.png'), dpi=900)

plt.show()


# time tracking
end_time = time.time()

duration = end_time - start_time
duration_minutes = duration // 60
duration_seconds = duration % 60

tprint("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes".format(duration, duration_minutes, int(duration_seconds)))


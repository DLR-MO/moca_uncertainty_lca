import os
import pandas as pd
import numpy as np
import json
import pickle
from tqdm import tqdm

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from concurrent.futures import ThreadPoolExecutor, as_completed

from utils import *

import matplotlib.font_manager as fm
fm.fontManager.addfont('C://Users//hoel_m0//AppData//Local//Microsoft//Windows//Fonts//latin-modern-roman.mroman12-regular.otf')

def initialize_report(workbook, writer):

    # In line with the DLR template, the font is set
    workbook.formats[0].set_font_name('Frutiger 45 Light')

    # A shortcut for basic format types. Can be expended by adding a new key.
    formats_dict = {
        'title': {
            'font_size': 18,
            'bold': True,
            'font_color': '#7b7b84',
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': 'white',
            'bottom': 2,
        },
        'white': {
            'bg_color': 'white',
        },
        'white+blackbottom': {
            'bg_color': 'white',
            'bottom': 2,
        }
    }

    # Make the formats available for the workbook
    formats = {key: workbook.add_format(val)
               for key, val in formats_dict.items()}

    # Preparation of the worksheets. Each sheet will have the same header, with a title. 
    worksheets = ['FC', 'FH', 'ASK', 'Month', 'Year', 'Life']
    worksheet_titles = ['Monte Carlo Results per Flight Cycle',
                        'Monte Carlo Results per Flight Hour',
                        'Monte Carlo Results per Available Seat Kilometer', 
                        'Monte Carlo Results per Month', 
                        'Monte Carlo Results per Year', 
                        'Monte Carlo Results per Life']

    for i, worksheet in enumerate(worksheets):
        ws = workbook.add_worksheet(worksheet)  # adding the sheet
        ws.set_row(0, 47.25, formats['white+blackbottom'])  # first row height
        ws.set_row(1, 15, formats['white'])  # second and third
        ws.set_column(0, 0, 2)  # first col width
        ws.set_column(1, 2, 16)  # second col width
        ws.set_column(3, 10000, 13)

        # Adding the sheet name right next to the DLR logo
        ws.merge_range('J1:G1', worksheet_titles[i], formats['title'])

        # Adding the DLR logo to the top left corner
        dpath_logos = os.path.join(lyfe_config.getpath('General', 'abs_path_lyfe'),'airlyfe', 'otherstuff')
        ws.insert_image('A1', filename=os.path.join(dpath_logos, 'logos.png'), options={'x_scale': 0.88886},)

        # This actually adds the worksheet to the workbook
        writer.sheets[worksheet] = ws

    return workbook, writer

def create_plot(data, output_path, labels):
    
    # ------------------- Set up the plot -------------------

    # set the font to 'Frutiger 45 Light'
    plt.rcParams['font.family'] = 'Frutiger'
    plt.rcParams['font.weight'] = 'light'

    # custom define colours
    blue = '#00668d'
    light_blue = '#0099CE'
    green = '#73a237'
    light_green = '#9cc045'
    gray = '#686867'

    # set up the plot
    plt.figure(figsize=(10, 6))
    
    # normalize the data to the deterministic score
    # data = data.div(data['Deterministic Score'], axis=0)
    
    # Half Violin Plot
    plt.violinplot(data.T.values, positions=range(len(labels)), showextrema=False)
    
    # Box Plot
    flierprops = dict(marker='o', markerfacecolor=light_blue, markersize=3, markeredgecolor='none')
    whiskerprops = dict(color=light_blue)
    boxprops = dict(color=light_blue)
    medianprops = dict(color=light_blue)
    capsprops = dict(color=light_blue)

    plt.boxplot(data.T.values, positions=range(len(labels)),
                widths=0.19, whis=[5, 95], notch=False,
                flierprops=flierprops, boxprops=boxprops, medianprops=medianprops,
                whiskerprops=whiskerprops, capprops=capsprops)
    
    # plot the deterministic scores
    plt.scatter(range(len(labels)), data.iloc[:, 0], color=gray, zorder=10)

    # legend
    line_mc = Line2D([0], [0], color=light_blue, label='Monte Carlo Results')
    scores_scatter = Line2D([0], [0], color="w", markerfacecolor=gray, marker='o', label='Deterministic Score')
    plt.ylabel('LCA Score')
    plt.legend(handles=[line_mc, scores_scatter], loc='upper right')

    # plt.ylim(0, 300)
    plt.xticks(range(len(labels)), labels=labels, rotation=90, va='top')

    plt.tight_layout()   
    plt.savefig(output_path, dpi=900)
    plt.close()
    
def plot_convergence(parameter, filename_convergence, filename_results):
    # change the font to LM Roman 12
    plt.rcParams['font.family'] = 'Latin Modern Roman'
    # make the font size larger
    plt.rcParams.update({'font.size': 17})

    # custom define colours
    blue = '#00668d'
    light_blue = '#0099CE'
    green = '#73a237'
    light_green = '#9cc045'
    gray = '#686867'
    light_gray = '#b2b2b2'
    
    # calculate the final mean and std
    final_mean = np.mean(parameter)
    final_std = np.std(parameter)
    
    # ----- Convergence plot
    
    # plot the results of the Monte Carlo simulation
    plt.figure(figsize=(8,5))
    
    mean_values = np.array([np.mean(parameter[:i]) for i in range(1, len(parameter)+1)]) 
    std_values = np.array([np.std(parameter[:i]) for i in range(1, len(parameter)+1)])
    
    # Plot mean on the left y-axis
    fig, ax1 = plt.subplots(figsize=(8, 5))

    color = blue
    ax1.set_xlabel('Number of Iterations')
    ax1.set_ylabel('Mean Value [kg CO2-Eq]', color=color)
    ax1.plot(np.arange(1, len(parameter)+1), mean_values, label='Mean Value', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(y=final_mean, linestyle='--', label='Final Mean Value')

    # Create a second y-axis for the standard deviation
    ax2 = ax1.twinx()  
    color = green
    ax2.set_ylabel('Standard Deviation [kg CO2-Eq]', color=color)  
    ax2.plot(np.arange(1, len(parameter)+1), std_values, label='Standard Deviation', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.axhline(y=final_std, color=color, linestyle='--', label='Final Standard Deviation')

    # Add the title and layout adjustments
    fig.tight_layout()

    # Save the figure
    plt.savefig(set_filename(filename_convergence, folder='outputs'), dpi=900)
    
    # ----- Results plot
    
    # plot the results of the Monte Carlo simulation
    plt.figure(figsize=(8,5))
    
    # for the labels
    plt.scatter(np.arange(1, len(parameter)+1), parameter, color=gray, alpha=0.5, s=6, linewidth=0, label='Simulation Results')
    plt.axhline(y=final_mean, color=blue, linestyle='--', label='Mean Value', linewidth=2)
    
    # fill the area between the mean and the mean ± std along the whole width of the plot
    plt.fill_between(np.arange(1, len(parameter)+1), final_mean - final_std, final_mean + final_std, color=light_green, alpha=0.5, linewidth=0, label='Mean ± Standard Deviation')
    plt.scatter(np.arange(1, len(parameter)+1), parameter, color=gray, alpha=0.5, s=6, linewidth=0)
    plt.axhline(y=final_mean, color=blue, linestyle='--', linewidth=2)
    plt.xlabel('Number of Iterations')
    
    plt.ylabel('Climate Change Impact [kg CO2-Eq]')
    # plt.title(f'Results of Monte Carlo Simulation for {demand["name_plots"]}')
    
    # set the x axis to between 0 and 10,000
    plt.xlim(0, len(parameter) + 1)
    
    plt.legend()
    plt.tight_layout()
    plt.savefig(set_filename(filename_results, folder='outputs'), dpi=900)

    tprint(f"Successfully plotted the convergence of the LYFE Monte Carlo simulation.")

def process_file(file):
    try:
        if file.endswith("_eco.xlsx") and not file.startswith("D250-TF"):
            file_path = os.path.join(output_folder_path, file)

            # Read the entire Excel file into memory
            xls = pd.read_excel(file_path, sheet_name=0, header=None)

            # Extract the LCIA method
            lcia_method = xls.iloc[10, 1].replace("'", "")
            if lcia_method != "EF v3.0 no LT":
                raise ValueError(f"The Monte Carlo LCA postprocessing is currently only implemented for the following LCIA methods: <EF v3.0 no LT>\nYou are using: {lcia_method} in {file}")

            # Extract relevant data
            df = xls.iloc[31:47, 1:9]  # B:I columns
            # set the first row as the column names
            df.columns = xls.iloc[30, 1:9].tolist()
            #
            cc_life = xls.iloc[37, 8]  # row 38, column I (zero-indexed)

            return df, cc_life  # Return processed data

    except Exception as e:
        return None, None  # Return None if there's an issue with the file


# find the correct project output folder
lyfe_config, airlyfe_config = read_config()
dpath_project = os.path.realpath(os.path.join(
        os.path.realpath(os.path.dirname(os.path.dirname(__file__))), 'projects', lyfe_config.get('General', 'projectName')
    ))
output_folder_path = os.path.realpath(os.path.join(dpath_project, 'outputs'))

# List to hold all DataFrames
input_data = []
i = 0

cc_life_list = []


# List of files in the output folder
files = [file for file in os.listdir(output_folder_path) if file.endswith("_eco.xlsx") and not file.startswith("D250-TF")]

num_workers = min(60, os.cpu_count())

# Create a thread pool and process files in parallel
with ThreadPoolExecutor(max_workers=num_workers) as executor:  # Adjust max_workers based on your system's capabilities
    futures = {executor.submit(process_file, file): file for file in files}
    
    # Collect results as they complete
    for future in tqdm(as_completed(futures), total=len(futures)):
        df, cc_life = future.result()
        
        if df is not None and cc_life is not None:
            input_data.append(df)
            cc_life_list.append(cc_life)

# dump the cc_life_list to a json file
with open(set_filename("cc_life_list.json"), 'w') as f:
    # transform cc_life_list to a list of floats
    cc_life_list = [float(i) for i in cc_life_list]
    
    json.dump(cc_life_list, f)
    
with open(set_filename("lyfe_mc_results.pkl"), 'wb') as f:
    pickle.dump(input_data, f)
        
tprint(f"Successfully read the data from {len(files)} files in the folder {output_folder_path}")

    
    
plot_convergence(cc_life_list, "cc_life_convergence.png", "cc_life_results.png")

# filter any values that deviate by more than 5 standard deviation from the mean from cc_life_list
values = np.array(cc_life_list)
mean = np.mean(cc_life_list)
std = np.std(cc_life_list)

cc_life_list = values[(values >= 0) & (values <= (mean + 5 * std))]

plot_convergence(cc_life_list, "cc_life_convergence_filtered5.png", "cc_life_results_filtered5.png")

cc_life_list = values[(values >= 0) & (values <= (mean + 4 * std))]

plot_convergence(cc_life_list, "cc_life_convergence_filtered4.png", "cc_life_results_filtered4.png")

cc_life_list = values[(values >= 0) & (values <= (mean + 3 * std))]

plot_convergence(cc_life_list, "cc_life_convergence_filtered3.png", "cc_life_results_filtered3.png")

        
# read the deterministic scores from referencecase_eco.xlsx
referencecase_path = os.path.join(output_folder_path, "D250-TF_eco.xlsx")
referencecase_df = pd.read_excel(referencecase_path, usecols="B:I", skiprows=30, nrows=16)

# Set functional units (more descriptive names could be helpful)
fu_indices = {
    'FC': 2,
    'FH': 3,
    'ASK': 4,
    'Month': 5,
    'Year': 6,
    'Life': 7
}

# Initialize DataFrame to store results
results = {fu: pd.DataFrame(columns=['Deterministic Score', 'Mean', 'Std', 'Median', '5th Percentile', '95th Percentile']) for fu in fu_indices}

# Extract the first column (row names)
row_names = input_data[0].iloc[:, 0]  # Assumes the first column is common across all input_data

# Calculate statistics
for fu_name, fu_index in fu_indices.items():
    for i in range(input_data[0].shape[0]):
        values = np.array([df.iloc[i, fu_index] for df in input_data])
        
        # Using pandas' methods to calculate the required statistics
        results[fu_name].loc[i] = {
            'Deterministic Score': referencecase_df.iloc[i, fu_index],
            'Mean': np.mean(values),
            'Std': np.std(values),
            'Median': np.median(values),
            '5th Percentile': np.percentile(values, 5),
            '95th Percentile': np.percentile(values, 95)
        }

    # Add the row names as the first column
    results[fu_name].insert(0, 'Impact Category', row_names)

# set filename for the output file
output_file = os.path.join(output_folder_path, "mc_postprocessing.xlsx")

# initialize the writer and workbook
writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
workbook = writer.book
workbook, writer = initialize_report(workbook, writer)

# write the data into the Excel file
with writer as writer:
    for fu_name, df in results.items():
        df.to_excel(writer, sheet_name=fu_name, startcol=1, startrow=3, index=False)
                
        # Generate the plot
        plot_path = os.path.join(output_folder_path, f"{fu_name}_plot.png")
        labels = df['Impact Category'].tolist()  # use the impact category names as labels
        create_plot(df.iloc[:, 1:], plot_path, labels)  # Exclude the 'Impact Category' column for the plot

        worksheet = writer.sheets[fu_name]
        worksheet.insert_image('J4', plot_path, {'x_scale': 0.85, 'y_scale': 1})

tprint(f"Results have been written to {output_file}")




from brightway2 import *
import time
import numpy as np
import pandas as pd
from utils import *


def recursively_call_exchanges(activity, demand, mode):
       
    # loop through each exchange in the activity's technosphere
    for exchange in activity.technosphere():
        
        # call the function that performs the LSA
        change_exchange_value(exchange, demand, mode)
        
        # recursively call the function for the next exchange
        if exchange.input['database'] != "ecoinvent_3.9.1_cutoff":
            recursively_call_exchanges(exchange.input, demand, mode)

def change_exchange_value(exchange, demand, mode):
    
    exchange_info = {
        'demand': demand['name'],
        'from': exchange.input,
        'to': exchange.output,
        'amount_deterministic': exchange['amount'],
    }
    
    # set the minimum and maximum values for the exchange amount depending on the uncertainty type in the database
    
    # undefined or no uncertainty
    if not exchange.uncertainty or exchange.uncertainty['uncertainty type'] == 0 or exchange.uncertainty['uncertainty type'] == 1:
        exchange_info['uncertainty_type'] = 'undefined'
        
        # if no uncertainty info is in the exchange, assume the scale for a Pedigree Matrix (5,5,5,5,5)
        scale = 0.5952127450215152
        
        # calculate the standard deviation (of the lognormal distribution) from the scale (= std of underlying normal distribution)
        std_lognormal = exchange_info['amount_deterministic'] * np.sqrt(np.exp(scale**2) - 1)
        
        # calculate the boundaries of the 95% interpercentile range via the 2 sigma rule
        minimum_value = max(0, exchange_info['amount_deterministic'] - 2 * std_lognormal)
        maximum_value = exchange_info['amount_deterministic'] + 2 * std_lognormal
          
    # lognormal
    elif exchange.uncertainty['uncertainty type'] == 2:
        exchange_info['uncertainty_type'] = 'lognormal'
        
        scale = exchange.uncertainty['scale']
        
        # calculate the standard deviation (of the lognormal distribution) from the scale (= std of underlying normal distribution)
        std_lognormal = exchange_info['amount_deterministic'] * np.sqrt(np.exp(scale**2) - 1)
        
        # calculate the boundaries of the 95% interpercentile range via the 2 sigma rule
        minimum_value = max(0, exchange_info['amount_deterministic'] - 2 * std_lognormal)
        maximum_value = exchange_info['amount_deterministic'] + 2 * std_lognormal
        
    # normal    
    elif exchange.uncertainty['uncertainty type'] == 3:
        exchange_info['uncertainty_type'] = 'normal'
        
        minimum_value = max(0, exchange_info['amount_deterministic'] - exchange.uncertainty['scale'])
        maximum_value = exchange_info['amount_deterministic'] + exchange.uncertainty['scale']
    
    # uniform, triangular, discrete uniform
    elif exchange.uncertainty['uncertainty type'] == 4 or exchange.uncertainty['uncertainty type'] == 5 or exchange.uncertainty['uncertainty type'] == 7:
        exchange_info['uncertainty_type'] = exchange.uncertainty['uncertainty type']
        
        try:
            minimum_value = exchange.uncertainty['minimum']
        except:
            minimum_value = 0
        
        maximum_value = exchange.uncertainty['maximum']
        
    else:
        raise ValueError(f"The uncertainty type {exchange.uncertainty['uncertainty_type']} is not supported")
    
    # if the minimum value is zero, set it to a small value instead
    if minimum_value == 0:
        minimum_value = exchange_info['amount_deterministic'] * 0.01
        
    # save the minimum and maximum values in the exchange_info dictionary
    exchange_info['amount_minimum'] = minimum_value
    exchange_info['amount_maximum'] = maximum_value
    
    if mode == 'minimum':
        exchange['amount'] = minimum_value
        exchange.save()
        
        # appending should only be done once (done with the minimum setting since this occurs first)
        exchange_list.append(exchange_info)
    
    elif mode == 'maximum':
        exchange['amount'] = maximum_value
        exchange.save()      
          
    else:
        raise ValueError("The mode must be either 'minimum' or 'maximum'")     
    
    
def write_results(exchange_list, demand_list, filename_output):

    
    # Process exchange_list to create DataFrames for the Excel sheets
    sheet1_data = []
    sheet2_data = []
    sheet3_data = []
    sheet4_data = []
    
    for exchange_info in exchange_list:
        # For sheet 1
        sheet1_row = {
            'demand': exchange_info['demand'],
            'to': exchange_info['to']['name'],
            'from': exchange_info['from']['name'],
            'amount_det': exchange_info['amount_deterministic'],
            'uncertainty_type': exchange_info['uncertainty_type'],
            'amount_min': exchange_info['amount_minimum'],
            'amount_max': exchange_info['amount_maximum']
        }
        sheet1_data.append(sheet1_row)
    
    for demand in demand_list:
        # For sheet 2
        sheet2_row = {
            'demand': demand['name'],
            'database': demand['database'],
            'key': demand['key']
        }
        # Add the deterministic results
        for key, value in demand['lca_results_deterministic'].items():
            sheet2_row[key] = value
        sheet2_data.append(sheet2_row)
        
        # For sheet 3
        sheet3_row = { 
            'demand': demand['name'],
            'database': demand['database'],
            'key': demand['key']
        }
        # Add the minimum-values results
        for key, value in demand['lca_results_minima'].items():
            sheet3_row[key] = value
        sheet3_data.append(sheet3_row)
        
        # For sheet 4
        sheet4_row = {
            'demand': demand['name'],
            'database': demand['database'],
            'key': demand['key']
        }
        # Add the maximum-values results
        for key, value in demand['lca_results_maxima'].items():
            sheet4_row[key] = value
        sheet4_data.append(sheet4_row)
    
    # Create DataFrames
    df_sheet1 = pd.DataFrame(sheet1_data)
    df_sheet2 = pd.DataFrame(sheet2_data)
    df_sheet3 = pd.DataFrame(sheet3_data)
    df_sheet4 = pd.DataFrame(sheet4_data)

    
    # Write to Excel file with three sheets
    with pd.ExcelWriter(filename_output) as writer:
        df_sheet1.to_excel(writer, sheet_name='Exchanges', index=False)
        df_sheet2.to_excel(writer, sheet_name='Deterministic', index=False)
        df_sheet3.to_excel(writer, sheet_name='Minima', index=False)
        df_sheet4.to_excel(writer, sheet_name='Maxima', index=False)

    tprint(f"Excel file 'mmm_propagation.xlsx' has been created. Number of exchanges: {len(sheet1_data)}")

if __name__ == "__main__": 
    start_time = time.time()
    
    # set filenames
    # filename_input = set_filename('D250-TFLH2-MHEP_eco.xlsx')
    filename_input = set_filename('D250-TF_eco.xlsx')
    filename_output = set_filename('mmm_propagation.xlsx')
    filename_output_json = set_filename('sensitivity_analysis.json')
        
    # initialize the project and brightway infrastructure
    lyfe_config, airlyfe_config = read_config()
    brightway_project = airlyfe_config.get('LCA', 'brightway_projectname')
    projects.set_current(brightway_project)
    
    # setting up all required Brightway projects
       
    tprint("Creating a project duplicate for the deterministic LCAs")
    if 'mmm_propagation' in projects:
        projects.delete_project('mmm_propagation', delete_dir=True)
        projects.copy_project('mmm_propagation')
    else:
        projects.copy_project('mmm_propagation')
    
    tprint("Creating a project duplicate for the minimum-values LCAs")
    if 'mmm_propagation_minima' in projects:
        projects.delete_project('mmm_propagation_minima', delete_dir=True)
        projects.copy_project('mmm_propagation_minima')
    else:
        projects.copy_project('mmm_propagation_minima')
        
    tprint("Creating a project duplicate for the maximum-values LCAs")
    if 'mmm_propagation_maxima' in projects:
        projects.delete_project('mmm_propagation_maxima', delete_dir=True)
        projects.copy_project('mmm_propagation_maxima')
    else:
        projects.copy_project('mmm_propagation_maxima')
        
    projects.set_current('mmm_propagation')
    assert projects.current == 'mmm_propagation'
    
    bw2setup() 
    
    # read in the data from the output file
    input_data = pd.read_excel(filename_input, sheet_name='Individual LCAs', header=3, usecols='B:ZZZ')
      
    # transform the pandas dataframe into a list of dictionaries
    demand_list = [
        {
            'name': row['Name'],
            'key': row['Key'],
            'database': row['Database'],
            'lca_results_deterministic': {},
            'lca_results_minima': {},
            'lca_results_maxima': {}
        }
        for _, row in input_data.iterrows()
    ]
    
    # demand_list = []
    # demand = {
    #     'name': 'A-Check',
    #     'key': '6b833f545a364efbac180f95710d34c8',
    #     'database': 'maintenance_D250-TF',
    #     'lca_results_deterministic': {},
    #     'lca_results_minima': {},
    #     'lca_results_maxima': {}
    # }
    # demand_list.append(demand)
    
    # set the correct LCIA methods and their formatting
    lcia_method_name = airlyfe_config.get('LCA', 'lcia_method')
    lcia_methods = [method for method in methods if lcia_method_name in str(method)]
    lcia_methods = [method for method in lcia_methods if lcia_method_transl(lcia_method_name, str(method[1]))]
    
    # set the keys list according to the translated names
    key_list = []
    for method in lcia_methods:
        key_list.append(lcia_method_transl(lcia_method_name, str(method[1]))[-1])
    
    # initialise the exchange list to store the results
    exchange_list = []
        
    # perform the deterministic LCA
    for demand in demand_list:

        tprint(f"Performing the deterministic LCA for {demand['name']}")
        demand_activity = Database(demand['database']).get(demand['key'])
        
        lca = LCA({demand_activity: 1}, method=lcia_methods[0])
        lca.lci()
                    
        # loop through each LCIA method
        for i, method in enumerate(lcia_methods):
            lca.switch_method(method)
            lca.lcia()
            demand['lca_results_deterministic'][key_list[i]] = lca.score                
        
    
    # set the project to the minimum-values project
    projects.set_current('mmm_propagation_minima')
    assert projects.current == 'mmm_propagation_minima'
    
    # perform the minimum-values LCA
    for demand in demand_list:

        tprint(f"Performing the minimum-values LCA for {demand['name']}")
        demand_activity = Database(demand['database']).get(demand['key'])
        
        recursively_call_exchanges(demand_activity, demand, mode='minimum')    
        
        lca = LCA({demand_activity: 1}, method=lcia_methods[0])
        lca.lci()
                    
        # loop through each LCIA method
        for i, method in enumerate(lcia_methods):
            lca.switch_method(method)
            lca.lcia()
            demand['lca_results_minima'][key_list[i]] = lca.score
                
    # set the project to the maximum-values project
    projects.set_current('mmm_propagation_maxima')
    assert projects.current == 'mmm_propagation_maxima'
    
    # perform the maximum-values LCA
    for demand in demand_list:

        tprint(f"Performing the maximum-values LCA for {demand['name']}")
        demand_activity = Database(demand['database']).get(demand['key'])
        
        recursively_call_exchanges(demand_activity, demand, mode='maximum')
        
        lca = LCA({demand_activity: 1}, method=lcia_methods[0])
        lca.lci()
                    
        # loop through each LCIA method
        for i, method in enumerate(lcia_methods):
            lca.switch_method(method)
            lca.lcia()
            demand['lca_results_maxima'][key_list[i]] = lca.score
    
    write_results(exchange_list, demand_list, filename_output)
    
    projects.set_current(brightway_project)
    # delete the project duplicates
    try:
        projects.delete_project('mmm_propagation', delete_dir=True)
        projects.delete_project('mmm_propagation_minima', delete_dir=True)
        projects.delete_project('mmm_propagation_maxima', delete_dir=True)
        tprint("Project duplicates have been deleted")
    except:
        tprint("Error deleting the project duplicates, please do this manually")
    
    end_time = time.time()
    duration = end_time - start_time
    duration_minutes = duration // 60
    duration_seconds = duration % 60
    
    tprint("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes".format(duration, duration_minutes, int(duration_seconds)))

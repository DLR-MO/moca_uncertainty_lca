from brightway2 import *
import time
import numpy as np
import pandas as pd
from utils import *


def recursively_call_exchanges(activity, demand):
    """
    Recursively call the exchanges of an activity to perform the LSA.
    
    Parameters:
        activity: the activity for which the LSA is performed
        demand: the demand dictionary
        
    Returns:
        None
    """
    
    # return if the technosphere contains zero or just one exchange
    if len(activity.technosphere()) < 2:
        return
    
    # loop through each exchange in the activity's technosphere
    for exchange in activity.technosphere():
        
        # call the function that performs the LSA
        perform_lsa(exchange, demand)
        
        # recursively call the function for the next exchange
        if exchange.input['database'] != "ecoinvent_3.9.1_cutoff" and exchange.input['database'] != "materials":
            recursively_call_exchanges(exchange.input, demand)

def perform_lsa(exchange, demand):
    """
    Perform the local sensitivity analysis (LSA) for a given exchange.
    
    Parameters:
        exchange: the exchange for which the LSA is performed
        demand: the demand dictionary
        
    Returns:
        None
    """
    
    # create an identifier for the exchange
    exchange_identifier = {
        'demand': demand['name'],
        'to': exchange.output,
        'from': exchange.input,
    }
    
    # check whether an exchange with a matching identifier already exists
    if exchange_identifier in exchange_list:
        return
    
    # save the original amount
    original_amount = exchange['amount']
    
    # change the amount by 10%
    if exchange['amount'] != 0:
        exchange['amount'] = exchange['amount'] * 1.1
    else:
        exchange['amount'] = 0.1
    exchange.save()
    
    # calculate x_nominal and delta_x
    x_nominal = original_amount
    delta_x = exchange['amount'] - x_nominal
    
    if x_nominal == 0:
        x_nominal = 1
        delta_x = 0.1
    
    # initialise the LCA
    lca = LCA({demand_activity: 1}, method=lcia_methods[0])
    lca.lci()
    
    # dictionary to store LCA results
    lca_results = {}
    sensitivity = {}
    elasticity = {}
    
    # loop through each LCIA method and calculate the sensitivity and elasticity
    for i, method in enumerate(lcia_methods):
        lca.switch_method(method)
        lca.lcia()
        lca_results[key_list[i]] = lca.score
        
        # calculate y_nominal and delta_y
        y_nominal = demand['lca_results'][key_list[i]]
        delta_y = lca_results[key_list[i]] - y_nominal
        
        # calculate sensitivity and elasticity
        sensitivity[key_list[i]] = delta_y / delta_x
        elasticity[key_list[i]] = (x_nominal * delta_y) / (y_nominal * delta_x)
        
    # calculate the average sensitivity and elasticity
    avg_sensitivity = sum(sensitivity.values()) / len(sensitivity)
    avg_elasticity = sum(elasticity.values()) / len(elasticity)
    
    exchange_info = {
        'demand': demand['name'],
        'from': exchange.input,
        'to': exchange.output,
        'amount': original_amount,
        'avg_sensitivity': avg_sensitivity,
        'avg_elasticity': avg_elasticity,
        'sensitivity': sensitivity,
        'elasticity': elasticity
    }
    exchange_list.append(exchange_info)
    
    # reset the amount    
    exchange['amount'] = original_amount
    exchange.save()
    
def write_results(exchange_list, filename_output):
    """
    Write the results of the LSA to an Excel file with three sheets: Summary, Sensitivity, Elasticity.
    
    Parameters:
        exchange_list: the list of exchanges
        filename_output: the output filename
        
    Returns:
        None
    """
    
    # Process exchange_list to create DataFrames for the Excel sheets
    sheet1_data = []
    sheet2_data = []
    sheet3_data = []
    
    for exchange_info in exchange_list:
        # For sheet 1
        sheet1_row = {
            'demand': exchange_info['demand'],
            'to': exchange_info['to']['name'],
            'from': exchange_info['from']['name'],
            'amount': exchange_info['amount'],
            'average sensitivity': exchange_info['avg_sensitivity'],
            'average elasticity': exchange_info['avg_elasticity']
        }
        sheet1_data.append(sheet1_row)
        
        # For sheet 2
        sheet2_row = {
            'demand': exchange_info['demand'],
            'to': exchange_info['to']['name'],
            'from': exchange_info['from']['name'],
            'amount': exchange_info['amount']
        }
        # Add sensitivities
        for key, value in exchange_info['sensitivity'].items():
            sheet2_row[key] = value
        sheet2_data.append(sheet2_row)
        
        # For sheet 3
        sheet3_row = {
            'demand': exchange_info['demand'],
            'to': exchange_info['to']['name'],
            'from': exchange_info['from']['name'],
            'amount': exchange_info['amount']
        }
        # Add elasticities
        for key, value in exchange_info['elasticity'].items():
            sheet3_row[key] = value
        sheet3_data.append(sheet3_row)
    
    # Create DataFrames
    df_sheet1 = pd.DataFrame(sheet1_data)
    df_sheet2 = pd.DataFrame(sheet2_data)
    df_sheet3 = pd.DataFrame(sheet3_data)
    
    # Write to Excel file with three sheets
    with pd.ExcelWriter(filename_output) as writer:
        df_sheet1.to_excel(writer, sheet_name='Summary', index=False)
        df_sheet2.to_excel(writer, sheet_name='Sensitivity', index=False)
        df_sheet3.to_excel(writer, sheet_name='Elasticity', index=False)
    
    tprint(f"Excel file 'sensitivity_analysis.xlsx' has been created. Number of rows: {len(sheet1_data)}")

if __name__ == "__main__": 
    start_time = time.time()
    
    # set filenames
    # filename_input = set_filename('D250-TFLH2-MHEP_eco.xlsx')
    filename_input = set_filename('D250-TF_eco.xlsx')
    filename_output = set_filename('sensitivity_analysis.xlsx')
    filename_output_json = set_filename('sensitivity_analysis.json')
        
    # initialize the project and brightway infrastructure
    lyfe_config, airlyfe_config = read_config()
    brightway_project = airlyfe_config.get('LCA', 'brightway_projectname')
    projects.set_current(brightway_project)
    bw2setup() 
    
    # read in the data from the output file
    input_data = pd.read_excel(filename_input, sheet_name='Individual LCAs', header=3, usecols='B:ZZZ')
      
    # transform the pandas dataframe into a list of dictionaries
    demand_list = [
        {
            'name': row['Name'],
            'key': row['Key'],
            'database': row['Database'],
            'lca_results': {k: v for k, v in row.iloc[4:].items() if not pd.isna(v)}
        }
        for _, row in input_data.iterrows()
    ]
    
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
    
    for demand in demand_list:


        tprint(f"Performing LSA for {demand['name']}")
        
        demand_activity = Database(demand['database']).get(demand['key'])
        
        lca = LCA({demand_activity: 1}, method=lcia_methods[0])
        lca.lci()
                    
        # loop through each LCIA method
        for i, method in enumerate(lcia_methods):
            lca.switch_method(method)
            lca.lcia()
            demand['lca_results'][key_list[i]] = lca.score
                
        recursively_call_exchanges(demand_activity, demand)
        write_results(exchange_list, filename_output)
    
    write_results(exchange_list, filename_output)
    
    end_time = time.time()
    duration = end_time - start_time
    duration_minutes = duration // 60
    duration_seconds = duration % 60
    
    tprint("Time elapsed: {:.2f} seconds = {:.0f}:{:02} minutes".format(duration, duration_minutes, int(duration_seconds)))

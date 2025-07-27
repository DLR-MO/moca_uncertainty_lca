import json
import csv

def extract_sensitivity_analysis(data):
    # List to hold the rows for the CSV file
    rows = []

    # Iterate through the list of parent entries (Aircraft in this case)
    for entry in data:
        parent_name = entry["name"]
        parent_score = entry["score_baseline"]
        
        # Iterate through the sensitivity analysis entries
        for sa_entry in entry.get("sensitivity_analysis", []):
            row = {
                "parent_name": parent_name,
                "parent_score": parent_score,
                "sensitivity_param": sa_entry["name"],
                "original_amount": sa_entry["original_amount"],
                "changed_amount": sa_entry["changed_amount"],
                "changed_score": sa_entry["changed_score"],
                "sensitivity": sa_entry["sensitivity"]
            }
            rows.append(row)
    
    return rows

filename_input = "C:/Git_LYFE/airlyfe/projects/ecoLYFE/outputs/referencecase_sensitivity_analysis.json"
filename_output = "C:/Git_LYFE/airlyfe/projects/ecoLYFE/outputs/referencecase_sensitivity_analysis.csv"

with open(filename_input) as json_file:
    data = json.load(json_file)
    
rows = extract_sensitivity_analysis(data)

# Write to a CSV file
with open(filename_output, 'w', newline='') as csv_file:
    fieldnames = ["parent_name", "parent_score", "sensitivity_param", "original_amount", "changed_amount", "changed_score", "sensitivity"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    # Manually write the header for nicer formatting
    writer.writerow({
        "parent_name": "LCA Demand",
        "parent_score": "Original Score",
        "sensitivity_param": "Sensitivity Parameter",
        "original_amount": "Original Amount",
        "changed_amount": "Changed Amount",
        "changed_score": "Changed Score",
        "sensitivity": "Sensitivity"
    })
    
    # writer.writeheader()
    writer.writerows(rows)
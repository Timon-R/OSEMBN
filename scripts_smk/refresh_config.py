'''
This python script refreshes the config file for the gsa snakemake pipeline.
It is not used in the workflow but manually before running the workflow.
Author: Timon Renzelmann
'''
import pandas as pd
import csv

def excel_to_csv(excel_file):
    # Load the Excel file
    xls = pd.ExcelFile(excel_file)

    # For each sheet in the Excel file
    for sheet_name in xls.sheet_names:
        # Read the sheet into a pandas DataFrame
        df = xls.parse(sheet_name)
        # Write the DataFrame to a CSV file
        csv_file = f"config/{sheet_name}.csv"
        df.to_csv(csv_file, index=False)

        # If the sheet is 'results', add brackets to the specified columns
        if sheet_name == 'results':
            df = pd.read_csv(csv_file)
            for col in ['REGION', 'TECHNOLOGY', 'FUEL', 'EMISSION']:
                if col in df.columns:
                    df.loc[df[col].notna(), col] = '"' + df.loc[df[col].notna(), col].astype(str) + '"'
            df.to_csv(csv_file, index=False, quoting=csv.QUOTE_NONE)

# Usage
if __name__ == "__main__":
    excel_to_csv('GSA_configuration.xlsx')
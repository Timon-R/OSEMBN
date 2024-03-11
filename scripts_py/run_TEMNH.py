'''
This is a python script that runs the model without the use of snakemake.

@author: Timon Renzelmann
'''

import otoole
import subprocess
import sys
import py_scripts.visualiser as visualiser
import os
import pandas as pd

input_folder = 'input_data\\Nordic_test\\data'
results_folder = 'results\\WP1_NetZero_test'

pre_process = ["python", "pre_process_py.py"]
run_osemosys1 = [ #convert model into lp file
    'glpsol',
    '-m',
    'model\\osemosys.txt',
    '-d',
    'nordic.txt',
    '--wlp',
    'nordic.lp',
    '--check'
]
run_osemosys2 = [ # run the model
    'gurobi_cl',
    'ResultFile=nordic.sol',
    'nordic.lp'
]

visualize = [
    'otoole',
    'viz',
    'res',
    'csv',
    input_folder, #input files
    'visualisations\\res.png',
    'config\\otoole.yaml'
]

visualize2 = [
    'otoole',
    'viz',
    'res',
    'csv',
    'input_data\\WP1_NetZero\\input_data_decoded', #input files
    'visualisations\\res_decoded.png',
    'config\\otoole.yaml'
]

def create_net_charge_per_year_csv(folder_with_results):
    # Load the two existing CSV files
    df_start = pd.read_csv(os.path.join(folder_with_results, 'StorageLevelYearStart.csv'))
    df_finish = pd.read_csv(os.path.join(folder_with_results, 'StorageLevelYearFinish.csv'))

    # Merge the two DataFrames
    df = pd.merge(df_finish, df_start, on=['REGION', 'STORAGE', 'YEAR'], how='outer', suffixes=('_finish','_start'))

    # Fill any missing 'VALUE' entries with 0
    df[['VALUE_start', 'VALUE_finish']] = df[['VALUE_start', 'VALUE_finish']].fillna(0)

    # Create a new column 'VALUE' that is the difference between the 'VALUE' columns
    df['VALUE'] = df['VALUE_finish'] - df['VALUE_start']

    # Drop the original 'VALUE' columns
    df.drop(columns=['VALUE_start', 'VALUE_finish'], inplace=True)

    # Save the resulting DataFrame to a new CSV file
    df.to_csv(os.path.join(folder_with_results, 'StorageNetCharge.csv'), index=False)


#create_net_charge_per_year_csv(results_folder)

try:
    otoole.convert('config\\otoole.yaml', 'csv', 'datafile', input_folder, 'nordic_pre.txt')
    print('File conversion is done')

    subprocess.run(pre_process)  # preprocessing the model
    print('Pre-processing is done')

    subprocess.run(run_osemosys1, check=True)  # convert model into lp file
    print('conversion into lp file is done')

    subprocess.run(run_osemosys2, check=True)  # solve the model with gurobi
    print('Running of the model is done')

    otoole.convert_results('config\\otoole.yaml', 'gurobi', 'csv', 'nordic.sol', results_folder, 'csv', input_folder)

    create_net_charge_per_year_csv(results_folder) #add rule to check whether storage exists

    #visualiser.run()  # visualisation of results
    #print('Visualisation is done')

except subprocess.CalledProcessError as e:
    print(f"Error: {e}")
    sys.exit()

# try: #visualisation of res
#     subprocess.run(visualize, check=True)
#     print('Generation of visualisation is done')
# except subprocess.CalledProcessError as e4: # Handle errors
#     print(f"Error: {e4}")
#     sys.exit()

# try: #visualisation of res_decoded
#     subprocess.run(visualize2, check=True)
#     print('Generation of visualisation2 is done')
# except subprocess.CalledProcessError as e4: # Handle errors
#     print(f"Error: {e4}")
#     sys.exit()


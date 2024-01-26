'''
This is a python script that runs the model without the use of snakemake.
'''

import otoole
import subprocess
import sys
#import visualiser
import os
import pandas as pd


#ADD new folder that is called like the scenario in the results folder and put the results there

#define commands

input_folder = 'input_data\\Nordic\\data'
results_folder = 'results\\Nordic'


pre_process = ["python", "scripts_py\\pre_process.py", 'otoole', 'nordic_pre.txt', 'nordic.txt']
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


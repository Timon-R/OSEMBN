'''
To use this workflow, activate one of the all functions depending on whether you like to run scenarios or a GSA.
Make sure that the right scripts are included.
'''

import os
import pandas as pd
import sys
from typing import List 
from yaml import load
from otoole.utils import UniqueKeyLoader

#need to be run with: snakemake --cores all --use-conda
#other flags: --rerun-incomplete --forceall -n


###for single baseline run 
baseline_dp_files = pd.read_csv('config/dp_files.txt')
BASELINE = ['Nordic','Nordic_no_h2','Nordic_co2_limit','Nordic_em_free', 'Nordic_co2_tax']
#BASELINE = ['Nordic_no_h2']
###

configfile: "config/config.yaml"
localrules: all#, clean # always executed
wildcard_constraints:
    result_file=r"[^(objective)][a-zA-Z_\-]+", # exclude strings that start with "objective" and contains letters or hyphens or underscores
    scenario=r"\d+", # has to be at least one digit
    model_run=r"\d+"

# container: "docker://condaforge/mambaforge:4.10.1-0" # use mambaforge to speed up conda env creation

SCENARIOS = pd.read_csv(config["scenarios"]).set_index('name')
GROUPS = pd.read_csv(config['parameters'])['group'].unique()

# Calculates number of model runs for the Method of Morris
MODELRUNS = range((len(GROUPS) + 1) * config['replicates']) # replicates * number of groups in parameters + 1
RESULTS = pd.read_csv(config["results"]) # results file from config/config.yaml which is config/results.csv
RESULT_FILES = RESULTS['filename'].to_list()
ZIP = '.gz' if config['zip'] else ''

# Get list of expected input/output files from otoole config.

# While these are only tied to a single scenario, since the user only supplies
# one model file, the params and variables can not change between scenarios
def get_expected_files(config: str, config_type: str) -> List[str]:
    if config_type not in ["param", "result", "set"]:
        return TypeError(f"Type must be 'param', 'result', or 'set'. Recieved {config_type}.")
    with open(config, "r") as f:
        parsed_config = load(f, Loader=UniqueKeyLoader)
    return [x for x, y in parsed_config.items() if y["type"] == config_type]

# may get type error if just extracting paper data 
if "skip_checks" in config:
    otoole_config_path = "config/otoole.yaml"
else:
    first_scenario_name = SCENARIOS.index[0]
    otoole_config_path = SCENARIOS.loc[first_scenario_name, "config"]
    
#input and output files equal to the parameters and results in the otoole config, which are the input and output csv files
INPUT_FILES_PARAMS = get_expected_files(otoole_config_path, "param")
INPUT_FILES_SETS = get_expected_files(otoole_config_path, "set")
INPUT_FILES = INPUT_FILES_PARAMS + INPUT_FILES_SETS

OUTPUT_FILES = get_expected_files(otoole_config_path, "result")
files_to_remove = [ #this way, those files are being calculated but not expected as output - alternatively, I could make sure they are being calculated
    #"NewStorageCapacity", 
    "NumberOfNewTechnologyUnits", 
    #"SalvageValueStorage", 
    #"StorageLevelDayTypeFinish", 
    #"StorageLevelDayTypeStart", 
    #"StorageLevelSeasonStart", 
    #"StorageLevelYearFinish", 
    #"StorageLevelYearStart", 
    "Trade"
]
OUTPUT_FILES = [x for x in OUTPUT_FILES if x not in files_to_remove]
OUTPUT_FILES = OUTPUT_FILES 

#comment out so it doesn't rerun the model every time
include: "scripts_smk/sample.smk"
include: "scripts_smk/osemosys.smk"
include: "scripts_smk/results.smk"

# for running the model with the baseline scenario
include: 'scripts_smk/run.smk'

# needed for running examples via jupyter notebook 
args = sys.argv

try:
    config_path = args[args.index("--configfile") + 1]
except ValueError:
    config_path = 'config/config.yaml'
    
onstart: #executed once at the start of the workflow , don't understand the checking of the user inputs yet
    if "skip_checks" not in config:
        print('Checking user inputs...')
        shell("python scripts_smk/gsa/check_inputs.py {}".format(config_path))

onsuccess: #executed once at the end of the workflow
    print('Workflow finished successfully!')

# rule all: #for GSA
#     input:
#         expand("results/{scenario}_summary/SA_objective.{extension}", scenario=SCENARIOS.index, extension=['csv', 'png']),
#         expand("results/{scenario}_summary/SA_{result_file}.{extension}", scenario=SCENARIOS.index, extension=['csv', 'png'], result_file=RESULT_FILES),
#         ### expand("results/{scenario}_summary/SA_interactions.png", scenario=SCENARIOS.index),
#         expand("results/{scenario}/model_{model_run}/results/{x}.csv", x=OUTPUT_FILES, model_run=MODELRUNS, scenario=SCENARIOS.index), #all the result folders
#         expand("results/{scenario}/objective_{scenario}.csv", scenario=SCENARIOS.index), #all the objective folders
#         expand("results/{scenario}_summary/{result_file}_heatmap.png", scenario=SCENARIOS.index, result_file=RESULT_FILES)            
#     message: "Running pipeline to generate the sensitivity analysis results"


#for the baseline run
rule all:
    input:        
        expand("results/{scen}/res-csv_done.txt", scen = BASELINE)
        #expand("visualisations/{scen}/res.graphml", scen = BASELINE) #for the graphml files of the reference energy system
        
# rule update_config: #better do manually
#     input:
#         "GSA_configuration.xlsx"
#     output:
#         "config/parameters.csv",
#         "config/results.csv"
#     script:
#         "scripts_smk/refresh_config.py"

rule clean:
    shell:
        "rm -rf results/* && rm -rf results/* && rm -rf modelruns/* && rm -rf temp/* "

rule clean_plots:
    shell:
        "rm -f results/{modelrun}/*.pdf"

rule plot:
    input: "results/{modelrun}/{result}.csv"
    output: "results/{modelrun}/{result}.pdf"
    conda: "envs/plot.yaml"
    message: "Generating plot using '{input}' and writing to '{output}'"
    shell:
        "python scripts_smk/gsa/plot_results.py {input} {output}"

rule make_dag:
    output: pipe("dag.txt")
    shell:
        "snakemake --dag > {output}"

rule plot_dag:
    input: "dag.txt"
    output: "dag.png"
    conda: "envs/graphviz_env.yaml"
    shell:
        "dot -Tpng {input} > dag.png && xdg-open dag.png"
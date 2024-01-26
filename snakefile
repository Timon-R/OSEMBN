import os
import pandas as pd
import sys
from typing import List 
from yaml import load
from otoole.utils import UniqueKeyLoader

#need to be run with snakemake --cores all --use-conda
#add --rerun-incomplete() when workflow broke
#add --forceall to force rerun all rules


###for single baseline run 
baseline_dp_files = pd.read_csv('config/dp_files.txt')
SCENARIOS = ['Nordic']
###

include: 'scripts_smk/run.smk'

onsuccess: #executed once at the end of the workflow
    print('Workflow finished successfully!')

rule all: #final output files
    input:        
        expand("results/{scen}/res-csv_done.txt", scen = BASELINE)
        #,expand("visualisations/{scen}/res.graphml", scen = BASELINE) # for reference energy system


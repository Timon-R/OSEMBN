"""Generates a sample from a list of parameters

Arguments
---------
replicates : int
    The number of model runs to generate
path_to_parameters : str
    File containing the parameters to generate a sample for

Usage
-----
To run the script on the command line, type::

    python create_sample.py 10 path/to/parameters.csv

The ``parameters.csv`` CSV input file should be formatted as follows::

    name,group,indexes,min_value_base_year,max_value_base_year,min_value_end_year,max_value_end_year,dist,interpolation_index,action
    DiscountRate,discountrate,"REGION",0.05,0.15,0.05,0.15,unif,None,fixed
    CapitalCost,CapitalCost,"REGION,HYD1",2100,3100,742,1800,unif,YEAR,interpolate

The output sample file is formatted as follows::

    name,indexes,value_base_year,value_end_year,action,interpolation_index
    DiscountRate,"REGION",0.05,0.05,fixed,None
    CapitalCost,"REGION,HYD1",2100,742,interpolate,YEAR

"""
import os
import csv
import numpy as np
from typing import List
import sys
import math
import logging
from logging import getLogger

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    handlers=[logging.StreamHandler(sys.stdout)]  # Write logs to stdout
)
logger = getLogger(__name__)

def assign_sample_value(min_value, max_value, sample):
    values = [min_value, max_value]
    points = [0, 1]
    return np.interp(sample, points, values)

def main(morris_sample, parameters, output_files):
    try:
        for model_run, sample_row in enumerate(morris_sample):           
            filepath = output_files[model_run]            
            with open(filepath, 'w') as csvfile:

                fieldnames = ['name', 'indexes', 'value_base_year', 'value_end_year', 'action', 'interpolation_index']
                writer = csv.DictWriter(csvfile, fieldnames)
                writer.writeheader()

                for column, param in zip(sample_row, parameters):

                    try:
                        min_by = float(param['min_value_base_year'])
                        max_by = float(param['max_value_base_year'])
                        min_ey = float(param['min_value_end_year'])
                        max_ey = float(param['max_value_end_year'])
                    except ValueError as ex:
                        print(param)
                        raise ValueError(str(ex))

                    # check for a fixed endpoints
                    if math.isclose(min_by, max_by):
                        value_base_year = min_by
                    else:
                        value_base_year = (max_by - min_by) * column + min_by

                    if math.isclose(min_ey, max_ey):
                        value_end_year = min_ey
                    else:
                        value_end_year =  (max_ey - min_ey) * column + min_ey
                        
                    # check for datatype on interpolation index
                    # ie. Solves issues further down the workflow 
                    if param['interpolation_index']:
                        if param['interpolation_index'] in ['None', 'none', '']:
                            interpolation_index = None
                        else:
                            interpolation_index = param['interpolation_index']
                    else:
                        interpolation_index = None

                    data = {'name': param['name'],
                            'indexes': param['indexes'],
                            'value_base_year': value_base_year,
                            'value_end_year': value_end_year,
                            'action': param['action'],
                            'interpolation_index': interpolation_index}
                    writer.writerow(data)
                    #logger.info(data)
        #logger.info("The sample has been written to {}".format(filepath))
    except Exception as ex:
        logger.error("An error occurred: %s", str(ex))
        logger.info("The sample has not been written to {}".format(filepath))
        raise ex

if __name__ == "__main__":
# {input} {params.parameters} {output} > {log} 2>&1
  
    sample_file = snakemake.input[0]
    parameters_file = snakemake.params[0]
    output_files = snakemake.output[0:]
    print(output_files)
    with open(parameters_file, 'r') as csv_file:
        parameter_list = list(csv.DictReader(csv_file))
    morris_sample = np.loadtxt(sample_file, delimiter=",")
    main(morris_sample, parameter_list, output_files)

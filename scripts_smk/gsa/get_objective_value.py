import sys
import pandas as pd

def get_objective_value_gurobi(input_files, output_file):
    # Initialize a list to store the data
    data = []

    # Loop over the input files
    for input_file in input_files:
        # Extract the model run from the input file path
        model_run = input_file.split('/')[-1].split('.')[0]

        # Read the input file and extract the objective value and status
        with open(input_file, 'r') as f:
            lines = f.readlines()
            objective_value = lines[0].split('=')[1].strip()
            status = 'Solved with gurobi'  
            # Append the data to the list
            data.append([model_run, objective_value, status])

    # Convert the list to a DataFrame
    df = pd.DataFrame(data, columns=['JOB', 'OBJECTIVE', 'STATUS'])

    # Write the DataFrame to the output file
    df.to_csv(output_file, index=False)

if __name__ == '__main__':

    # Get the command-line arguments
    
    input_files = snakemake.input[0:]
    output_file = snakemake.output[0]

    # Call the function
    get_objective_value_gurobi(input_files, output_file)

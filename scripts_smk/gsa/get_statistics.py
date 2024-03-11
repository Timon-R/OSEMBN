import os
import sys
import logging

def get_statistics(input_file, output_file):
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        # Read the second line of the input file and write it to the output file
        with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
            next(f_in)  # Skip the first line
            second_line = next(f_in)  # Read the second line
            f_out.write(second_line)
            logging.info(f'Wrote second line of {input_file} to {output_file}')
    
    except Exception as e:
        logging.error(f'Error occurred while processing files {input_file} and {output_file}: {str(e)}')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    get_statistics(input_file, output_file)

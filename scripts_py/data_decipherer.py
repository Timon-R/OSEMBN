'''
This script uses the code decipherer to decode the codes in the csv files of the input data.
It also converts the csv files to an excel file if desired.
Author: Timon Renzelmann
'''

import os
import pandas as pd
from code_decipherer import decode_code
from otoole import convert

# Define paths to original and new result folders
original_folder = "input_data\\Nordic\\data"
new_folder = "input_data\\Nordic_decoded"

# Create new folder if it doesn't exist
if not os.path.exists(new_folder):
    os.makedirs(new_folder)

# Loop through each csv file in new folder
for file_name in os.listdir(original_folder):
    if file_name.endswith(".csv"):
        # Read csv file into pandas dataframe
        file_path = os.path.join(original_folder, file_name)
        df = pd.read_csv(file_path)
        
        if file_name == "TECHNOLOGY.csv" or file_name == "FUEL.csv":
        # Decode codes in "value" column
            df["VALUE"] = df["VALUE"] + " | " + df["VALUE"].apply(decode_code)

        if file_name == "EMISSION.csv":
        # Decode codes in "value" column
            df["VALUE"] = df["VALUE"] + " | " + df["VALUE"].apply(decode_code, args=(None, True,))

        if "FUEL" in df.columns:
            # Decode codes in "FUEL" column
            df["FUEL"] = df["FUEL"].apply(decode_code)
        
        # Check if "TECHNOLOGY" column exists in dataframe
        if "TECHNOLOGY" in df.columns:
            # Decode codes in "TECHNOLOGY" column
            df["TECHNOLOGY"] = df["TECHNOLOGY"].apply(decode_code)

        if "EMISSION" in df.columns:
            # Decode codes in "TECHNOLOGY" column
            df["EMISSION"] = df["EMISSION"].apply(decode_code, args=(None, True,))
        
        # Write updated dataframe to new csv file
        updated_file_path = os.path.join(new_folder, file_name)
        df.to_csv(updated_file_path, index=False)

# Convert csv files to excel file
convert('config\\otoole.yaml', 'csv', 'excel', original_folder, original_folder + '\\input_data.xlsx')
convert('config\\config.yaml', 'csv', 'excel', new_folder, new_folder + '\\input_data_decoded.xlsx')
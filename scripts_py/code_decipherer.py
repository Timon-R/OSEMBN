"""
Script: Code Decoder and CSV Modifier

Description:
This Python script decodes technology and fuel codes.
The main function creates a new or updates a CSV file with appended decoded descriptions in a new column.

Functions:
1. decode_code(code, specifier=None): Decodes an OSeMBE Fuel Technology or Emission code. The specifier can be 'country', 'commodity', 'technology', 'energy_level', 'age', 'size' to only return that information about the code.
2. add_code_descriptions_to_csv(input_csv_filename, output_csv_filename=None): creates a new csv file including a new column with code descriptions.

It can also be used from the command line to decode a single code or to modify a CSV file.

Example Usage:
input_csv_filename = 'input_data\\WP1_NetZero\\data\\FUEL.csv'
output_csv_filename = 'output_codes_fuel.csv'
add_code_descriptions_to_csv(input_csv_filename, output_csv_filename)

Author: Timon Renzelmann
"""

import sys
import pandas as pd
import os

# Define code mappings
country_codes = {
    'AT': 'Austria',
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'CH': 'Switzerland',
    'CY': 'Cyprus',
    'CZ': 'Czech Republic',
    'DE': 'Germany',
    'DK': 'Denmark',
    'EE': 'Estonia',
    'ES': 'Spain',
    'FI': 'Finland',
    'FR': 'France',
    'GR': 'Greece',
    'HR': 'Croatia',
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IT': 'Italy',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'LV': 'Latvia',
    'MT': 'Malta',
    'NL': 'The Netherlands',
    'NO': 'Norway',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'SE': 'Sweden',
    'SI': 'Slovenia',
    'SK': 'Slovakia',
    'UK': 'United Kingdom'
}


commodity_codes = { # can also be an emission
    'BF': 'Biofuel',
    'BM': 'Biomass',
    'CO': 'Coal',
    'EL': 'Electricity',
    'E1': 'Electricity 1',
    'E2': 'Electricity 2',
    'GO': 'Geothermal',
    'HF': 'Heavy fuel oil',
    'HY': 'Hydro',
    'NG': 'Natural gas',
    'NU': 'Nuclear',
    'OC': 'Ocean',
    'OI': 'Oil',
    'OS': 'Oil Shale',
    'SO': 'Sun',
    'UR': 'Uranium',
    'WS': 'Waste',
    'WI': 'Wind',
    'H1': 'Hydrogen 1',
    'H2': 'Hydrogen 2'
}

technology_codes = {
    'CC': 'Combined cycle',
    'CH': 'Combined heat and power',
    'CS': 'Carbon Capture and Storage',
    'CV': 'Conventional',
    'DI': 'Distributed PV',
    'DM': 'Dam',
    'DS': 'Pumped Storage',
    'FC': 'Fuel cell',
    'GC': 'Gas cycle',
    'G2': 'Generation 2',
    'G3': 'Generation 3',
    'HP': 'Internal combustion engine with heat recovery',
    'OF': 'Offshore',
    'ON': 'Onshore',
    'ST': 'Steam cycle',
    'UT': 'Utility PV',
    'WV': 'Wave power',
    'RF': 'Refinery',
    '00': 'unspecified',
    'BG': 'Biomass gasification',
    'BC': 'Biomass gasification with CCS',
    'SR': 'Steam reforming',
    'SC': 'Steam reforming with CCS',
    'EA': 'alkaline Electrolysis',
    'EP': 'PEM Electrolysis',
    'ES': 'Solid oxide Electrolysis',
    'EC': 'Electrolysis (unspecified)',
    'SL': 'Storage loading and unloading',
}

energy_level_codes = {
    'P': 'Primary energy commodity',
    'F': 'Final electricity',
    'I': 'Import technology',
    'X': 'Extraction or generation technology',
    'E': 'Export technology',
}

age_codes = {
    'H': 'Historic',
    'N': 'New',
}

emission_codes = {
    'CO2': 'Carbon dioxide',
    'PM25': 'Particulate matter 2.5',
    'HO': 'Hydro power dummy',
    'SO': 'Solar pv dummy',
    'WI': 'Wind power dummy',
    'WO': 'Wind offshore dummy',
}

def decode_code(code, specifier=None, is_emission=False):
    """Decodes a single code of 4 or 9 digits as a full description or just a specific part of the code such as the country.
    Args:
        code (str): The code to decode.
        specifier (str): The specifier to decode. None means the whole code is decoded. Values can be 'country', 'commodity', 'technology', 'energy_level', 'age', 'size' or 'emission'.
        is_emission (bool): True if the code is an emission code, False otherwise.
    Returns:
        str: The decoded description of the code.
    """
    if specifier == 'emission' and is_emission == False:
        is_emission = True
        print('Warning: The argument is_emission needs to be True when the code is an emission code, it has been set to rue because the specifier was set to "emission"')
    if is_emission:
        if specifier == None:
            if code == 'CO2': return 'Carbon dioxide'
            else:
                country = code[0:2]
                emission = code[2:]
                country_description = country_codes.get(country, f'Unknown country')
                emission_description = emission_codes.get(emission, f'Unknown emission')
                description = (
                    f"{country_description} ({country})| "
                    f"{emission_description} ({emission})"
                    )
                return description
        elif specifier == 'country':
            if code == 'CO2': return 'All countries'
            else:
                country = code[0:2]
                country_description = country_codes.get(country, f'Unknown country')
                return country_description
        elif specifier == 'emission':
            if code == 'CO2': return 'Carbon dioxide'
            else:
                emission = code[2:]
                emission_description = emission_codes.get(emission, f'Unknown emission')
                return emission_description           
    elif len(code) == 4 or len(code) == 9:
        description = 'Error: Check the script.'
        country = code[0:2]
        commodity = code[2:4]
        country_description = country_codes.get(country, f'Unknown country')
        commodity_description = commodity_codes.get(commodity, f'Unknown commodity')
        if specifier == None:
            description = (
                f"{country_description} ({country})| "
                f"{commodity_description} ({commodity})"
                )
        if len(code) == 9:
            technology = code[4:6]
            energy_level = code[6]
            age = code[7]
            size = code[8]
            if technology in technology_codes:
                technology_description = technology_codes[technology]
            elif technology in country_codes:
                technology_description = f'connected to {country_codes[technology]}'
            else: technology_description = 'Unknown technology'
            energy_level_description = energy_level_codes.get(energy_level, f'Unknown energy level')
            age_description = age_codes.get(age, f'Unknown age')
            size_description = f'size {size}'
            if specifier == None:
                description = (
                    f"{country_description} ({country})| "
                    f"{commodity_description} ({commodity})| "
                    f"{technology_description} ({technology})| "
                    f"{energy_level_description} ({energy_level})| "
                    f"{age_description} ({age})| "
                    f"{size_description}"
                    )
        if specifier == 'country':
            description = country_description
        elif specifier == 'commodity':
            description = commodity_description
        elif specifier == 'technology':
            description = technology_description
        elif specifier == 'energy_level':
            description = energy_level_description
        elif specifier == 'age':
            description = age_description
        elif specifier == 'size':
            description = size_description
        return description
    else:
        print('Warning: The code is not 4 or 9 digits long and the boolean is_emission is set to false.')
        for emission in emission_codes:
            if emission in code:
                print('The code seems to be an emission.')
                return decode_code(code, specifier, True)
                       
    
def add_code_descriptions_to_csv(input_csv_filename, output_csv_filename=None):
    """Modifies a CSV file by adding a ' #codedescription' column.
    
    This function reads a CSV file containing codes in one column, decodes each
    code using the decode_tech function for 9 digit codes and decode_fuel for 4-digit codes,
    and adds a new column to the CSV file with the decoded descriptions in the format ' #codedescription'.
    It overrides the input CSV file with the modified data if the output file name is not provided
    or if it's the same as the input file name.
    
    Args:
        input_csv_filename (str): The name of the input CSV file.
        output_csv_filename (str, optional): The name of the output CSV file.
    
    Returns:
        None
    """
    try:
        # Read the input CSV file
        df = pd.read_csv(input_csv_filename, header=None)

        # Store the existing header
        header = df.iloc[0].tolist()
        header.append("description")
        df1 = pd.DataFrame([header])

        # Remove the header from the DataFrame
        df = df.iloc[1:]

        # Apply the decode_code and add a new column        
        df[1] = df[0].apply(lambda code: f'#{decode_code(code)}' if not pd.isna(code) else '')
        #create new dataframe
        df = pd.concat([df1, df], ignore_index=True)

        if output_csv_filename is None or output_csv_filename == input_csv_filename:
            while True:
                overwrite_input = input(f"Overwrite '{input_csv_filename}'? (yes/no): ").strip().lower()
                if overwrite_input == 'yes':
                    # Save the modified DataFrame back to the input CSV file, overriding it
                    df.to_csv(input_csv_filename, index=False, header=False)
                    print(f"Code descriptions added to '{input_csv_filename}'.")
                    break
                elif overwrite_input == 'no':
                    break
                else:
                    print("Please enter 'yes' or 'no'.")

        else:
            # Save the modified DataFrame to the output CSV file
            df.to_csv(output_csv_filename, index=False, header=False)
            print(f"Code descriptions saved to '{output_csv_filename}'.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Add a new functions to handle decoding codes from the command line
def decode_code_from_cli():
    if len(sys.argv) != 3:
        print("Usage: python script.py decode_code <code>")
    else:
        code = sys.argv[2]
        result = decode_code(code)
        print(result)
     

# if __name__ == '__main__':
    # input_file = 'input_data\\WP1_NetZero\\data\\TECHNOLOGY.csv'
    # output_file = 'tech_codes.csv'
    # if len(sys.argv) < 2 or len(sys.argv) > 3:
    #     print("Usage: python script.py input_file [output_file]")
    # else:
    #     input_file = sys.argv[1]
    #     output_file = sys.argv[2] if len(sys.argv) > 2 else None
    #     add_code_descriptions_to_csv(input_file, output_file)
    

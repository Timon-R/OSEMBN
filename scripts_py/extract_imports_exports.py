'''
This scripts takes the results of the OSeMBE model and extracts the imports and exports of the Nordic countries.
It writes the results to the TotalTechnologyAnnualActivityUpperLimit.csv and TotalTechnologyAnnualActivityLowerLimit.csv files.

This allows for setting the imports and exports of the Nordics to the same value in the OSeMBE model without having the same dynamic interconnector technologies.
@author: Timon Renzelmann
'''


import pandas as pd


codes = [
    "DEELDKPH1",
    "DKELNLPH1",
    "EEELFIPH1",
    "DEELNOPH1",
    "NLELNOPH1",
    "NOELUKPH1",
    "DEELSEPH1",
    "LTELSEPH1",
    "PLELSEPH1"
]

import_codes = [
    "DKELDEIH1",
    "DKELNLIH1",
    "FIELEEIH1",
    "NOELDEIH1",
    "NOELNLIH1",
    "NOELUKIH1",
    "SEELDEIH1",
    "SEELLTIH1",
    "SEELPLIH1"
]
countries = ['SE', 'NO', 'DK', 'FI']

def rename_technology(tech, is_import):
    if tech[:2] not in countries:
        tech = tech[4:6] + tech[2:4] + tech[:2] + tech[6:]
    if is_import:
        tech = tech[:-3] + 'IH1'
    if not is_import:
        tech = tech[:-3] + 'EH1'
    return tech

folder = 'input_data/Nordic_no_h2/data/'

def main(folder):

    df = pd.read_csv('results/OSeMBE/results_csv/TotalAnnualTechnologyActivityByMode.csv')
    df = df[df['TECHNOLOGY'].isin(codes)]
    df['is_import'] = df.apply(lambda row: True if ((row['TECHNOLOGY'][:2] in countries and row['MODE_OF_OPERATION'] == 2) or 
                                                    (row['TECHNOLOGY'][:2] not in countries and row['MODE_OF_OPERATION'] == 1)) 
                                else False, axis=1)

    df_lower_limit_exports = df[df['is_import'] == False].groupby(['TECHNOLOGY', 'YEAR']).sum().reset_index()
    df_upper_limit_imports = df[df['is_import'] == True].groupby(['TECHNOLOGY', 'YEAR']).sum().reset_index()

    df_lower_limit_exports['TECHNOLOGY'] = df_lower_limit_exports.apply(lambda row: rename_technology(row['TECHNOLOGY'], False), axis=1)
    df_upper_limit_imports['TECHNOLOGY'] = df_upper_limit_imports.apply(lambda row: rename_technology(row['TECHNOLOGY'], True), axis=1)

    df_lower_limit_exports = df_lower_limit_exports[['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE']]
    df_upper_limit_imports = df_upper_limit_imports[['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE']]
    df_lower_limit_exports['REGION'] = 'REGION1'
    df_upper_limit_imports['REGION'] = 'REGION1'

    
    # Create a pivot table
    pivot = df_upper_limit_imports.pivot_table(index=['REGION', 'TECHNOLOGY'], columns='YEAR', values='VALUE', fill_value=0)


    # Create a DataFrame with all combinations of 'REGION', 'TECHNOLOGY', and 'YEAR'
    df_all_years = pd.DataFrame([(region, technology, year) for region in df_upper_limit_imports['REGION'].unique() 
                                for technology in import_codes
                                for year in range(2015, 2061)], 
                                columns=['REGION', 'TECHNOLOGY', 'YEAR'])

    # Merge this DataFrame with the original DataFrame, filling missing values with 0
    df_upper_limit_imports = pd.merge(df_all_years, df_upper_limit_imports, on=['REGION', 'TECHNOLOGY', 'YEAR'], how='left').fillna(0)

    # Reorder the columns
    df_upper_limit_imports = df_upper_limit_imports[['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE']]

    # Sort the DataFrame
    df_lower_limit_exports = df_lower_limit_exports.sort_values(by=['TECHNOLOGY', 'YEAR'])

    df_lower_limit_exports = df_lower_limit_exports[['REGION', 'TECHNOLOGY', 'YEAR', 'VALUE']]
   
    df_upper_limit_imports = df_upper_limit_imports.sort_values(by=['TECHNOLOGY', 'YEAR'])
    df_lower_limit_exports = df_lower_limit_exports.sort_values(by=['TECHNOLOGY', 'YEAR'])

    # df_upper_limit_imports.to_csv('upper_limit_imports.csv', index=False)
    # df_lower_limit_exports.to_csv('lower_limit_exports.csv', index=False)

    # Read the existing CSV files
    original_folder = 'input_data/Nordic_before_interconnectors/data/'
    df_existing_upper_limit_imports = pd.read_csv(original_folder+'TotalTechnologyAnnualActivityUpperLimit.csv')
    df_existing_lower_limit_exports = pd.read_csv(original_folder+'TotalTechnologyAnnualActivityLowerLimit.csv')

    # Concatenate the existing DataFrames with the new DataFrames
    df_upper_limit_imports = pd.concat([df_existing_upper_limit_imports, df_upper_limit_imports])
    df_lower_limit_exports = pd.concat([df_existing_lower_limit_exports, df_lower_limit_exports])

    # Drop duplicates based on 'REGION', 'TECHNOLOGY', and 'YEAR', keeping the last occurrence
    df_upper_limit_imports = df_upper_limit_imports.drop_duplicates(subset=['REGION', 'TECHNOLOGY', 'YEAR'], keep='last')
    df_lower_limit_exports = df_lower_limit_exports.drop_duplicates(subset=['REGION', 'TECHNOLOGY', 'YEAR'], keep='last')

    df_upper_limit_imports = df_upper_limit_imports.sort_values(by=['TECHNOLOGY', 'YEAR'])
    df_lower_limit_exports = df_lower_limit_exports.sort_values(by=['TECHNOLOGY', 'YEAR'])

    # Write the resulting DataFrames back to the CSV files
    df_upper_limit_imports.to_csv(folder+'TotalTechnologyAnnualActivityUpperLimit.csv', index=False)
    df_lower_limit_exports.to_csv(folder+'TotalTechnologyAnnualActivityLowerLimit.csv', index=False)
    print(folder + ' done')


# folder = 'input_data/Nordic_no_h2/data/'
# main(folder)

for folder in ['input_data/Nordic_no_h2/data/', 'input_data/Nordic/data/', 'input_data/Nordic_em_free/data/', 'input_data/Nordic_co2_limit/data/', 'input_data/Nordic_co2_tax/data/']:
    main(folder)
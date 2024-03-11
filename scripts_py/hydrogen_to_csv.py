'''
This script adds all the values from the hydrogen excel sheet to the csv files.
It is limited to a specific excel format.

Common error: AttributeError: 'float' object has no attribute 'startswith'. Happens when the script takes empty rows from excel.
Solution: delete the empty rows in excel.

@author: Timon Renzelmann

'''

import openpyxl
import numpy as np
import pandas as pd
import os
import sys

def load_data(workbook , sheets_to_exclude = [], technologies_to_exclude = []):
    '''
    This function loads the data from the excel sheet and returns it as a dictionary.
    The keys are the sheet names and the values are the dataframes.

    Parameters
    ----------
    workbook : str
        The name of the excel workbook.
    sheets_to_exclude : list, optional
        A list of sheet names that should be excluded from the dictionary. The default is [].

    Returns 
    -------
    data_dict : dict
        A dictionary with the sheet names as keys and the dataframes as values.
    '''
    workbook = openpyxl.load_workbook(workbook, data_only=True)
    data_dict = {}
    for sheet in workbook.worksheets:
        if sheet.title == 'TotalAnnualMaxCapacityInvest':
            sheetname = 'TotalAnnualMaxCapacityInvestment'
        else:
            sheetname = sheet.title
        if sheetname not in sheets_to_exclude:
            if sheetname in ['Conversionld','Conversionls','Conversionlh','DaySplit','DaysInDayType']:
                # Extract values from the Excel sheet
                values1 = [cell.value for cell in sheet['A'][1:]] 
                values2 = [cell.value for cell in sheet['B'][1:]]  
                values3 = [cell.value for cell in sheet['C'][1:]]  
                if sheetname == 'DaysInDayType':
                    values4 = [cell.value for cell in sheet['D'][1:]]  
                # Create a DataFrame for each value
                df = pd.DataFrame({
                    sheet['A'][0].value: values1,
                    sheet['B'][0].value: values2,
                    sheet['C'][0].value: values3,
                })
                if sheetname == 'DaysInDayType':
                    df[sheet['D'][0].value] = values4
                data_dict[sheetname] = df             

            elif sheetname in ['TechnologyToStorage','TechnologyFromStorage']:
                # Extract technologies and values from the Excel sheet
                region = [cell.value for cell in sheet['A'][1:]]
                technologies = [cell.value for cell in sheet['B'][1:]]
                storage = [cell.value for cell in sheet['C'][1:]]
                m_o_o = [cell.value for cell in sheet['D'][1:]]
                values = [cell.value for cell in sheet['E'][1:]]
                # Create a DataFrame for each technology-value combination
                df = pd.DataFrame({
                    "REGION": region,
                    "TECHNOLOGY": technologies,
                    "STORAGE": storage,
                    "MODE_OF_OPERATION": m_o_o,
                    "VALUE": values
                })
                data_dict[sheetname] = df
            elif sheetname in ['OperationalLifeStorage']:
                # Extract storage techs and values from the Excel sheet
                storage = [cell.value for cell in sheet['A'][1:]]  # Column A for technologies
                values = [cell.value for cell in sheet['B'][1:]]  # Column B for values
                # Create a DataFrame for each technology-value combination
                df = pd.DataFrame({
                    "STORAGE": storage,
                    "VALUE": values
                }) 
                data_dict[sheetname] = df
            elif sheetname in ['OperationalLife', 'CapacityToActivityUnit']:    
                # Extract technologies and values from the Excel sheet
                technologies = [cell.value for cell in sheet['A'][1:]]  # Column A for technologies
                values = [cell.value for cell in sheet['B'][1:]]  # Column B for values
                # Create a DataFrame for each technology-value combination
                df = pd.DataFrame({
                    "TECHNOLOGY": technologies,
                    "VALUE": values
                })
                df = df[~df['TECHNOLOGY'].isin(technologies_to_exclude)]    
                data_dict[sheetname] = df
            elif sheetname == 'SpecifiedDemandProfile':
                # Extract values from the Excel sheet
                fuels = [cell.value for cell in sheet['A'][1:]]
                timeslices = [cell.value for cell in sheet['B'][1:]]
                values = [cell.value for cell in sheet['C'][1:]]
                # Create a DataFrame for each value
                df = pd.DataFrame({
                    "FUEL": fuels,
                    "TIMESLICE": timeslices,
                    "VALUE": values
                })
                data_dict[sheetname] = df
            elif sheetname in ['TECHNOLOGY','FUEL','STORAGE','DAILYTIMEBRACKET','DAYTYPE','SEASON']:    
                # Extract values from the Excel sheet
                values = [cell.value for cell in sheet['A'][1:]]  # Column A for values
                # Create a DataFrame for each value
                df = pd.DataFrame({
                    "VALUE": values
                })
                df = df[~df['VALUE'].isin(technologies_to_exclude)]    
                data_dict[sheetname] = df
            else:
                # Extract years and values from the Excel sheet
                years = [cell.value for cell in sheet[1][1:47]]  # Adjust as needed
                values = {technology[0].value: [cell.value for cell in technology[1:47]] for technology in sheet.iter_rows(min_row=2)}
                # Create a DataFrame for each technology and concatenate them
                dfs = []
                for technology, vals in values.items():
                    if technology not in technologies_to_exclude:
                        if sheetname in ['AccumulatedAnnualDemand','SpecifiedAnnualDemand']:
                            column_name = "FUEL"
                        elif sheetname == 'CapitalCostStorage':
                            column_name = "STORAGE"
                        else:
                            column_name = "TECHNOLOGY"        
                        df = pd.DataFrame({                            
                            column_name: technology,
                            "YEAR": years,
                            "VALUE": vals
                        })
                        #convert from PJ/year to GW, from 2021 USD to 2015 USD (0.875) and from 2015 USD to 2015 € (/1.16)
                        if sheetname in ['CapitalCost', 'FixedCost']:
                            df['VALUE'] = df['VALUE'] * 31.536 * 0.875 / 1.16
                        elif sheetname in ['VariableCost', 'CapitalCostStorage']:
                            df['VALUE'] = df['VALUE'] * 1.16
                        df = df.dropna(axis=1, how='all')
                        dfs.append(df)
                df = pd.concat(dfs, ignore_index=True)
                data_dict[sheetname] = df
    return data_dict

def get_fuel(technology, input_bool,mode):
    '''
    This function is for getting the fuel for the InputActivityRatio and OutputActivityRatio sheets.
    '''
    if 'SL' in technology:
        return technology[:2] + 'H1'
    elif mode == 1:
        if input_bool:
            if 'SR' in technology:
                return technology[:2] + 'NG'
            elif 'BG' in technology or 'BC' in technology:
                return technology[:2] + 'BM'
            elif 'TD' in technology:
                return technology[:2] + 'H1'
            elif 'FC' in technology:
                return technology[:2] + 'H1'
            else:
                return technology[:2] + 'E1'
        else:
            if 'TD' in technology:
                return technology[:2] + 'H2'
            elif 'FC' in technology:
                return technology[:2] + 'E1'
            else:
                return technology[:2] + 'H1'
    else:
        return technology[:2] + 'H1'
    
def create_new_rows(df, technologies_to_split, is_input):
    '''
    This is for modifying the InputActivityRatio and OutputActivityRatio sheets.'''
    new_rows = []
    for _, row in df.iterrows():
        technology = row['TECHNOLOGY']
        if technology in technologies_to_split:
            h = 'H1'
            c = technology[4:6]
            new_rows.append({'REGION': row['REGION'], 'TECHNOLOGY': technology, 'MODE_OF_OPERATION': 1 if is_input else 2, 'FUEL': technology[:2] + h, 'YEAR': row['YEAR'], 'VALUE': row['VALUE']})
            new_rows.append({'REGION': row['REGION'], 'TECHNOLOGY': technology, 'MODE_OF_OPERATION': 2 if is_input else 1, 'FUEL': c + h, 'YEAR': row['YEAR'], 'VALUE': row['VALUE']})
        else:
            if 'HGSL' in technology:
                m_o_o = 1 if is_input else 2
            else:
                m_o_o = 1
            new_rows.append({'REGION': row['REGION'], 'TECHNOLOGY': technology, 'MODE_OF_OPERATION': m_o_o, 'FUEL': get_fuel(technology, is_input,1), 'YEAR': row['YEAR'], 'VALUE': row['VALUE']})
    return pd.DataFrame(new_rows)


def modify_data_for_csv(data_dict):
    '''
    This function modifies the data from the excel sheet to the format of the csv files adding columns like Mode of Operation and Time Slice.
    It also arranges the order of the columns.
    '''
    #for the interconnectors, add two mode of operation columns, one for each direction
    data = data_dict
    technologies_to_split = ['FIHGNOPH1', 'FIHGSEPH1', 'NOHGSEPH1', 'DKHGNOPH1', 'DKHGSEPH1']
    time_slices = ['S01B1', 'S01B2', 'S01B3', 'S02B1', 'S02B2', 'S02B3', 'S03B1', 'S03B2', 'S03B3', 'S04B1', 'S04B2', 'S04B3', 'S05B1', 'S05B2', 'S05B3']
    for key, df in data.items():
        if key not in ['TECHNOLOGY','FUEL','STORAGE','TechnologyToStorage','TechnologyFromStorage','DAILYTIMEBRACKET','DAYTYPE','SEASON','Conversionld','Conversionls','Conversionlh','DaySplit','DaysInDayType']:
            df = df.assign(REGION='REGION1')
            if key == 'VariableCost':
                df = df.assign(MODE_OF_OPERATION=1)
                df = df[['REGION', 'TECHNOLOGY', 'MODE_OF_OPERATION', 'YEAR', 'VALUE']]
            elif key in ['InputActivityRatio', 'OutputActivityRatio']:
                df = create_new_rows(df, technologies_to_split, key == 'InputActivityRatio')
                df = df[['REGION', 'TECHNOLOGY', 'FUEL', 'MODE_OF_OPERATION', 'YEAR', 'VALUE']]  
            elif key == 'CapacityFactor':
                df['TIMESLICE'] = [time_slices] * len(df)
                df = df.explode('TIMESLICE')
                df = df[['REGION', 'TECHNOLOGY', 'TIMESLICE', 'YEAR', 'VALUE']]
            elif key == 'SpecifiedDemandProfile':
                df['YEAR'] = [list(range(2015, 2061))] * len(df)
                df = df.explode('YEAR')
                df = df[['REGION', 'FUEL', 'TIMESLICE', 'YEAR', 'VALUE']]  # Reorder the columns
            elif key == 'EmissionActivityRatio':
                df = df.assign(MODE_OF_OPERATION=1)
                df['EMISSION'] = df['TECHNOLOGY'].apply(lambda x: 'CO2' if x.endswith('HGSCPN2') or x.endswith('HGBCPN2') else x[:2] + 'PM25')
                df = df[['REGION', 'TECHNOLOGY', 'EMISSION', 'MODE_OF_OPERATION', 'YEAR', 'VALUE']]
            elif key == 'AccumulatedAnnualDemand':
                df = df[['REGION', 'FUEL', 'YEAR', 'VALUE']]
            elif key == 'CapitalCostStorage':
                df = df[['REGION', 'STORAGE', 'YEAR', 'VALUE']]
            else:
                df = df[['REGION'] + [col for col in df.columns if col != 'REGION']]
            data[key] = df
    return data_dict

def split_techs_into_countries(data_dict):
    '''
    This function splits the technologies into the different countries.
    Parameters
    ----------
    data_dict : dict
        A dictionary with the sheet names as keys and the dataframes as values.

    Returns
    -------
    data_dict : dict
    '''
    keys_to_exclude = ['FUEL', 'STORAGE','TechnologyToStorage','TechnologyFromStorage','OperationalLifeStorage','DAILYTIMEBRACKET','DAYTYPE','SEASON','Conversionld','Conversionls','Conversionlh','DaySplit','DaysInDayType', 'SpecifiedDemandProfile']
    countries = ['NO', 'SE', 'DK', 'FI']
    for key, df in data_dict.items():
        if key not in keys_to_exclude:
            if key == 'TECHNOLOGY':
                new_technologies = []
                for technology in df['VALUE']:
                    if any(technology.startswith(country) for country in countries):
                        new_technologies.append(technology)
                    else:
                        for country in countries:
                            new_technologies.append(country + technology)                 
                data_dict[key] = pd.DataFrame(new_technologies, columns=['VALUE'])
            else:
                new_rows = []
                for _, row in df.iterrows():
                    if key in ['AccumulatedAnnualDemand','SpecifiedAnnualDemand']:
                        column_name = "FUEL"
                    elif key == 'CapitalCostStorage':
                        column_name = "STORAGE"
                    else:
                        column_name = "TECHNOLOGY"
                    technology = row[column_name]
                    if any(technology.startswith(country) for country in countries):
                        new_rows.append(row)
                    else:
                        for country in countries:
                            new_row = row.copy()
                            new_row[column_name] = country + technology
                            new_rows.append(new_row)
                data_dict[key] = pd.DataFrame(new_rows)
    return data_dict

def add_to_csv(csv_folder, output_folder, data_dict):
    '''
    This function adds the data from the excel sheet to the csv files.

    Parameters
    ----------
    csv_folder : str
        The path to the folder with the input csv files.
    output_folder : str
        The path to the folder where the updated csv files will be written.
    data_dict : dict
        A dictionary with the sheet names as keys and the dataframes as values.

    Returns
    -------
    None.
    '''
    for key, df in data_dict.items():
        file_name = key + '.csv'
        input_file_path = os.path.join(csv_folder, file_name)
        output_file_path = os.path.join(output_folder, file_name)
        if os.path.isfile(input_file_path):
            csv_df = pd.read_csv(input_file_path)
            if not csv_df.empty:
                if key in ['TECHNOLOGY', 'FUEL', 'STORAGE','DAILYTIMEBRACKET','DAYTYPE','SEASON']:
                    merged_df = pd.concat([csv_df, df])
                    merged_df.drop_duplicates(keep='first', inplace=True)
                else:
                    merge_columns = csv_df.columns.tolist()
                    merge_columns.remove('VALUE')
                    merged_df = csv_df.merge(df, on=merge_columns, how='outer')
                    merged_df['VALUE'] = merged_df['VALUE_y'].where(pd.notna(merged_df['VALUE_y']), merged_df['VALUE_x'])
                    merged_df = merged_df[csv_df.columns]                    
                    # Get a list of all column names except 'VALUE'
                    sort_columns = merged_df.columns.tolist()
                    sort_columns.remove('VALUE')
                    # Sort the DataFrame
                    merged_df.sort_values(sort_columns, inplace=True)
            else:
                merged_df = df
            merged_df.dropna(subset=['VALUE'], inplace=True)  
            # Sort the DataFrame  
            merged_df.to_csv(output_file_path, index=False)
        else:
            print(input_file_path + ' does not exist.')
    # Copy all non-modified csv files
    for file_name in os.listdir(csv_folder):
        if file_name.endswith('.csv') and file_name[:-4] not in data_dict:
            with open(os.path.join(csv_folder, file_name), 'r') as src_file:
                with open(os.path.join(output_folder, file_name), 'w') as dst_file:
                    dst_file.write(src_file.read())

if __name__ == "__main__":

    #args = sys.argv[1:]

    args = ['Hydrogen_baseline.xlsx', 'Nordic_co2_tax']
    input_file = args[0]
    scenario = args[1]
    if input_file is not None:            
        if scenario == 'Nordic': #includes specified demand for denmark now 1 PJ/year for S2B1
            sheets_to_exclude = ['Efficiancy','Helpsheet','StorageMaxChargeRate','StorageMaxDischargeRate','TotalAnnualMaxCapacity', 'CapitalCost_GW_EURO', 'FixedCost_GW_EURO','VariableCost_GW_EURO']
        else: #for the testing scenarios using a specified demand profile
            sheets_to_exclude = ['Efficiancy','Helpsheet','StorageMaxChargeRate','StorageMaxDischargeRate','TotalAnnualMaxCapacity']
        technologies_to_exclude = ['HGEAPN2','HGEPPN2','HGESPN2'] #, "FIHGNOPN1", "FIHGSEPN1", "NOHGSEPN1", "DKHGNOPN1", "DKHGSEPN1"
        #without storage
        # sheets_to_exclude = ['Efficiancy','Helpsheet','StorageMaxChargeRate','StorageMaxDischargeRate', 'STORAGE', 'OperationalLifeStorage', 'TechnologyToStorage', 'TechnologyFromStorage', 'CapitalCostStorage','StorageMaxChargeRate','StorageMaxDischargeRate','SpecifiedDemandProfile','SpecifiedAnnualDemand','TotalAnnualMaxCapacity','DAILYTIMEBRACKET','DAYTYPE','SEASON','Conversionld','Conversionls','Conversionlh','DaySplit','DaysInDayType']
        # technologies_to_exclude = ['HGEAPN2','HGEPPN2','HGESPN2', 'HGSLPN2']
        data_dict = load_data(input_file, sheets_to_exclude, technologies_to_exclude)
        data_dict = split_techs_into_countries(data_dict)
        data_dict = modify_data_for_csv(data_dict)
        output_csv_folder = f'input_data\\{scenario}\\data'
        input_csv_folder = 'input_data\\Nordic_no_h2\\data'
        add_to_csv(input_csv_folder,output_csv_folder, data_dict)
        print('The csv files have been updated.')
    else: 
        raise Exception('No input file given. The script can only work with two excel sheets currently, hydrogen_baseline and hydrogen_test.')                


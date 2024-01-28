"""
This script aims to visualize the results. 

@author: Timon Renzelmann

based on vizymosys 

This script is not polished yet and contains a bunch of functions that can create different plots.
"""
import plotly.express as px
import pandas as pd
import os
import code_decipherer as cd
import electricity_generation_plot as electricity_generation_plot
import plotly.graph_objects as go
import code_decipherer as cd
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from PIL import Image
from d3blocks import D3Blocks
# import holoviews as hv
# from holoviews import opts, dim
# import bokeh.io as bk


valid_countries = ['All countries','Sweden', 'Norway', 'Finland', 'Denmark']
# Define a dictionary to map country codes to country names
country_names = {"SE": "Sweden", "NO": "Norway", "DK": "Denmark", "FI": "Finland"}
# Define the country codes
country_codes = list(country_names.keys())
renewable_commodities = ['BF', 'BM', 'EL', 'E1', 'E2', 'GO', 'HY', 'OC', 'SO', 'WS', 'WI', 'H1','H2']
fossil_free_commodities = ['BF', 'BM', 'EL', 'E1', 'E2', 'GO', 'HY', 'NU', 'UR', 'OC', 'SO', 'WS', 'WI', 'H1','H2'] #includes nuclear and uranium
fossil_sources_commodities = ['CO', 'HF', 'OI', 'OS', 'NG']
hydrogen_technologies = [
    "SEHGEAPH2", "NOHGEAPH2", "NOHGSRPH2", "SEHGSRPH2", "DKHGSRPH2", "FIHGSRPH2",
    "NOHGSRPN2", "SEHGSRPN2", "DKHGSRPN2", "FIHGSRPN2", "NOHGSCPN2", "SEHGSCPN2",
    "DKHGSCPN2", "FIHGSCPN2", "NOHGBGPN2", "SEHGBGPN2", "DKHGBGPN2", "FIHGBGPN2",
    "NOHGBCPN2", "SEHGBCPN2", "DKHGBCPN2", "FIHGBCPN2", "NOHGEAPN2", "SEHGEAPN2",
    "DKHGEAPN2", "FIHGEAPN2", "NOHGEPPN2", "SEHGEPPN2", "DKHGEPPN2", "FIHGEPPN2",
    "NOHGESPN2", "SEHGESPN2", "DKHGESPN2", "FIHGESPN2", "NOHGFCPN2", "SEHGFCPN2",
    "DKHGFCPN2", "FIHGFCPN2", "FIHGNOPN1", "FIHGSEPN1", "NOHGSEPN1", "DKHGNOPN1", "DKHGSEPN1",
    "NOHGECPN2", "SEHGECPN2", "DKHGECPN2", "FIHGECPN2",
    "NOHGSLPN2", "SEHGSLPN2", "DKHGSLPN2", "FIHGSLPN2",
] # could be changed to if contains 'HG'
hydrogen_se = [tech for tech in hydrogen_technologies if "SE" in tech]
hydrogen_no = [tech for tech in hydrogen_technologies if "NO" in tech]
hydrogen_fi = [tech for tech in hydrogen_technologies if "FI" in tech]
hydrogen_dk = [tech for tech in hydrogen_technologies if "DK" in tech]

storage_techs = ["NOHGSLPN2", "SEHGSLPN2", "DKHGSLPN2", "FIHGSLPN2"]

def get_transmission_techs(tech_list):
    return [tech for tech in tech_list if sum(code in tech for code in country_codes) > 1]

def get_production_techs(tech_list):
    return [tech for tech in tech_list if sum(code in tech for code in country_codes) <= 1 and tech not in storage_techs]
#note that for elec-generation the source of the EL matters

def load_data(df, scenario, variable, data_path='results'):
    '''
    Description: This function loads a CSV file with the given variable name from the scenario directory and appends it to the given DataFrame df. The resulting DataFrame is returned.
    Parameters:
    df (pandas DataFrame): The DataFrame to which the loaded data will be appended.
    scenario (str): The name of the directory containing the CSV file.
    variable (str): The name of the CSV file to be loaded.

    Returns: df (pandas DataFrame): The DataFrame with the loaded data appended.
    '''
    file = os.path.join(data_path, scenario, 'results_csv',f'{variable}.csv')
    _df = pd.read_csv(file)
    _df['scenario'] = scenario
     # Drop columns that are all NA
    df = df.dropna(how='all', axis=1)
    _df = _df.dropna(how='all', axis=1)
    return pd.concat([df,_df], ignore_index=True)

def create_df_dict(directory_names, data_path='results'):
    '''
    Description: This function creates a dictionary of DataFrames, where each DataFrame contains the data of one parameter for all given scenarios.
    Each dataframe has an additional column 'scenario' that contains the name of the scenario.
    
    The function calls the load_data function for each scenario and variable.

    Parameters:
    data_path (str): The path to the directory containing the scenario directories.
    '''
    df_dict = {}
    directories = {name: data_path + '\\' + name + '\\results_csv' for name in directory_names}
    
    # Get CSV filenames for each directory
    csv_files = {dir: [f for f in os.listdir(path) if f.endswith('.csv')] for dir, path in directories.items()}
    # Get filenames without extensions
    filenames = {dir: set([os.path.splitext(f)[0] for f in files]) for dir, files in csv_files.items()}
    #Check for filenames that are not in all directories and only load data for common filenames
    all_filenames = set.union(*filenames.values())
    common_filenames = set.intersection(*filenames.values())
    not_in_all_dirs = set(f for f in all_filenames if sum(f in filenames[dir] for dir in directories.keys()) != len(directories))  # Check which directories each unique filename exists in
    # Check which directories each filename is missing in and print in which directories it is missing
    for filename in not_in_all_dirs:
        present_dirs = [dir for dir, files in filenames.items() if filename in files]
        missing_dirs = [dir for dir in directories.keys() if dir not in present_dirs]
        for dir in missing_dirs:
            print(f"{filename} is missing in {dir}")
    # Load data for common filenames
    for param in common_filenames:
        df_dict[param] = pd.DataFrame()
        for dir in directories.keys():
            df_dict[param] = load_data(df_dict[param], dir, param)
    return df_dict

def remove_unwanted_countries(dff):
    if 'TECHNOLOGY' in dff.columns:
        dff['country'] = dff['TECHNOLOGY'].apply(cd.decode_code, args=('country',))
        dff = dff[dff['country'].isin(valid_countries)]
    elif 'FUEL' in dff.columns:
        dff['country'] = dff['FUEL'].apply(cd.decode_code, args=('country',))
        dff = dff[dff['country'].isin(valid_countries)]
    elif 'EMISSION' in dff.columns:
        dff['country'] = dff['EMISSION'].apply(cd.decode_code, args=('country',True))
        dff = dff[dff['country'].isin(valid_countries)]
    return dff

def get_color(legend_value, biomass_counter, electrolysis_counter, steam_counter):
    green_shades = ['green', 'forestgreen', 'darkgreen', 'lightgreen', 'limegreen']
    blue_shades = ['blue', 'deepskyblue', 'dodgerblue', 'steelblue', 'lightblue']
    black_shades = ['black', 'dimgray', 'gray', 'darkgray', 'silver']
    if 'Biomass' in legend_value:
        return green_shades[biomass_counter % len(green_shades)]
    elif 'Electrolysis' in legend_value:
        return blue_shades[electrolysis_counter % len(blue_shades)]
    elif 'Steam' in legend_value:
        return black_shades[steam_counter % len(black_shades)]
    else:
        return 'red'  # Default color

def write_high_res_plot(dff, title, param, filedesc, is_emission=False):
    '''
    Description: This function plots the given DataFrame dff and writes it to a file.
    Parameters:
    dff (pandas DataFrame): The DataFrame to be plotted. Has to include the column 'legend'.
    title (str): The title of the plot.
    param (str): The name of the variable to be plotted.
    filedesc (str): A string that will be appended to the filename.
    is_emission (bool): Whether the variable is an emission. If True, the plot will have two y-axes.
    '''
    dash_styles = ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
    colors = ['blue', 'green', 'red', 'black', 'orange', 'purple', 'brown']
    fig = go.Figure()
    biomass_counter = 0
    electrolysis_counter = 0
    steam_counter = 0
    for i, legend_value in enumerate(dff['legend'].unique()):
        df_subset = dff[dff['legend'] == legend_value]
        yaxis = 'y2' if is_emission and 'CO2' not in legend_value else 'y1'
        dash_style = 'dot' if 'Imports' in legend_value else dash_styles[i // len(colors) % len(dash_styles)]
        if 'Biomass' in legend_value:
            color = get_color(legend_value, biomass_counter, electrolysis_counter, steam_counter)
            biomass_counter += 1
        elif 'Electrolysis' in legend_value:
            color = get_color(legend_value, biomass_counter, electrolysis_counter, steam_counter)            
            electrolysis_counter += 1
        elif 'Steam' in legend_value:
            color = get_color(legend_value, biomass_counter, electrolysis_counter, steam_counter)            
            steam_counter += 1
        else:
            color = colors[i % len(colors)]        
        fig.add_trace(go.Scatter(
            x=df_subset['YEAR'], y=df_subset['VALUE'],
            mode='lines', name=legend_value,
            line=dict(color=color, dash=dash_style),
            yaxis=yaxis,
            showlegend=True
        ))        
    fig.update_layout(
        template='plotly_white', 
        title=title,
        legend=dict(orientation='v', yanchor="bottom", y=1.02, xanchor="right", x=1),
        #yaxis=dict(domain=[0, 0.85], showgrid=True, gridwidth=2, gridcolor='Grey'),
        yaxis=dict(domain=[0, 0.85]),
        yaxis2=dict(domain=[0, 0.85], anchor="x", position=1),
        font=dict(
        size=18,  # change this to the size you want
    )
        # shapes=[
        #     dict(
        #         type='line',
        #         yref='y', y0=0, y1=0,
        #         xref='paper', x0=0, x1=1,
        #         line=dict(color='Grey', width=2)
        #     )
        # ]
    )
    if is_emission:
        fig.update_layout(
            yaxis1=dict(title='CO2 in kton'),
            yaxis2=dict(title='PM2.5 in kton', overlaying='y', side='right')
        )
        # Define the base filename
    base_filename = 'visualisations\\' + param + filedesc
    extension = '.png'
    filename = base_filename + extension
    # Check if the file already exists
    # i = 2
    # while os.path.isfile(filename):
    #     # If the file exists, add a number to the filename
    #     filename = base_filename + '(' + str(i) + ')' + extension
    #     i += 1
    # Write the image
    fig.write_image(filename, height=600, width=1200)



def plot_annual_sum_by_scenario(df_dict, param, list_to_group_by = ['YEAR', 'scenario']):
    '''
    Description: This function plots the annual sum of the given variable for each scenario.
    Parameters:
    df_dict (dict): A dictionary of DataFrames, where each DataFrame contains the data of a scenario.
    param (str): The name of the variable to be plotted.
    '''
    if param != 'TotalTechnologyModelPeriodActivity' and param != 'CapitalInvestment':
            dff = remove_unwanted_countries(df_dict[param])
            dff = dff.groupby(list_to_group_by).sum().reset_index()
            dff['legend'] = dff[[col for col in list_to_group_by if col != 'YEAR']].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
            write_high_res_plot(dff, 'Annual sum of ' + param, param, '_annual_by_scenario', is_emission= False)

def plot_annual_sum_advanced(df_dict, param, scenarios = 'all', countries = ['all'], technologies = ['all'], split_countries = True, split_techs = True):
    '''
    Description: This function plots the annual sum of the given variable for each country.
    Parameters:
    df_dict (dict): A dictionary of DataFrames, where each DataFrame contains the data of a scenario.
    param (str): The name of the variable to be plotted.
    scenario (str): The name of the scenario to be plotted. If 'all', all scenarios are plotted.
    countries (list): A list of countries to be plotted. If 'all', all countries are plotted.
    technologies (list): A list of technologies to be plotted. If 'all', all technologies are plotted.
    '''
    dff = remove_unwanted_countries(df_dict[param])
    title = 'Annual sum of ' + param
    if scenarios != 'all':
        dff = dff[dff['scenario'] == scenarios]
    if countries != ['all']:
        dff = dff[dff['country'].isin(countries)]
    if technologies != ['all']:
        dff = dff[dff['TECHNOLOGY'].isin(technologies)]
    list_to_group_by = ['YEAR', 'scenario', 'country','TECHNOLOGY']
    if split_countries == False:
        list_to_group_by.remove('country')
        if countries == ['all']:
            title += ', all countries '
    else:
        title += str(countries) + ' '
    if split_techs == False:
        list_to_group_by.remove('TECHNOLOGY')
        title += ', all techs '
    if scenarios != ['all'] and len(countries) == 1:
        list_to_group_by.remove('scenario')
        title += ', scenario ' + scenarios
    dff = dff.groupby(list_to_group_by).sum().reset_index()
    # Create a column 'legend'
    list_to_group_by.remove('YEAR')
    list_to_group_by = [col for col in list_to_group_by if col in dff.columns]
    legend_entries = []
    for _, row in dff[list_to_group_by].iterrows():
        legend_entry = '_'.join(row.astype(str))
        legend_entries.append(legend_entry)
    dff['legend'] = legend_entries
    # Use 'legend' as the color parameter in your plot
    filedesc = ''
    if countries != 'all':
        filedesc = '_' + '_'.join(countries)
    filedesc += '_advanced'
    write_high_res_plot(dff, title, param, filedesc, is_emission= False)

def plot_emissions(df_dict, param, scenarios = 'all', emissions = ['all'], sum_emissions = False):
    dff = remove_unwanted_countries(df_dict[param])
    if scenarios != 'all':
        dff = dff[dff['scenario'] == scenarios]
    if emissions != ['all']:
        emission_codes = list()
        for emission in emissions:
            if emission != "CO2":
                for country in ['SE', 'NO', 'FI', 'DK']:
                    emission_codes.append(country + emission)
            else:
                emission_codes.append(emission)
        dff = dff[dff['EMISSION'].isin(emission_codes)]
    if sum_emissions:
           # Create a new column 'emission_type' that contains the emission type
        dff['emission_type'] = dff['EMISSION'].apply(lambda x: x[2:] if x != 'CO2' else x)
        # Group by 'emission_type' and sum the values
    else:
        dff['emission_type'] = dff['EMISSION']
    dff = dff.groupby(['YEAR', 'scenario', 'emission_type']).sum().reset_index()
    title = 'Annual sum of ' + param
    if scenarios == 'all':
        dff['legend'] = dff['scenario'] + '_' + dff['emission_type']
    else:
        dff['legend'] = dff['emission_type']
    title = 'Annual sum of ' + param 
    if scenarios != 'all':
        title += ', scenario ' + scenarios     
    write_high_res_plot(dff, title, param, '_'+scenarios, is_emission= True)
 
def plot_hydrogen(df_dict, scenario , countries = ['all']): #Fuel cells have to be negated
    '''
    Creates a hydrogen plot for one given scenario. Plots production in straight lines and imports and exports in dottet lines. 
    '''
    param='ProductionByTechnologyAnnual'
    dff = remove_unwanted_countries(df_dict[param])
    dff = dff[~dff['TECHNOLOGY'].isin(storage_techs)]
    dff = dff[dff['scenario'] == scenario]
    dff = dff[dff['TECHNOLOGY'].isin(hydrogen_technologies)]
    if countries != ['all']:
        dff = dff[dff['country'].isin(countries)]
    title = 'Hydrogen production and imports for ' + str(countries[0])
    list_to_group_by = ['YEAR', 'country','TECHNOLOGY','FUEL']
    dff = dff.groupby(list_to_group_by).sum().reset_index()
    list_to_group_by.remove('YEAR')
    list_to_group_by = [col for col in list_to_group_by if col in dff.columns]
    legend_entries = []
    for _, row in dff[list_to_group_by].iterrows():
        legend_entry = '_'.join(row.astype(str))        
        # Check if the technology is a transmission technology
        if row['TECHNOLOGY'] in get_transmission_techs(hydrogen_technologies):
            # Replace the first two characters of the fuel code with the country name and append "Imports"
            fuel_code = row['FUEL']
            country_code = fuel_code[:2]
            country_name = country_names.get(country_code)
            # Find both country codes in the technology
            technology = row['TECHNOLOGY']
            country_codes_in_tech = [code for code in country_codes if code in technology]
            # Remove the country code that matches the fuel code
            country_codes_in_tech.remove(country_code)
            # Use the remaining country code as the exporting country
            exporting_country_code = country_codes_in_tech[0] if country_codes_in_tech else country_code
            exporting_country_name = country_names.get(exporting_country_code)
            # Create the legend entry
            if row['TECHNOLOGY'] in storage_techs:
                legend_entry = country_name + 'Unloading from Storage'
            else: legend_entry = country_name + " Imports from " + exporting_country_name
        else:
            technology = row['TECHNOLOGY']
            legend_entry = cd.decode_code(technology, specifier='country') + ' ' + \
                        cd.decode_code(technology, specifier='technology') + ' ' + \
                        cd.decode_code(technology, specifier='age')      
        legend_entries.append(legend_entry)
    dff['legend'] = legend_entries
    # Negate the 'Value' if the technology includes 'FC'
    dff.loc[dff['TECHNOLOGY'].str.contains('FC'), 'VALUE'] *= -1
    # Create a column to distinguish between import and production technologies
    dff['is_import'] = dff['legend'].apply(lambda x: 'Imports from' in x)
    # Sort the DataFrame first by the 'is_import' column, and then by the 'legend'
    dff.sort_values(by=['is_import', 'legend'], inplace=True)
    write_high_res_plot(dff, title, param, '_hydrogen_'+scenario+'_'+countries[0], is_emission= False)



def create_df_imports_exports(df_dict, scenarios):
    param1 = "ProductionByTechnology"
    param2= "TotalAnnualTechnologyActivityByMode"
    df1 = df_dict[param1]
    df2 = df_dict[param2]
    df2 = df2[df2['TECHNOLOGY'].str.endswith('EH1')]
    df2.loc[:, 'FUEL'] = df2['TECHNOLOGY'].str[:3]+'1'
    cols = df2.columns.tolist()
    cols = cols[:2] + ['FUEL'] + cols[2:-1]
    df2 = df2[cols]
    df2['VALUE'] = df2['VALUE']*0.95 #to account for losses during exports
    dff = pd.concat([df1, df2], ignore_index=True)
    #removing all columns that are not imports and exports
    import_export_techs = [
    "DEELDKPH1",  # Denmark to Germany
    "DKELNLPH1",  # Denmark to The Netherlands
    "DKELPLPH1",  # Denmark to Poland (not used)
    "DKELUKPH1",  # Denmark to The UK (not used)
    "EEELFIPH1",  # Finland to Estonia
    "DEELNOPH1",  # Norway to Germany
    "NLELNOPH1",  # Norway to The Netherlands
    "NOELUKPH1",  # Norway to The UK
    "DEELSEPH1",  # Sweden to Germany
    "LTELSEPH1",  # Sweden to Lithuania
    "PLELSEPH1",  # Sweden to Poland
    "DKELDEIH1", "DKELNLIH1", "DKELPLEH1", "DKELUKIH1", "FIELEEIH1", 
    "NOELDEIH1", "NOELNLIH1", "NOELUKIH1", "SEELDEIH1", "SEELLTIH1", 
    "SEELPLEH1", "DKELDEEH1", "DKELNLEH1", "DKELPLEEH1", "DKELUKEH1", 
    "FIELEEEH1", "NOELDEEH1", "NOELNLEH1", "NOELUKEH1", "SEELDEEH1", 
    "SEELLTEH1", "SEELPLEEH1",
    "DKELNOPH1", "DKELSEPH1", "FIELSEPH1", "FIELNOPH1", "NOELSEPH1"
    ]
    dff = dff[dff['TECHNOLOGY'].isin(import_export_techs)]
    return dff

def create_import_matrix(df,scenarios, years=None):
    dff = create_df_imports_exports(df,scenarios)
    dff['from_country'] = dff.apply(
        lambda row: row['TECHNOLOGY'][4:6] if row['TECHNOLOGY'].endswith('IH1')
        else row['TECHNOLOGY'][:2] if row['TECHNOLOGY'].endswith('EH1')
        else row['TECHNOLOGY'][:2] if row['TECHNOLOGY'][:2] != row['FUEL'][:2]
        else row['TECHNOLOGY'][4:6], axis=1
    )
    dff['to_country'] = dff.apply(
        lambda row: row['TECHNOLOGY'][:2] if row['TECHNOLOGY'].endswith('IH1')
        else row['TECHNOLOGY'][4:6] if row['TECHNOLOGY'].endswith('EH1')
        else row['FUEL'][:2], axis=1
    )
    dff = dff.groupby(['YEAR','from_country', 'to_country','scenario']).sum().reset_index()
    dff = dff.drop(['REGION','TIMESLICE','TECHNOLOGY','FUEL','MODE_OF_OPERATION'], axis=1)
    if years != None:
        dff = dff[dff['YEAR'].isin(years)]
    return dff    


def plot_exports_imports(df_dict, scenarios, country):
    dff = create_df_imports_exports(df_dict, scenarios)
    dff = dff[dff['scenario'].isin(scenarios)]
    dff = dff[dff['TECHNOLOGY'].str.contains(country)]
    dff['isImport'] = dff.apply(
        lambda row: True if row['TECHNOLOGY'].endswith('IH1') else False if row['TECHNOLOGY'].endswith('EH1') else country in row['FUEL'], axis=1
    )
    dff.loc[dff['isImport'] == False, 'VALUE'] = dff.loc[dff['isImport'] == False, 'VALUE'] * -1
    dff['legend'] = dff.apply(
        lambda row: f"Imports from {row['TECHNOLOGY'][0:2]}" if row['isImport'] and country not in row['TECHNOLOGY'][0:2]
        else f"Imports from {row['TECHNOLOGY'][4:6]}" if row['isImport'] and country not in row['TECHNOLOGY'][4:6]
        else f"Exports from {row['TECHNOLOGY'][4:6]}" if not row['isImport'] and country not in row['TECHNOLOGY'][4:6]
        else f"Exports from {row['TECHNOLOGY'][0:2]}", axis=1
    )
    dff['legend'] = dff['legend'] + ' ' + dff['scenario']
    dff['legend_trimmed'] = dff['legend'].str[13:]
    dff = dff.groupby(['YEAR', 'TIMESLICE','legend_trimmed'])['VALUE'].sum().reset_index()
    #dff = dff.groupby(['YEAR', 'TIMESLICE','legend'])['VALUE'].sum().reset_index() # if you want to keep the differenciation between imports and exports
    dff['OSEMBE'] = dff['legend_trimmed'].apply(lambda x: 'OSEMBE' in x)
    dff = dff.sort_values('OSEMBE', ascending=False).drop('OSEMBE', axis=1)

    #plotting
    timeslice_mapping = dict(enumerate(dff['TIMESLICE'].astype('category').cat.categories))
    dff['TIMESLICE'] = dff['TIMESLICE'].astype('category').cat.codes  
    legends = dff['legend_trimmed'].unique()
    fig = plt.figure(figsize=(15, 10))  # Set the figure size in inches
    ax = fig.add_subplot(111, projection='3d')  # Add a 3D subplot
    proxies = []   

    colors_blue = ['navy', 'blue', 'royalblue', 'darkcyan']
    colors_red = ['darkred', 'red', 'salmon', 'coral', 'mistyrose']

    groups = dff.groupby(dff['legend_trimmed'].str[:2])

    for group_name, group_df in groups:
        fig = plt.figure(figsize=(20, 10))
        ax = fig.add_subplot(111, projection='3d')

        legends = group_df['legend_trimmed'].unique()

        for i, legend in enumerate(legends):
            df_legend = dff[dff['legend_trimmed'] == legend]
            timeslices = df_legend['TIMESLICE'].unique()
            
            for timeslice in timeslices:
                df_timeslice = df_legend[df_legend['TIMESLICE'] == timeslice]
                df_timeslice = df_timeslice.sort_values('YEAR')
                Y = df_timeslice['YEAR']
                X = df_timeslice['TIMESLICE']
                #X = np.full_like(Y, timeslice)
                Z = df_timeslice['VALUE']            
                # Choose the color based on the index of the legend
                color = colors_red[i % len(colors_red)] if 'OSeMBE' in legend else colors_blue[i % len(colors_blue)]
                ax.plot(X, Y, Z, color=color)
            
            # Create a proxy artist for the legend
            proxy = mpl.lines.Line2D([0], [0], color=color, lw=2, label=legend)
            proxies.append(proxy)

        ax.set_xlabel('TIMESLICE', labelpad=20, fontsize=16)
        ax.set_ylabel('YEAR', labelpad=10, fontsize=16)
        ax.set_zlabel('Imports(+)/Exports(-) in PJ', labelpad=10, fontsize=16)
        ax.tick_params(axis='y', labelsize=8)  # Set y-axis label size to 8
        ax.set_box_aspect([10, 4, 4])
        ax.view_init(elev=8, azim=-80)
        ax.set_xticks(np.arange(len(timeslice_mapping)))  # Set x-ticks at the positions of the timeslices
        ax.set_xticklabels(timeslice_mapping.values())  # Set x-tick labels to the original string values
        ax.legend(handles=proxies)
        ax.legend(handles=proxies, bbox_to_anchor=(1, 0.85), loc='upper right')
        plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
        proxies = []

        fig.savefig('temp/temp.png', dpi=300)
        img = Image.open('temp/temp.png')
        crop_area = (1500, 400, 4700, 2300)
        img_cropped = img.crop(crop_area)
        img_cropped.save(f'visualisations/exports_imports_{country}_{group_name}.png')
        os.remove('temp/temp.png')
        mpl.pyplot.close(fig)


def plot_hydrogen_timesliced(df_dict, scenario , country):
    param  = "ProductionByTechnology"
    dff = remove_unwanted_countries(df_dict[param])
    dff = dff[dff['scenario'] == scenario]
    dff = dff[dff['TECHNOLOGY'].isin(hydrogen_technologies)]
    dff = dff[dff['country'].isin([country])]
    # Create a column 'legend'
    dff['legend'] = dff['TECHNOLOGY'].apply(lambda x: cd.decode_code(x, specifier='technology') + ' ' + cd.decode_code(x, specifier='age'))
    #plotting
    timeslice_mapping = dict(enumerate(dff['TIMESLICE'].astype('category').cat.categories))
    dff['TIMESLICE'] = dff['TIMESLICE'].astype('category').cat.codes  
    legends = dff['legend'].unique()
    fig = plt.figure(figsize=(15, 10))  # Set the figure size in inches
    ax = fig.add_subplot(111, projection='3d')  # Add a 3D subplot
    proxies = []   
    colors_blue = ['navy', 'blue', 'royalblue', 'darkcyan']
    colors_red = ['darkred', 'red', 'salmon', 'coral', 'mistyrose']
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111, projection='3d')

    for i, legend in enumerate(legends):
        df_legend = dff[dff['legend'] == legend]
        timeslices = df_legend['TIMESLICE'].unique()        
        for timeslice in timeslices:
            df_timeslice = df_legend[df_legend['TIMESLICE'] == timeslice]
            df_timeslice = df_timeslice.sort_values('YEAR')
            Y = df_timeslice['YEAR']
            X = df_timeslice['TIMESLICE']
            #X = np.full_like(Y, timeslice)
            Z = df_timeslice['VALUE']            
            # Choose the color based on the index of the legend
            color = colors_red[i % len(colors_red)] if 'OSEMBE' in legend else colors_blue[i % len(colors_blue)]
            ax.plot(X, Y, Z, color=color)        
        # Create a proxy artist for the legend
        proxy = mpl.lines.Line2D([0], [0], color=color, lw=2, label=legend)
        proxies.append(proxy)
        
    ax.set_xlabel('TIMESLICE', labelpad=20, fontsize=16)
    ax.set_ylabel('YEAR', labelpad=10, fontsize=16)
    ax.set_zlabel('Hydrogen production in PJ', labelpad=10, fontsize=16)
    ax.tick_params(axis='y', labelsize=8)  # Set y-axis label size to 8
    ax.set_box_aspect([10, 4, 4])
    ax.view_init(elev=8, azim=-80)
    ax.set_xticks(np.arange(len(timeslice_mapping)))  # Set x-ticks at the positions of the timeslices
    ax.set_xticklabels(timeslice_mapping.values())  # Set x-tick labels to the original string values
    ax.legend(handles=proxies)
    ax.legend(handles=proxies, bbox_to_anchor=(1, 0.85), loc='upper right')
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)

    fig.savefig('temp/temp.png', dpi=300)
    img = Image.open('temp/temp.png')
    crop_area = (1500, 400, 4700, 2300)
    img_cropped = img.crop(crop_area)
    img_cropped.save(f'visualisations/hydrogen_timesliced_{country}.png')
    os.remove('temp/temp.png')
    mpl.pyplot.close(fig)

def plot_chord_diagram(dff, scenario, year):
    df = dff[dff['YEAR'] == year]
    df = df[df['scenario'] == scenario]
    df = df.rename(columns={'from_country': 'source'})
    df['source'] = df['source'].apply(lambda x: cd.country_codes.get(x))
    df = df.rename(columns={'to_country': 'target'})
    df['target'] = df['target'].apply(lambda x: cd.country_codes.get(x))
    df = df.rename(columns={'VALUE': 'weight'})
    df = df.drop(['YEAR', 'scenario'], axis=1).reset_index(drop=True)
    df = df.sort_values(by=['source', 'target'])
    #Plot
    d3 = D3Blocks(chart='Chord', frame=False) 
    cmap = 'tab20c' 
    colors = ['#3182bd', '#e6550d', '#31a354', '#756bb1', '#636363', '#9ecae1', '#fdae6b', '#a1d99b', '#bcbddc', '#bdbdbd']
    unique_values = pd.concat([dff['from_country'], dff['to_country']]).unique()
    mapped_values = list(map(lambda x: cd.country_codes.get(x), unique_values))
    color_dict = {country: colors[i % len(colors)] for i, country in enumerate(mapped_values)}
    d3.set_node_properties(df, cmap=cmap)
    d3.set_edge_properties(df, color='source', opacity='source')
    #iterate through all edges and set the color
    unique_values_df = pd.concat([df['target'], df['source']]).unique().tolist()
    for value in unique_values_df:
        color = color_dict.get(value)
        d3.node_properties.get(value)['color'] = color
    d3.chord(df, title = scenario + ' ' + str(year),fontsize=20, filepath = f'visualisations/chord_diagram_{scenario}_{year}.html', reset_properties = False)

    # Plot using holoviews
    # hv.extension('bokeh')
    # data = hv.Dataset(df, ['source', 'target'], 'weight')
    # # Create the chord diagram
    # chord = hv.Chord(data)
    # labels = hv.Labels(data, ['source', 'target'], 'weight')
    # plot = chord * labels
    # plot.opts(
    #     opts.Chord(cmap='Category10', edge_cmap='Category10', edge_color=dim('source').str(), 
    #                labels='name', node_color=dim('index').str()),
    #     opts.Labels(text_color='white')
    # )
    # bk.show(hv.render(plot))





def run():
    scenarios = ['OSeMBE', 'Nordic_no_h2','Nordic','Nordic_co2_limit','Nordic_em_free']
    #scenarios = ['Nordic_emission_limit']
    df_dict = create_df_dict(scenarios)
    ccs_tech = ['BMCSPN2','COCSPN2','NGCSPN2','HGSCPN2','HGBCPN2']
    bm_tech = ['BMCCPH1', 'BMCHPH3','BMSTPH3']
    css_techs = []
    bm_techs = []
    for country_code in ['SE', 'NO', 'FI', 'DK']:
        for tech in ccs_tech:
            css_techs.append(country_code + tech)
        for tech in bm_tech:
            bm_techs.append(country_code + tech)

    d1 = create_import_matrix(df_dict, scenarios)
    for scenario in scenarios:
        plot_chord_diagram(d1, scenario, 2060)


    #for country_code in ['SE', 'NO', 'FI', 'DK']:
    #     #plot_annual_sum_advanced(df_dict,'ProductionByTechnologyAnnual', scenarios = 'WP1_NetZero', countries = [country_names[country_code]], technologies = css_techs, split_countries = True, split_techs = True)
    #     #plot_annual_sum_advanced(df_dict,'ProductionByTechnologyAnnual', scenarios = 'WP1_NetZero', countries = ['all'], technologies = bm_techs, split_countries = True, split_techs = True)
    #    plot_hydrogen_timesliced(df_dict, 'WP1_NetZero', country_names[country_code])

    #plot_annual_sum_by_scenario(df_dict, 'StorageNetCharge', list_to_group_by = ['YEAR', 'scenario', 'STORAGE'])
    #Plot annual sum of parameters for each scenario
    #for param in ['AccumulatedNewCapacity','NewCapacity','AnnualFixedOperatingCost','AnnualVariableOperatingCost','CapitalInvestment','DiscountedSalvageValue', 'DiscountedTechnologyEmissionsPenalty','TotalCapacityAnnual']:
    #    plot_annual_sum_by_scenario(df_dict, param)
    #Plot annual sum of parameters for each country
    # plot_annual_sum_advanced(df_dict,'ProductionByTechnologyAnnual', scenarios = 'WP1_NetZero', countries = ['all'], technologies = get_production_techs(hydrogen_technologies), split_countries = True, split_techs = True)
    # plot_annual_sum_advanced(df_dict,'ProductionByTechnologyAnnual', scenarios = 'WP1_NetZero', countries = ['all'], technologies = get_transmission_techs(hydrogen_technologies), split_countries = True, split_techs = True)
    #plot_hydrogen(df_dict, scenarios[0], countries = ['all'])
    #plot_hydrogen(df_dict, 'WP1_NetZero_without_storage', countries = ['all'])
    #plot_emissions(df_dict, 'AnnualEmissions', scenarios = 'all', emissions = ['CO2','PM25'], sum_emissions = True)
    #plot_annual_sum_by_scenario(df_dict, 'TotalDiscountedCost', list_to_group_by = ['YEAR', 'scenario'])
    #Plot electricity generation for all scenarios in one stacked bar graph for each country
    #for selec_region in ['SE', 'NO', 'FI', 'DK']:
         #electricity_generation_plot.main(selec_region, scenarios, temp = True, years = [2015,2030,2050,2060])
    #    plot_hydrogen(df_dict, 'WP1_NetZero', countries = [country_names[selec_region]])
    #    plot_exports_imports(df_dict, scenarios, selec_region)
    
#for the capacity visualisation, the import and export capacities need to be excluded so that it makes sense
run()
        

# -*- coding: utf-8 -*-
"""From OSEMBE
Created on Fri Sep 25 14:51:38 2020

@author: haukeh
modified by Timon Renzelmann
It can work with the new import and export techs for electricity ending on EH1 and IH1
Maybe add 'All countries' as an option for the main function to create a figure for all countries
"""
# Import of required packages
import numpy as np
import pandas as pd
import os
import sys
import plotly.graph_objs as go
from plotly.offline import plot
import plotly.io as pio


#result_folder = 'results_csv_OSeMBE'
result_folder = 'results'

# Function to read results csv files
def read_csv(scen, param):
    """
    Read a CSV file based on the scenario and parameter.

    Args:
        scen (str): The scenario name.
        param (str): The parameter name.

    Returns:
        pd.DataFrame: The DataFrame containing the CSV data.
    """
    df = pd.read_csv(result_folder+'\\{}\\results_csv\\{}.csv'.format(scen,param))
    df['pathway'] = scen
    df2 = pd.read_csv(result_folder+'\\{}\\results_csv\\TotalTechnologyAnnualActivity.csv'.format(scen))
    df2['pathway'] = scen
    df2 = df2[df2['TECHNOLOGY'].str.endswith('EH1')]
    # Create new column 'FUEL' with first 4 digits of 'technology' column
    df2['FUEL'] = df2['TECHNOLOGY'].str[:3]+'1'
    # Rearrange columns to place 'FUEL' at 3rd position
    cols = df2.columns.tolist()
    cols = cols[:2] + ['FUEL'] + cols[2:-1]
    df2 = df2[cols]
    df2['VALUE'] = df2['VALUE']*0.95 #correct for losses from Activity to actual Exports
    df = pd.concat([df, df2], ignore_index=True)
    return df

# Function to create dictionaries containing dictionaries for each scenario that contain the results as dataframes
def build_dic(scen, params):
    """
    Build a dictionary of dictionaries containing DataFrames for each scenario and parameter.

    Args:
        scen (list): List of scenario names.
        params (list): List of parameter names.

    Returns:
        dict: A nested dictionary containing DataFrames.
    """
    dic = {}
    for s in scen:
        dic[s] = {}
    for s in scen:
        for param in params:
            dic[s][param] = read_csv(s, param)
    return dic

# Function to create a DataFrame with the production by technology annual
def build_PbTA_df(dic,params,years=[2015,2020,2030,2040,2050]):
    """
    Build a DataFrame with production by technology annually.

    Args:
        dic (dict): Dictionary containing DataFrames.

    Returns:
        pd.DataFrame: The resulting DataFrame.
    """
    df = pd.DataFrame(columns=['REGION', 'TECHNOLOGY', 'FUEL', 'YEAR', 'VALUE', 'pathway'])
    for i in dic:
        df_work = dic[i][params]
        df = df.dropna(axis=1, how='all')
        df = pd.concat([df, df_work])
    df['region'] = df['TECHNOLOGY'].apply(lambda x: x[:2])
    df['fuel'] = df['TECHNOLOGY'].apply(lambda x: x[2:4])
    df['tech_type'] = df['TECHNOLOGY'].apply(lambda x: x[4:6])
    df['tech_spec'] = df['TECHNOLOGY'].apply(lambda x: x[2:])
    df = df[(df['fuel'] != 'OI')
            & (df['tech_type'] != '00')
            & (df['YEAR'].isin(years))]
    df['unit'] = 'PJ'
    return df

# Function to create a dictionary with information
def get_facts(df):
    """
    Get facts from the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame.

    Returns:
        dict: A dictionary containing facts.
    """
    facts_dic = {}
    facts_dic['pathways'] = df.loc[:, 'pathway'].unique()
    facts_dic['regions'] = df.loc[:, 'region'].unique()
    facts_dic['unit'] = df.loc[:, 'unit'].unique()
    facts_dic['regions'] = np.append(facts_dic['regions'], 'EU28')
    return facts_dic

# Dictionary of dictionaries with colour schemes
colour_schemes = dict(
    dES_colours = dict(
        Coal = 'rgb(0, 0, 0)',
        Oil = 'rgb(121, 43, 41)',
        Gas = 'rgb(86, 108, 140)',
        Nuclear = 'rgb(186, 28, 175)',
        Waste = 'rgb(138, 171, 71)',
        Biomass = 'rgb(172, 199, 119)',
        Biofuel = 'rgb(79, 98, 40)',
        Hydro = 'rgb(0, 139, 188)',
        Wind = 'rgb(143, 119, 173)',
        Solar = 'rgb(230, 175, 0)',
        Geo = 'rgb(192, 80, 77)',
        Ocean ='rgb(22, 54, 92)',
        Imports = 'rgb(232, 133, 2)',
        Hydrogen = 'rgb(152,245,255)'),
    TIMES_PanEU_colours = dict(
        Coal = 'rgb(0, 0, 0)',
        Oil = 'rgb(202, 171, 169)',
        Gas = 'rgb(102, 77, 142)',
        Nuclear = 'rgb(109, 109, 109)',
        Waste = 'rgb(223, 134, 192)',
        Biomass = 'rgb(80, 112, 45)',
        Biofuel = 'rgb(178, 191, 225)',
        Hydro = 'rgb(181, 192, 224)',
        Wind = 'rgb(103, 154, 181)',
        Solar = 'rgb(210, 136, 63)',
        Geo = 'rgb(178, 191, 225)',
        Ocean ='rgb(178, 191, 225)',
        Imports = 'rgb(232, 133, 2)')
    )

# Functions for returning positives and negatives
def positives(value):
    return max(value, 0)

def negatives(value):
    return min(value, 0)

# Function to create dfs with import and export of electricity for the selected country
def impex(data, paths, selected_country):
    """
    Create DataFrames with import and export of electricity for the selected country.
    Args:
        data (pd.DataFrame): The input DataFrame.
        paths (list): List of scenario names.
        selected_country (str): The selected country code.

    Returns:
        pd.DataFrame: DataFrames for imports and exports.
    """
    df_filtered = data[(data['fuel']=='EL')
                       &((data['region']==selected_country)|(data['tech_type']==selected_country))
                       &(data['tech_type']!='00')]
    countries = []
    countries = list(df_filtered['region'].unique())
    countries.extend(df_filtered['tech_type'].unique())
    countries = list(dict.fromkeys(countries))
    df_filtered = df_filtered[df_filtered['FUEL'].str.contains('|'.join(countries))]
    df_filtered = df_filtered[df_filtered['FUEL'].str.contains('E1')]
    years = pd.Series(df_filtered['YEAR'].unique(),name='YEAR').sort_values()
    #paths = list(path_names.keys())
    neighbours = []
    for i in countries:
        if i != selected_country:
            neighbours.append(i)
    dict_path = {}
    links = list(df_filtered['TECHNOLOGY'].unique())
    for j in paths:
        net_imp = pd.DataFrame(index=years)
        for link in links:
            if (link.endswith('PH1')):
                imp = df_filtered[(df_filtered['pathway']==j)
                                &(df_filtered['TECHNOLOGY']==link)
                                &(df_filtered['FUEL']==(selected_country+'E1'))]
                if len(imp.index)<5:
                    imp = imp.set_index('YEAR').reindex(years).reset_index().fillna(0)
                imp = imp.set_index(years)
                f = selected_country
                for neighbour in neighbours:
                    if neighbour in link:
                        f = neighbour                        
                exp = df_filtered[(df_filtered['pathway']==j)
                                &(df_filtered['TECHNOLOGY']==link)
                                &(df_filtered['FUEL']==(f+'E1'))]
                if len(exp.index)<5:
                    exp = exp.set_index('YEAR').reindex(years).reset_index().fillna(0)
                exp = exp.set_index(years) 
                net_imp[link] = imp['VALUE'] - exp['VALUE']
            elif (link.endswith('IH1')):
                imp = df_filtered[(df_filtered['pathway']==j)
                                &(df_filtered['TECHNOLOGY']==link)
                                &(df_filtered['FUEL']==(selected_country+'E1'))]
                if len(imp.index)<5:
                    imp = imp.set_index('YEAR').reindex(years).reset_index().fillna(0)
                imp = imp.set_index(years)
                net_imp[link] = imp['VALUE']
            elif (link.endswith('EH1')):
                exp = df_filtered[(df_filtered['pathway']==j)
                                &(df_filtered['TECHNOLOGY']==link)
                                &(df_filtered['FUEL']==(selected_country+'E1'))]
                if len(exp.index)<5:
                    exp = exp.set_index('YEAR').reindex(years).reset_index().fillna(0)
                exp = exp.set_index(years) 
                net_imp[link] = -exp['VALUE']
        net_imp_final = pd.DataFrame()
        # Get unique first 6 characters of column names
        unique_prefixes = set(col[:6] for col in net_imp.columns)
        # For each unique prefix, add together all columns that start with it
        for prefix in unique_prefixes:
            matching_columns = [col for col in net_imp.columns if col.startswith(prefix)]
            net_imp_final[prefix] = net_imp[matching_columns].sum(axis=1)                   
        net_imp = net_imp_final
        net_imp_pos = pd.DataFrame(index=years,columns=net_imp.columns)
        net_imp_neg = pd.DataFrame(index=years,columns=net_imp.columns)
        for column in net_imp.columns:
            net_imp_pos[column] = net_imp[column].map(positives)
            net_imp_neg[column] = net_imp[column].map(negatives)
        
        label_imp = []
        label_exp = []
        for n in net_imp.columns:
            if(n[:2]==selected_country):
                label_imp.append('Import from '+n[4:6])
                label_exp.append('Export to '+n[4:6])
            else:
                label_imp.append('Import from '+n[:2])
                label_exp.append('Export to '+n[:2])
        net_imp_pos.columns = label_imp
        net_imp_neg.columns = label_exp
        dict_path[j] = {}
        dict_path[j]['imports']=net_imp_pos
        dict_path[j]['exports']=net_imp_neg
    path_ind = []
    df_exports = pd.DataFrame(columns=label_exp)
    df_imports = pd.DataFrame(columns=label_imp)
    for year in years:
        df_exports = df_exports.dropna(axis=1, how='all')
        df_imports = df_imports.dropna(axis=1, how='all')
        for i, j in enumerate(paths):
            df_exports = pd.concat([df_exports, dict_path[j]['exports'].loc[[year]]])
            df_imports = pd.concat([df_imports, dict_path[j]['imports'].loc[[year]]])
            path_ind.append(j.upper())
    df_exports = df_exports.set_index([pd.Index(path_ind, name='paths')],append=True)
    df_imports = df_imports.set_index([pd.Index(path_ind, name='paths')],append=True)
    df_exports = df_exports.T.groupby(level=0).sum().T
    df_imports = df_imports.T.groupby(level=0).sum().T
    print(selected_country +' Exports:')
    print(df_exports) 
    print(selected_country + ' Imports:')
    print(df_imports)  
    return df_exports, df_imports


# Function to create a figure
def create_fig(data, paths, country_sel, countries_mod, fuels, colours):
    """
    Create a figure using Plotly. Adjust values here for layout changes.

    Args:
        data (pd.DataFrame): The input DataFrame.
        paths (list): List of scenario names.
        country_sel (str): The selected country code.
        countries_mod (dict): Dictionary of country codes and names.
        fuels (pd.DataFrame): DataFrame with fuel names.
        colours (dict): Dictionary of color schemes.

    Returns:
        go.Figure: The Plotly figure.
    """
    fig = go.Figure()
    elexp, elimp = impex(data, paths, country_sel)
    elexp = elexp.sum(axis=1)
    elimp = elimp.sum(axis=1)
    #paths = list(path_names.keys())
    years = data['YEAR'].unique()
    years.sort()
    coms = fuels['fuel_name']
    coms = coms[(coms!='EL')&(coms!='OI')]
    info_dict = {}
    info_dict['Unit'] = data.loc[:,'unit'].unique()
    info_dict['Y-Axis'] = ['{}'.format(*info_dict['Unit'])]
    countr_el1 = country_sel + 'E1'
    countr_el2 = country_sel + 'E2'
    dict_path = {}
    for path in paths:
        filtered_df = data[
        (data['pathway'] == path) 
        & (data['region'] == country_sel) 
        & ((data['FUEL']==countr_el1)|(data['FUEL']==countr_el2)) 
        & (data['fuel']!='EL') 
        & (data['tech_type']!='00')]
        filtered_df_p = filtered_df.pivot(index='YEAR', columns='tech_spec',  values='VALUE')
        df_by_com = pd.DataFrame()
        for com in coms:
            com_selec = filtered_df_p.filter(regex=r"\A"+com, axis=1)
            com_sum = com_selec.sum(axis=1)
            df_by_com[com] = com_sum
        dict_path[path] = df_by_com
    df_fig = pd.DataFrame(columns=coms)
    path_ind = []
    year_ind = []
    for y in years:
        i = 0
        for p in paths:
            # Drop columns that are all NA
            df_fig = df_fig.dropna(how='all', axis=1)
            dict_path[p] = dict_path[p].dropna(how='all', axis=1)

            df_fig = pd.concat([df_fig, dict_path[p].loc[[y]]])
            path_ind.append(paths[i]) #add .upper() to make all caps
            year_ind.append(y)
            i +=1
    df_fig = df_fig.set_index([pd.Index(path_ind, name='paths')],append=True)
    df_fig['EL'] = elimp
    coms = pd.concat([coms, pd.Series(['EL'])])
    for c in coms:
        temp = fuels.loc[fuels['fuel_name']==c,'fuel_abr']
        fuel_code = temp.iloc[0]
        fig.add_trace(go.Bar(
            y = df_fig.loc[:,c],
            x = [year_ind,path_ind],
            name = fuel_code,
            hovertemplate = 'Power generation: %{y}PJ',
            marker_color = colours[fuel_code]
            ))
    fig.add_trace(go.Bar(
    y = elexp,
    x = [year_ind,path_ind],
    name = 'Exports',
    hovertemplate = 'Exported electricity: %{y}PJ',
    marker_color = colours['Imports'],
    base=0
    ))
    # change layout of the figure
    fig.update_layout(
        barmode = 'stack',
        plot_bgcolor='rgba(0,0,0,0)',
        title={
            'text':'<b>Electricity generation in {}</b>'.format(countries_mod[country_sel]),
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis = {'type': 'multicategory'},
        yaxis = dict(title='Electricity in {}'.format(info_dict['Y-Axis'][0])),
        font_family = "Arial",
        font_color = "black",
        title_font_size = 32,
        legend_font_size = 26
        )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='Black',title_font_size=26, tickfont_size=22)
    fig.update_xaxes(tickfont_size=22)
    return fig

# Main function to execute the script
def main(country, scenarios, temp = False, years=[2015,2020,2030,2040,2050]):
    """
    Main function to execute the script.

    Args:
        country (str): The selected country code.

    Returns:
        None
    """
    params = 'ProductionByTechnologyAnnual' #change parameter if desired (might not work though)
    results_dic = build_dic(scenarios, [params])  
    df_PbTA = build_PbTA_df(results_dic,params,years = years)
    #facts_dic = get_facts(df_PbTA)
    countries_mod = {'AT':'Austria','BE':'Belgium','BG':'Bulgaria','CH':'Switzerland','CY':'Cyrpus','CZ':'Czech Republic','DE':'Germany','DK':'Denmark','EE':'Estonia','ES':'Spain','FI':'Finland','FR':'France','GR':'Greece','HR':'Croatia','HU':'Hungary','IE':'Ireland','IT':'Italy','LT':'Lithuania','LU':'Luxembourg','LV':'Latvia','MT':'Malta','NL':'Netherlands','NO':'Norway','PL':'Poland','PT':'Portugal','RO':'Romania','SE':'Sweden','SI':'Slovenia','SK':'Slovakia','UK':'United Kingdom','EU28':'EU28'}
    fuels = pd.DataFrame({'fuel_name':['WI','HY','BF','CO','BM','WS','HF','NU','NG','OC','OI','GO','SO','EL','HG'],'fuel_abr':['Wind','Hydro','Biofuel','Coal','Biomass','Waste','Oil','Nuclear','Gas','Ocean','Oil','Geo','Solar','Imports','Hydrogen']}, columns = ['fuel_name','fuel_abr'])
    fuels = fuels.sort_values(['fuel_name'])
    #for region in facts_dic['regions']:
        #print(region)
    #selec_region = input('Please select a country from the above listed by typing here:')
    #selec_region = 'DE'
    #print(list(colour_schemes.keys()))
    # selec_scheme = input('Please select one of the above listed colour schemes by writing it here and confirming by enter:')
    selec_scheme = 'dES_colours' 
    colours = colour_schemes[selec_scheme]
    i = 1
    while os.path.exists('visualisations\\elec_gen_{}{}.png'.format(country, '' if i == 1 else f'({i})')):
        i += 1

    figure = create_fig(df_PbTA, scenarios, country, countries_mod, fuels, colours)
    filename = 'visualisations\\elec_gen_{}{}.png'.format(country, '' if i == 1 else f'({i})')
    pio.write_image(figure, filename, width=1200, height=1000, scale=2)
    if temp: 
        plot(figure) #activate this to get closer insights into numbers and hover over the figure

#If executed as script
# if __name__ == '__main__':
#     selec_region = 'NO'  # Replace with your desired country code
#     scenarios = ['WP1_NetZero']
#     main(selec_region, scenarios)

# selec_region = 'NO'  # Replace with your desired country code
# scenarios = ['WP1_NetZero','OSEMBE']
# main(selec_region, scenarios)
# print(selec_region+' done')
# selec_region = 'SE'  # Replace with your desired country code
# scenarios = ['WP1_NetZero','OSEMBE']
# main(selec_region, scenarios)
# print(selec_region+' done')
# selec_region = 'DK'  # Replace with your desired country code
# scenarios = ['WP1_NetZero','OSEMBE']
# main(selec_region, scenarios)
# print(selec_region+' done')
# selec_region = 'FI'  # Replace with your desired country code
# scenarios = ['WP1_NetZero','OSEMBE']
# main(selec_region, scenarios)
# print(selec_region+' done')

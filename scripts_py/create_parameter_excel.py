'''
Making it easier to create and populate the parameter excel file for the GSA.
Hard coded for the H2 project.
The excel file is translated into a csv file used by the GSA analysis in the script refresh_config.py (in the scripts_smk folder).

@author: Timon Renzelmann
'''

import pandas as pd
import numpy as np
import os

countries = ['DK','FI','NO','SE']
h2_techs_standard = ['HGSRPN2','HGBGPN2','HGECPN2','HGBCPN2','HGSCPN2'] #group code will be the 3rd and 4th digit
fuel_cells = ['HGFCPN2']
storage = ['HGSTPN2']
renewables = ['BFHPFH1','BMCCPH1','BMCHPH3','BMSTPH3','HYDMPH0','HYDMPH1','HYDMPH2','HYDMPH3','SODIFH1','SOUTPH2','WIOFPH3','WIOFPN2','WIOFPN3','WIONPH3'] #ex geothermal
fossils_new = ['HFGCPN3','NGCHPN3','NGGCPN2'] # add other fossil fuels or modify overleaf file
ccs_bm = ['BMCSPN2']
ccs_fossil = ['NGCSPN2','COCSPN2']

values_to_delete = {
    }

def load_input_params_baseline(folder_path):
    dfs = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            base_name = os.path.splitext(file_name)[0]
            df = pd.read_csv(os.path.join(folder_path, file_name))
            dfs[base_name] = df
    return dfs

def get_baseline_value(input_params, key, key_values):
    # Get the DataFrame for the key
    df = input_params[key]
    # Initialize a mask with all True values
    mask = pd.Series([True] * len(df))
    # Update the mask for each key-value pair
    for k, v in key_values:
        mask = mask & (df[k] == v)
    # Check the number of matches
    matches = df.loc[mask, 'VALUE'].values
    if len(matches) == 0:
        #print(f"No matches found for {key_values} in {key}")    
        second_elements = [t[1] for t in key_values if t[1] not in [2015, 2060]]
        if key not in values_to_delete:
            values_to_delete[key] = []
        if second_elements not in values_to_delete[key]:
            values_to_delete[key].append(second_elements)          
        return 0
    elif len(matches) > 1:
        raise ValueError("Multiple matches found for" + str(key_values) + " : " + str(matches))
    # Return the value from the 'VALUE' column that matches the mask
    return matches[0]

def create_df():
    data = {
        'name': [],
        'group': [],
        'indexes': [],
        'min_value_base_year': [],
        'max_value_base_year': [],
        'min_value_end_year': [],
        'max_value_end_year': [],
        'dist': [],
        'interpolation_index': [],
        'action': []
    }
    return pd.DataFrame(data)

def create_new_row(name, group, indexes, dist, interpolation_index, action, values=None):
    if values is not None and len(values) != 4:
        raise ValueError("values must be either None or a list of length 4")
    values = values if values is not None else ['','','','']
    return pd.DataFrame({'name': [name], 
                         'group': [group], 
                         'indexes': [indexes], 
                         'min_value_base_year': values[0], 
                         'max_value_base_year': values[1], 
                         'min_value_end_year': values[2], 
                         'max_value_end_year': values[3], 
                         'dist': [dist], 
                         'interpolation_index': [interpolation_index], 
                         'action': [action]})

def add_demand(df, input_params):
    fixed_values = [(249, 518), (506, 668), (692, 895), (430, 1080)]
    h2_fixed_values = [(54, 428), (36, 540), (54, 270), (50, 320)]
    values_dict = {}
    h2_values_dict = {}
    for country, values, h2_values in zip(countries, fixed_values, h2_fixed_values):
        values_dict[country] = [
            get_baseline_value(input_params, 'SpecifiedAnnualDemand', [('FUEL', f'{country}E2'), ('YEAR', 2015)]),
            get_baseline_value(input_params, 'SpecifiedAnnualDemand', [('FUEL', f'{country}E2'), ('YEAR', 2015)]),
            *values
        ]
        h2_values_dict[country] = [
            get_baseline_value(input_params, 'AccumulatedAnnualDemand', [('FUEL', f'{country}H2'), ('YEAR', 2015)]),
            get_baseline_value(input_params, 'AccumulatedAnnualDemand', [('FUEL', f'{country}H2'), ('YEAR', 2015)]),
            *h2_values
        ]
    for country in countries:
        values = values_dict[country]
        h2_values = h2_values_dict[country]
        new_row = create_new_row('AccumulatedAnnualDemand', 'demand_h2', f'REGION1,{country}H2', 'unif', 'YEAR', 'interpolate', h2_values)
        df = pd.concat([df, new_row], ignore_index=True)
        new_row = create_new_row('SpecifiedAnnualDemand', 'demand_el', f'REGION1,{country}E2', 'unif', 'YEAR', 'interpolate', values)
        df = pd.concat([df, new_row], ignore_index=True)
    return df

def add_em_penalty(df):
    values = [0,0.05,0.05,0.15]
    new_row = create_new_row('EmissionsPenalty', 'em_penalty', 'REGION1,CO2', 'unif', 'YEAR', 'interpolate',values)
    df = pd.concat([df, new_row], ignore_index=True)
    return df

def add_cost(df, input_params):
    for cost in ['CapitalCost','FixedCost','VariableCost']:
        for country in countries:
            for h2_tech in h2_techs_standard:
                if h2_tech == 'HGBCPN2' or h2_tech == 'HGSCPN2':
                    code= f'ccs_{h2_tech[2:4]}'
                    if h2_tech == 'HGBCPN2':
                        share = 0.15
                    else:
                        share = 0.1
                else:
                    code = h2_tech[2:4]
                    if h2_tech == 'HGSRPN2':
                        share = 0.05
                    else:
                        share = 0.1
                        fuel = 'E1'
                index = f'REGION1,{country}{h2_tech}'
                if cost == 'VariableCost':
                    index += ',1'
                values = [get_baseline_value(input_params, cost, [('TECHNOLOGY', country + h2_tech), ('YEAR', 2015)]),
                          get_baseline_value(input_params, cost, [('TECHNOLOGY', country + h2_tech), ('YEAR', 2015)]),
                          get_baseline_value(input_params, cost, [('TECHNOLOGY', country + h2_tech), ('YEAR', 2060)])*(1-share),
                          get_baseline_value(input_params, cost, [('TECHNOLOGY', country + h2_tech), ('YEAR', 2060)])*(1+share)
                          ]
                new_row = create_new_row(cost, 'cost_h2_'+code, index, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for fuel_cell in fuel_cells:
                index = f'REGION1,{country}{fuel_cell}'
                if cost == 'VariableCost':
                    index += ',1'
                values = [get_baseline_value(input_params, cost, [('TECHNOLOGY', country + fuel_cell), ('YEAR', 2015)]),
                          get_baseline_value(input_params, cost, [('TECHNOLOGY', country + fuel_cell), ('YEAR', 2015)]),
                          get_baseline_value(input_params, cost, [('TECHNOLOGY', country + fuel_cell), ('YEAR', 2060)])*0.9,
                          get_baseline_value(input_params, cost, [('TECHNOLOGY', country + fuel_cell), ('YEAR', 2060)])*1.1
                          ]
                new_row = create_new_row(cost, f'cost_h2_{fuel_cell[2:4]}', index, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for renew in renewables:
                index = f'REGION1,{country}{renew}'
                if cost == 'VariableCost':
                    index += ',1'
                values = [get_baseline_value(input_params, cost, [('TECHNOLOGY', country + renew), ('YEAR', 2015)]),
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + renew), ('YEAR', 2015)]),
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + renew), ('YEAR', 2060)])*0.9,
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + renew), ('YEAR', 2060)])*1.1
                            ]
                new_row = create_new_row(cost, f'cost_renew', index, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for fossil in fossils_new:
                index = f'REGION1,{country}{fossil}'
                if cost == 'VariableCost':
                    index += ',1'
                values = [get_baseline_value(input_params, cost, [('TECHNOLOGY', country + fossil), ('YEAR', 2015)]),
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + fossil), ('YEAR', 2015)]),
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + fossil), ('YEAR', 2060)])*0.95,
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + fossil), ('YEAR', 2060)])*1.05
                            ]
                new_row = create_new_row(cost, f'cost_fossil', index, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for ccs in ccs_bm:
                index = f'REGION1,{country}{ccs}'
                if cost == 'VariableCost':
                    index += ',1'
                values = [get_baseline_value(input_params, cost, [('TECHNOLOGY', country + ccs), ('YEAR', 2015)]),
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + ccs), ('YEAR', 2015)]),
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + ccs), ('YEAR', 2060)])*0.85,
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + ccs), ('YEAR', 2060)])*1.15
                            ]
                new_row = create_new_row(cost, f'cost_ccs_biomass', index, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for ccs in ccs_fossil:
                index = f'REGION1,{country}{ccs}'
                if cost == 'VariableCost':
                    index += ',1'
                    values = [get_baseline_value(input_params, cost, [('TECHNOLOGY', country + ccs), ('YEAR', 2015)]),
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + ccs), ('YEAR', 2015)]),
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + ccs), ('YEAR', 2060)])*0.9,
                            get_baseline_value(input_params, cost, [('TECHNOLOGY', country + ccs), ('YEAR', 2060)])*1.1
                            ]
                new_row = create_new_row(cost, f'cost_ccs_fossil', index, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
    for country in countries:
        values = [get_baseline_value(input_params, 'CapitalCostStorage', [('STORAGE', f'{country}HGSTPN2'), ('YEAR', 2015)]),
                    get_baseline_value(input_params, 'CapitalCostStorage', [('STORAGE', f'{country}HGSTPN2'), ('YEAR', 2015)]),
                    get_baseline_value(input_params, 'CapitalCostStorage', [('STORAGE', f'{country}HGSTPN2'), ('YEAR', 2060)])*0.9,
                    get_baseline_value(input_params, 'CapitalCostStorage', [('STORAGE', f'{country}HGSTPN2'), ('YEAR', 2060)])*1.1
                    ]
        new_row = create_new_row('CapitalCostStorage', 'cost_h2_storage', f'REGION1,{country}{storage[0]}', 'unif', 'YEAR', 'interpolate', values)
        df = pd.concat([df, new_row], ignore_index=True)
    return df

def get_range(baseline_value, difference, is_lower_bound): #to ensure efficiency is more than 1
    lower_bound = max(1, baseline_value * (1 - difference))
    upper_bound = baseline_value * (1 + difference)
    if is_lower_bound:
        return lower_bound
    else:
        return upper_bound 

def add_efficiencies(df, input_params):
    for country in countries:
        for h2_tech in h2_techs_standard:
            if h2_tech == 'HGBCPN2' or h2_tech == 'HGSCPN2':
                code= f'ccs_{h2_tech[2:4]}'
                if h2_tech == 'HGBCPN2':
                    fuel = 'BM'
                else:
                    fuel = 'NG'
            else:
                if h2_tech == 'HGSRPN2':
                    fuel = 'NG'
                elif h2_tech == 'HGBGPN2':
                    fuel = 'BM'
                else:
                    fuel = 'E1'
                code = h2_tech[2:4]
            values = [get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+h2_tech),('YEAR',2015)]),
                        get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+h2_tech),('YEAR',2015)]),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+h2_tech),('YEAR',2060)]),0.1,True),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+h2_tech),('YEAR',2060)]),0.1,False)]
            new_row = create_new_row('InputActivityRatio', 'op_eff_capfac_h2_'+code, f'REGION1,{country}{h2_tech},{country}{fuel},1', 'unif', 'YEAR', 'interpolate', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for fuel_cell in fuel_cells:
            values = [get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+fuel_cell),('YEAR',2015)]),
                        get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+fuel_cell),('YEAR',2015)]),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+fuel_cell),('YEAR',2060)]),0.1,True),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+fuel_cell),('YEAR',2060)]),0.1,False)]
            new_row = create_new_row('InputActivityRatio', f'op_eff_capfac_h2_{fuel_cell[2:4]}', f'REGION1,{country}{fuel_cell},{country}H1,1', 'unif', 'YEAR', 'interpolate', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for renew in renewables:
            values = [get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+renew),('YEAR',2015)]),
                        get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+renew),('YEAR',2015)]),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+renew),('YEAR',2060)]),0.1,True),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+renew),('YEAR',2060)]),0.1,False)]
            new_row = create_new_row('InputActivityRatio', f'op_eff_capfac_renew', f'REGION1,{country}{renew},{country}{renew[0:2]},1', 'unif', 'YEAR', 'interpolate', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for fossil in fossils_new:
            values = [get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+fossil),('YEAR',2015)]),
                        get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+fossil),('YEAR',2015)]),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+fossil),('YEAR',2060)]),0.05,True),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+fossil),('YEAR',2060)]),0.05,False)]
            new_row = create_new_row('InputActivityRatio', f'op_eff_capfac_fossil', f'REGION1,{country}{fossil},{country}{fossil[0:2]},1', 'unif', 'YEAR', 'interpolate', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for ccs in ccs_bm:
            values = [get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+ccs),('YEAR',2015)]),
                        get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+ccs),('YEAR',2015)]),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+ccs),('YEAR',2060)]),0.1,True),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+ccs),('YEAR',2060)]),0.1,False)]
            new_row = create_new_row('InputActivityRatio', f'op_eff_capfac_ccs_biomass', f'REGION1,{country}{ccs},{country}BM,1', 'unif', 'YEAR', 'interpolate', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for ccs in ccs_fossil:
            values = [get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+ccs),('YEAR',2015)]),
                        get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+ccs),('YEAR',2015)]),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+ccs),('YEAR',2060)]),0.05,True),
                        get_range(get_baseline_value(input_params,'InputActivityRatio',[('TECHNOLOGY',country+ccs),('YEAR',2060)]),0.05,False)]
            new_row = create_new_row('InputActivityRatio', f'op_eff_capfac_ccs_fossil', f'REGION1,{country}{ccs},{country}{ccs[0:2]},1', 'unif', 'YEAR', 'interpolate', values)
            df = pd.concat([df, new_row], ignore_index=True)
    return df

def add_fuel_costs(df, input_params):
    for country in countries:
        for fuel in ['NG','CO','BM','BF']:
            if fuel in ['NG','CO']:
                code = 'fossil'
            else:
                code = 'biomass'
            for tech in {'00X00','00I00'}:
                if tech == '00X00' and fuel == 'NG' and country in ['FI','SE']:
                    continue
                elif tech == '00X00' and fuel == 'CO' and country in ['DK','NO']:
                    continue
                else:
                    technology = country+fuel+tech
                    value_dict_fossil = {'NG': [11.63,18.78], 'CO': [1.67,4.81]}
                    if code == 'fossil':
                        values = [get_baseline_value(input_params, 'VariableCost', [('TECHNOLOGY', technology), ('YEAR', 2015), ('MODE_OF_OPERATION', 1)]),
                                   get_baseline_value(input_params, 'VariableCost', [('TECHNOLOGY', technology), ('YEAR', 2015), ('MODE_OF_OPERATION', 1)]),
                                   *value_dict_fossil[fuel]]
                    else:
                        values = [get_baseline_value(input_params, 'VariableCost', [('TECHNOLOGY', technology), ('YEAR', 2015), ('MODE_OF_OPERATION', 1)]),
                                    get_baseline_value(input_params, 'VariableCost', [('TECHNOLOGY', technology), ('YEAR', 2015), ('MODE_OF_OPERATION', 1)]),
                                    get_baseline_value(input_params, 'VariableCost', [('TECHNOLOGY', technology), ('YEAR', 2060), ('MODE_OF_OPERATION', 1)])*0.8,
                                    get_baseline_value(input_params, 'VariableCost', [('TECHNOLOGY', technology), ('YEAR', 2060), ('MODE_OF_OPERATION', 1)])*1.2]
                    new_row = create_new_row('VariableCost', f'commodity_cost_'+code, f'REGION1,{technology},1', 'unif', 'YEAR', 'interpolate', values)
                    df = pd.concat([df, new_row], ignore_index=True)
    return df

def add_em_ac_ration(df, input_params): # write function calculating these values
    ccs_techs = ccs_bm + ccs_fossil + ['HGBCPN2','HGSCPN2']
    for country in countries:        
        for tech in ccs_techs:
            if tech in ccs_bm:
                code = 'ccs_biomass'
            elif tech in ccs_fossil:
                code = 'ccs_fossil'
            elif tech == 'HGBCPN2':
                code = 'h2_ccs_BC'
            elif tech == 'HGSCPN2':
                code = 'h2_ccs_SC'
            else:
                raise ValueError("tech not recognized")
            values = calculate_em_ac_ratio(input_params, country, tech, 0.53, 0.9)
            new_row = create_new_row('EmissionActivityRatio', f'em_activity_'+code, f'REGION1,{country}{tech},CO2,1', 'unif', 'YEAR', 'interpolate', values)
            df = pd.concat([df, new_row], ignore_index=True)
    return df

def calculate_em_ac_ratio(input_params, country, tech, lower_share, upper_share):
    biomass_em_activity = 102.8 # kton CO2 / PJ
    ng_em_activity = get_baseline_value(input_params, 'EmissionActivityRatio', [('TECHNOLOGY','DKNG00X00'),('EMISSION', 'CO2'), ('YEAR', 2015)])
    co_em_activity = get_baseline_value(input_params, 'EmissionActivityRatio', [('TECHNOLOGY','DKCO00I00'),('EMISSION', 'CO2'), ('YEAR', 2015)])
    input_activity_ratio_baseyear = get_baseline_value(input_params, 'InputActivityRatio', [('TECHNOLOGY', country+tech), ('YEAR', 2015), ('MODE_OF_OPERATION', 1)])
    input_activity_ratio_endyear = get_baseline_value(input_params, 'InputActivityRatio', [('TECHNOLOGY', country+tech), ('YEAR', 2060), ('MODE_OF_OPERATION', 1)])
    if tech in ccs_bm:
        em_activity = biomass_em_activity
    elif tech in ccs_fossil:
        em_activity = ng_em_activity if tech == 'NGCSPN2' else co_em_activity
    elif tech == 'HGBCPN2':
        em_activity = biomass_em_activity
    elif tech == 'HGSCPN2':
        em_activity = ng_em_activity
    else:
        raise ValueError("tech not recognized")
    em_ac_ratio_baseyear = -em_activity * input_activity_ratio_baseyear
    em_ac_ratio_endyear = -em_activity * input_activity_ratio_endyear
    return [em_ac_ratio_baseyear * upper_share, em_ac_ratio_baseyear * lower_share, em_ac_ratio_endyear * upper_share, em_ac_ratio_endyear * lower_share]

def get_capacity_factor(value, difference, is_lower_bound):
    lower_bound = max(0, value * (1 - difference))
    upper_bound = min(1, value * (1 + difference))
    if is_lower_bound:
        return lower_bound
    else:
        return upper_bound

def add_op_capfac(df, input_params):    
    for country in countries:
        #first operational life
        for h2_tech in h2_techs_standard:
            if h2_tech == 'HGBCPN2' or h2_tech == 'HGSCPN2':
                code= f'ccs_{h2_tech[2:4]}'
            else:
                code = h2_tech[2:4]
            values = [get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+h2_tech)])-5,
                      get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+h2_tech)])+5,
                      get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+h2_tech)])-5,
                      get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+h2_tech)])+5
                      ]
            new_row = create_new_row('OperationalLife', f'op_eff_capfac_h2_'+code, f'REGION1,{country}{h2_tech}', 'unif', 'None', 'fixed', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for fuel_cell in fuel_cells:
            values = [get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+fuel_cell)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+fuel_cell)])+5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+fuel_cell)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+fuel_cell)])+5
                        ]
            new_row = create_new_row('OperationalLife', f'op_eff_capfac_h2_'+fuel_cell[2:4], f'REGION1,{country}{fuel_cell}', 'unif', 'None', 'fixed', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for renew in renewables:
            values = [get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+renew)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+renew)])+5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+renew)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+renew)])+5
                        ]
            new_row = create_new_row('OperationalLife', f'op_eff_capfac_renew', f'REGION1,{country}{renew}', 'unif', 'None', 'fixed', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for fossil in fossils_new:
            values = [get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+fossil)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+fossil)])+5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+fossil)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+fossil)])+5
                        ]
            new_row = create_new_row('OperationalLife', f'op_eff_capfac_fossil', f'REGION1,{country}{fossil}', 'unif', 'None', 'fixed',values)
            df = pd.concat([df, new_row], ignore_index=True)
        for ccs in ccs_bm:
            values = [get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+ccs)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+ccs)])+5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+ccs)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+ccs)])+5
                        ]
            new_row = create_new_row('OperationalLife', f'op_eff_capfac_ccs_biomass', f'REGION1,{country}{ccs}', 'unif', 'None', 'fixed', values)
            df = pd.concat([df, new_row], ignore_index=True)
        for ccs in ccs_fossil:
            values = [get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+ccs)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+ccs)])+5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+ccs)])-5,
                        get_baseline_value(input_params, 'OperationalLife', [('TECHNOLOGY', country+ccs)])+5
                        ]
            new_row = create_new_row('OperationalLife', f'op_eff_capfac_ccs_fossil', f'REGION1,{country}{ccs}', 'unif', 'None', 'fixed',values)
            df = pd.concat([df, new_row], ignore_index=True)
        ### from her capacity factor
        for time_slice in ['S01B1','S01B2','S01B3','S02B1','S02B2','S02B3','S03B1','S03B2','S03B3','S04B1','S04B2','S04B3','S05B1','S05B2','S05B3']:
            for h2_tech in h2_techs_standard:
                if h2_tech == 'HGBCPN2' or h2_tech == 'HGSCPN2':
                    code= f'ccs_{h2_tech[2:4]}'
                else:
                    code = h2_tech[2:4]
                values = [get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+h2_tech), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                          get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+h2_tech), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+h2_tech), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.1,True),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+h2_tech), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.1,False)
                            ]      
                new_row = create_new_row('CapacityFactor', f'op_eff_capfac_h2_'+code, f'REGION1,{country}{h2_tech}'+','+time_slice, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for fuel_cell in fuel_cells:
                values = [get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+fuel_cell), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+fuel_cell), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+fuel_cell), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.1,True),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+fuel_cell), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.1,False)
                            ]
                new_row = create_new_row('CapacityFactor', f'op_eff_capfac_h2_'+fuel_cell[2:4], f'REGION1,{country}{fuel_cell}'+','+time_slice, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for renew in renewables:   
                values = [get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+renew), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+renew), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+renew), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.1,True),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+renew), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.1,False)
                            ] 
                new_row = create_new_row('CapacityFactor', f'op_eff_capfac_renew', f'REGION1,{country}{renew}'+','+time_slice, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for fossil in fossils_new:
                values = [get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+fossil), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+fossil), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+fossil), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.05,True),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+fossil), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.05,False)
                            ]
                new_row = create_new_row('CapacityFactor', f'op_eff_capfac_fossil', f'REGION1,{country}{fossil}'+','+time_slice, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for ccs in ccs_bm:
                values = [get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+ccs), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+ccs), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+ccs), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.1,True),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+ccs), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.1,False)
                            ]
                new_row = create_new_row('CapacityFactor', f'op_eff_capfac_ccs_biomass', f'REGION1,{country}{ccs}'+','+time_slice, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
            for ccs in ccs_fossil:
                values = [get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+ccs), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+ccs), ('YEAR', 2015), ('TIMESLICE', time_slice)]),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+ccs), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.05,True),
                            get_capacity_factor(get_baseline_value(input_params, 'CapacityFactor', [('TECHNOLOGY', country+ccs), ('YEAR', 2060), ('TIMESLICE', time_slice)]),0.05,False)
                            ]
                new_row = create_new_row('CapacityFactor', f'op_eff_capfac_ccs_fossil', f'REGION1,{country}{ccs}'+','+time_slice, 'unif', 'YEAR', 'interpolate', values)
                df = pd.concat([df, new_row], ignore_index=True)
    return df

def add_extraction_limit(df, input_params):
    extraction_tech = ['BM00X00']
    for country in countries:
        values = [get_baseline_value(input_params, 'TotalTechnologyAnnualActivityUpperLimit', [('TECHNOLOGY', country+extraction_tech[0]), ('YEAR', 2015)]),
                    get_baseline_value(input_params, 'TotalTechnologyAnnualActivityUpperLimit', [('TECHNOLOGY', country+extraction_tech[0]), ('YEAR', 2015)]),
                    get_baseline_value(input_params, 'TotalTechnologyAnnualActivityUpperLimit', [('TECHNOLOGY', country+extraction_tech[0]), ('YEAR', 2015)])*1.5,
                    get_baseline_value(input_params, 'TotalTechnologyAnnualActivityUpperLimit', [('TECHNOLOGY', country+extraction_tech[0]), ('YEAR', 2015)])*2
                    ]
        new_row = create_new_row('TotalTechnologyAnnualActivityUpperLimit', 'limit_bm', f'REGION1,{country}{extraction_tech[0]}', 'unif', 'YEAR', 'interpolate', values)
        df = pd.concat([df, new_row], ignore_index=True)
    return df

def delete_rows(df, values_to_delete): 
    delete_dict = values_to_delete
    mask = []
    for _, row in df.iterrows():
        name_in_dict = row['name'] in delete_dict.keys()
        indexes_subset = False
        if name_in_dict:
            for index_list in delete_dict[row['name']]:
                if all(str(index) in row['indexes'] for index in index_list):
                    indexes_subset = True     
        if row['min_value_base_year'] == 0 and row['max_value_base_year'] == 0 and row['min_value_end_year'] == 0 and row['max_value_end_year'] == 0:
            name_in_dict = True
            indexes_subset = True
        mask.append(name_in_dict and indexes_subset)
    df = df[~pd.Series(mask)]
    return df       

def main(): #beware, it overwrites the excel file
    excel_file = 'GSA_configuration.xlsx'
    input_params = load_input_params_baseline('input_data/Nordic/data/') # creates dictionary of dataframes

    df = create_df()
    df = add_demand(df, input_params) 
    df = add_em_penalty(df)    
    df = add_cost(df, input_params)
    df = add_efficiencies(df, input_params)    
    df = add_fuel_costs(df, input_params)    
    df = add_em_ac_ration(df, input_params)  
    print('1/3 done')  
    df = add_op_capfac(df, input_params) 
    df = add_extraction_limit(df, input_params)
    print('2/3 done')
    df = delete_rows(df, values_to_delete) 
    
    #sorting and information
    df.sort_values(by=['group','name'], inplace=True)
    num_unique_groups = df['group'].nunique()
    print(f"Number of unique groups: {num_unique_groups}")
    num_rows = df.shape[0]
    print(f"Number of rows: {num_rows}")

    # Load the second sheet before writing to the Excel file
    second_sheet_df = pd.read_excel(excel_file, sheet_name='results')

    with pd.ExcelWriter(excel_file) as writer:
        df.to_excel(writer, sheet_name='parameters', index=False)
        # Write the second sheet back without changes
        second_sheet_df.to_excel(writer, sheet_name='results', index=False)

main() # uncomment to run, beware it overwrites the excel file
        

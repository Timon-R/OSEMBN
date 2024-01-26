'''
This script calculates additional result variables from the model output, such as the share of renewable energy and the share of CCS technology used.
It creates new csv files with the results.
It is currently modified for snakemake but can be modified for use without it.
'''

# Import necessary packages
import pandas as pd

renewable_techs = ['BF','BM','GO','HY','OCWV','SO','WI','WS','NU']
fossil_techs = ['CO','NG','HF']
ccs_techs = ['COCS','NGCS','BMCS']
hydrogen_techs = ['BG','BC','SR','SC','EC']


def load_data(folderpath):
    filepath = f"{folderpath}/ProductionByTechnologyAnnual.csv"
    df = pd.read_csv(filepath)
    return df

def remove_unnecessary_techs_EL(df):
    tech_condition = df['TECHNOLOGY'].str.contains('00X|00I|EH1|IH1|HG|00TD') == False
    country_condition = df['TECHNOLOGY'].str.count('SE|NO|DK|FI') < 2
    df = df.loc[tech_condition & country_condition].copy()
    df.loc[:, 'country'] = df['TECHNOLOGY'].str[0:2]
    #print(df['TECHNOLOGY'].unique())
    return df

def remove_unnecessary_techs_HG(df):
    tech_condition = df['TECHNOLOGY'].str.contains('00X|00I|EH1|IH1|00TD|HGSL') == False
    country_condition = df['TECHNOLOGY'].str.count('SE|NO|DK|FI') < 2
    fuel_condition = df['FUEL'].str.contains('H1') == True
    df = df.loc[tech_condition & country_condition & fuel_condition].copy()
    df.loc[:, 'country'] = df['TECHNOLOGY'].str[0:2]
    #print(df['TECHNOLOGY'].unique())
    return df

def remove_unnecessary_techs_HGFC(df):
    tech_condition = df['TECHNOLOGY'].str.contains('HGFCPN2') == True
    df = df.loc[tech_condition].copy()
    df.loc[:, 'country'] = df['TECHNOLOGY'].str[0:2]
    return df

def calc_share(df, techs, tech_label):
    tech_regex = '|'.join(techs)
    df_tech = df[df['TECHNOLOGY'].str.contains(tech_regex)].copy()
    df_tech['country'] = df_tech['TECHNOLOGY'].str[0:2]
    df_tech_grouped = df_tech.groupby(['YEAR','country']).sum().reset_index()

    # Create a DataFrame with all combinations of years and countries
    all_years_countries = pd.MultiIndex.from_product([range(2015, 2061), ['DK', 'SE', 'FI', 'NO']], names=['YEAR', 'country']).to_frame(index=False)

    # Merge df_tech_grouped with all_years_countries, filling missing values with 0
    df_tech_grouped = pd.merge(all_years_countries, df_tech_grouped, on=['YEAR', 'country'], how='left')
    df_tech_grouped['VALUE'].fillna(0, inplace=True)
    df_tech_grouped['TECHNOLOGY'].fillna(df_tech_grouped['country'] + tech_label, inplace=True)

    df_tech_all = df_tech_grouped.groupby('YEAR').sum().reset_index()
    df_yearly = df.groupby(['YEAR','country']).sum().reset_index()
    df_yearly_all = df_yearly.groupby('YEAR').sum().reset_index()

    df_tech_grouped = pd.merge(df_tech_grouped, df_yearly, on=['YEAR', 'country'], suffixes=('', '_total'))
    df_tech_grouped['share'] = df_tech_grouped['VALUE'] / df_tech_grouped['VALUE_total']
    df_tech_grouped.drop(columns=['VALUE_total', 'TECHNOLOGY_total', 'FUEL_total', 'REGION_total','TECHNOLOGY'], inplace=True)
    df_tech_grouped['TECHNOLOGY'] = df_tech_grouped['country'] + tech_label    

    df_tech_all = pd.merge(df_tech_all, df_yearly_all, on='YEAR', suffixes=('', '_total'))
    df_tech_all['share'] = df_tech_all['VALUE'] / df_tech_all['VALUE_total']
    df_tech_all.drop(columns=['VALUE_total', 'TECHNOLOGY_total', 'FUEL_total', 'REGION_total'], inplace=True)

    df_tech_all['country'] = 'all'
    df_tech_all['TECHNOLOGY'] = tech_label
    df_tech = pd.concat([df_tech_grouped, df_tech_all], ignore_index=True)
    df_tech['REGION'] = 'REGION1'
    df_tech.rename(columns={'VALUE': 'absolute_production'}, inplace=True)
    df_tech['VALUE'] = df_tech['share']
    df_tech.drop(columns=['share'], inplace=True)

    df_tech = df_tech[['REGION','TECHNOLOGY', 'YEAR', 'VALUE', 'absolute_production']]
    df_tech.sort_values(['TECHNOLOGY', 'YEAR'], inplace=True)

    return df_tech

def calc_sum(df, techs, tech_label):
    country_techs = []
    for country in ['DK', 'SE', 'FI', 'NO']:
        for tech in techs:
            country_techs.append(country + tech)

    all_years = pd.DataFrame(range(2015, 2061), columns=['YEAR'])
    all_techs = pd.DataFrame(country_techs, columns=['TECHNOLOGY'])    
    all_combinations = all_years.assign(key=1).merge(all_techs.assign(key=1)).drop(columns='key')
    all_combinations['FUEL'] = all_combinations['TECHNOLOGY'].str[0:2] + 'E1'
    all_combinations['REGION'] = 'REGION1'

    df = pd.merge(all_combinations, df, on=['REGION', 'TECHNOLOGY', 'FUEL', 'YEAR'], how='left').fillna({'VALUE': 0})
    df = df[['REGION', 'TECHNOLOGY', 'FUEL', 'YEAR', 'VALUE']]

    df_yearly_sum = df.groupby('YEAR')['VALUE'].sum().reset_index()
    df_yearly_sum['REGION'] = 'REGION1'
    df_yearly_sum['TECHNOLOGY'] = tech_label
    df_yearly_sum['FUEL'] = 'E1'

    df = pd.concat([df, df_yearly_sum], ignore_index=True)
    df.sort_values(['TECHNOLOGY', 'YEAR'], inplace=True)

    return df


if __name__ == "__main__":
    
    folderpath = snakemake.params[0] #path to folder with results
    #folderpath = "results/WP1_NetZero_test/results_csv"
    df = load_data(folderpath)
    df_el = remove_unnecessary_techs_EL(df)
    df_ren = calc_share(df_el, renewable_techs, 'ELRENEW')
    df_foss = calc_share(df_el, fossil_techs, 'ELFOSSIL')
    df_ccs = calc_share(df_el, ccs_techs, 'ELCCS')
    df_hg = remove_unnecessary_techs_HG(df)
    for tech in hydrogen_techs:
        if tech == 'EC':
            techs = [tech,'EA']
        else: techs = [tech]
        df_tech = calc_share(df_hg, techs, tech)
        df_ren = pd.concat([df_ren, df_tech], ignore_index=True)
    df_new = pd.concat([df_ren, df_foss, df_ccs], ignore_index=True)    
    df_new.to_csv(f"{folderpath}/AnnualShareOfProduction.csv", index=False)

    # df_hgfc = remove_unnecessary_techs_HGFC(df)
    # df_hgfc = calc_sum(df_hgfc, ['HGFCPN2'], 'HGFCPN2')
    # df_hgfc.to_csv(f"{folderpath}/ProductionFromFuelCells.csv", index=False)

   
# check if renew and fossil add together to 1
    # df_foss.set_index('YEAR', inplace=True)
    # df_ren.set_index('YEAR', inplace=True)
    # df_sum = df_foss['share'] + df_ren['share']
    # print(df_sum)
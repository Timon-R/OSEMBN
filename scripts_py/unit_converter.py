'''
converts units from ton/year into PJ/year and GW

@author: Timon Renzelmann
'''

energy_density_h2 = 120.0 #GJ/ton


def PJ_year_into_GW(PJ_year):
    '''
    converts units from PJ/year into GW
    '''
    GW = PJ_year /31.536
    return GW

def GW_into_PJ_year(GW):
    '''
    converts units from GW into PJ/year
    '''
    PJ_year = GW * 31.536
    return PJ_year

def ton_year_into_PJ_year(ton_year):
    '''
    converts units from ton/year into PJ/year
    '''
    PJ_year = ton_year * energy_density_h2 / 1000000
    return PJ_year

def ton_year_into_capacity(ton_year, capacity_factor, efficiency):
    '''
    converts units from ton/year into GW
    '''
    GW = PJ_year_into_GW(ton_year_into_PJ_year(ton_year) / capacity_factor / efficiency)
    return GW

#print(round(ton_year_into_capacity(30000, 0.9, 0.66), 8))

print(PJ_year_into_GW(0.141)*0.7)



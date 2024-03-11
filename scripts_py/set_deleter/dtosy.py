'''
Deletes technologies from the csv input files.

@author: haukeh
modified by Timon Renzelmann
'''
import os
import sys
import pandas as pd
from shutil import copyfile#%% Read in datapackage

def read_dp(path):
    #path = '' #for testing
    datafiles =list()
    datafiles = next(os.walk(path))
    #for root, dirs, files in os.walk(path+'data'):
    for root, dirs, files in os.walk(path):
        datafiles = [f for f in files if not f[0] == '.']
    dic = dict()
    j = 0
    for j in range(len(datafiles)):
        dic[datafiles[j]] = pd.read_csv(path+'\\'+datafiles[j])
    return dic

def dp_new(dic,techs):
    dp_new_path = 'input_data\\WP1_NetZero'
    try:
        os.mkdir(dp_new_path)
    except OSError:
        print("Creation of the directory %s failed" % dp_new_path)
    #copyfile('datapackage.json',dp_new_path+'/datapackage.json')
    dp_new_path = dp_new_path+'/data'
    try:
        os.mkdir(dp_new_path)
    except OSError:
        print("Creation of the directory %s failed" % dp_new_path)
    for i in dic:
        df = dic[i]
        if i=='TECHNOLOGY.csv':
            #dic[i] = dic[i]['VALUE'].astype('str')
            m = df.VALUE.isin(techs)
            df = df[~m]
            df.to_csv(dp_new_path+'/'+i,index=False)
        elif 'TECHNOLOGY' in df.columns:
            m = df.TECHNOLOGY.isin(techs)
            df = df[~m]
            df.to_csv(dp_new_path+'/'+i,index=False)
        else:
            df.to_csv(dp_new_path+'/'+i, index=False)
    return 

def main(dp_path,tech_path):
    dic_data = read_dp(dp_path)
    t2d = pd.read_csv(tech_path)
    p_n_dp = dp_new(dic_data,t2d.iloc[:,0])

if __name__ == '__main__':
    #techs = sys.argv[1]
    techs = os.path.abspath('scripts_py\\tech_deleter-main\\t2d.csv')
    dp_path = os.path.abspath('.\\input_data\\WP1_NetZero\\data')
    main(dp_path,techs)
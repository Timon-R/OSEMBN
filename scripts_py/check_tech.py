'''
This script checks if a technology exists in the results of the models of the GSA.

@author: Timon Renzelmann
'''
import os
import pandas as pd

#technologies_to_check = ["NOHGFCPN2", "SEHGFCPN2", "DKHGFCPN2", "FIHGFCPN2"]
technologies_to_check = ['NONGCSPN2', 'SENGCSPN2', 'DKNGCSPN2', 'FINGCSPN2']

tech_exists = False
for i in range(0, 300):
    file_path = os.path.join("results", "0", f"model_{i}","results", "ProductionByTechnologyAnnual.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)        
        for technology in technologies_to_check:
            if technology in df['TECHNOLOGY'].values:
                print(f"{technology} exists in model_{i}")
                tech_exists = True    
    else:
        print(f"File {file_path} does not exist")
if not tech_exists:
    print("None of the technologies exist in the models")
"""From OSEMBE
This script handles the conversion of OSeMOSYS results in a workflow using otoole.
"""
import os
import sys
import otoole
import datetime

if __name__ == '__main__':
    
    args = sys.argv[1:]
   
    try:
        if len(args) != 4:
            print("Usage: python scripts_smk/convert.py <path_config> <path_gurobi.sol> <path_results> <path_data>")
            exit(1)

        path_config = args[0]
        path_sol = args[1]
        path_res = args[2]
        path_dp = args[3]

        if os.path.exists(path_sol):
            otoole.convert_results(path_config, 'gurobi', 'csv', path_sol, path_res, 'csv', path_dp)

        file_done = open(os.sep.join(path_res.split('/')[:-1]+["res-csv_done.txt"]), "w")
        file_done.write("File created or updated at: " + str(datetime.datetime.now()))
        file_done.close()
        print("Conversion into csv results done.")

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
"""From OSEMBE
This script runs OSeMOSYS models using gurobi. It takes as input an lp-file and produces a sol-file.
"""
import sys
import os
import gurobipy as gp
import pandas as pd

#CONSTRAINTS = ['Constr E8_AnnualEmissionsLimit']
CONSTRAINTS = []

def sol_gurobi(lp_path: str, environment, log_path: str, threads: int):
    m = gp.read(lp_path, environment)
    m.Params.LogToConsole = 0  # don't send log to console
    m.Params.Method = 2  # 2 = barrier
    m.Params.Threads = threads  # limit solve to use max {threads}
    m.Params.NumericFocus = 0  # 0 = automatic; 3 = slow and careful
    m.Params.LogFile = log_path  # don't write log to file
    m.optimize()

    return m

def get_duals(model):
    constraints = CONSTRAINTS
    try:
        dual = model.Pi
        constr = model.getConstrs()
        df_dual = pd.DataFrame(data= {'info': constr, 'value': dual})
        df_dual = df_dual.astype({'info': 'str'})
        meta = df_dual['info'].str.split('.', expand=True)
        meta = meta[1].str.split('(', expand=True)
        df_dual['constraint'] = meta[0]
        df_dual['sets'] = meta[1].str[:-2]
        df_dual = df_dual.drop(columns=['info'])
    except:
        df_dual = pd.DataFrame(columns=['value', 'constraint', 'sets'])
    dic_duals = {}
    if not df_dual.empty:
        for c in constraints:
            dic_duals[c] = df_dual[df_dual['constraint']==c]
            if not dic_duals[c].empty:
                sets = dic_duals[c]['sets'].str.split(',', expand=True).add_prefix('set_')
                dic_duals[c] = pd.concat([dic_duals[c], sets], axis=1)
                dic_duals[c] = dic_duals[c].drop(columns=['sets'])
            else:
                dic_duals[c] = pd.DataFrame(columns=['value', 'constraint', 'set_0', 'set_1', 'set_2'])
    return dic_duals

def write_duals(dict_duals: dict, path: str):
    path_res = os.sep.join(path.split('/')[:-1]+['results_csv'])
    os.mkdir(path_res)
    for df in dict_duals:
        dict_duals[df].to_csv('%(path)s/Dual_%(constr)s.csv' % {'path': path_res, 'constr': df}, index=False)
    return

def write_sol(sol, path_out: str, path_gen: str):
    try:
        sol.write(path_out)
    except:
        sol.computeIIS()
        sol.write("%(path)s.ilp" % {'path': path_gen})
    return

if __name__ == "__main__":

    # args = sys.argv[1:]

    # if len(args) != 2:
    #     print("Usage: python run.py <lp_path> <generic_out_path>")
    #     exit(1)

    # lp_path = args[0]
    # gen_path = args[1]

    lp_path = snakemake.input[0]
    outpath = snakemake.output[0]
    log_path = snakemake.log[0]
    #dual_path = snakemake.output[1]
    threads = snakemake.threads

    env = gp.Env(log_path)

    model = sol_gurobi(lp_path, env, log_path, threads)
   # dic_duals = get_duals(model)
    #write_duals(dic_duals, dual_path)
    write_sol(model, outpath, outpath)

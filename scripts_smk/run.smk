'''
Snakefile to run the baseline model
'''


rule convert_dp:
    message: "Converting csv for {wildcards.scen}"
    input:
        other = expand("input_data/{{scen}}/data/{files}", files=baseline_dp_files),
        dp_path = "input_data/{scen}/data"
    output:
        df_path = "working_directory/{scen}.txt"
    log:
        "working_directory/otoole_{scen}.log"
    conda:
        "../envs/otoole_env.yaml"
    shell:
        "otoole -v convert csv datafile {input.dp_path} {output.df_path} config/otoole.yaml > {log} 2>&1"

rule pre_process:
    input:
        "working_directory/{scen}.txt"
    output:
        temporary("working_directory/{scen}.pre")
    conda:
        "../envs/otoole_env.yaml"
    shell:
        "python scripts_smk/pre_process.py otoole {input} {output}"

rule build_lp:
    input:
        df_path = "working_directory/{scen}.pre"
    params:
        model_path = "model/osemosys.txt",
    output:
        temp("working_directory/{scen}.lp")
    log:
        "working_directory/{scen}.log"
    threads: 4
    conda:
        "../envs/otoole_env.yaml"
    shell:
        "glpsol -m {params.model_path} -d {input.df_path} --wlp {output} --check > {log}"

rule run_model:
    priority: 100
    message: "Solving the LP for '{input}'"
    input:
        "working_directory/{scen}.lp",
    output:
         temp("working_directory/{scen}.sol"),
         #directory("working_directory/{scen}_duals")
         #Unhash the line above, and the dic_duals and write_duals (in the run.py) if you want dual values as output, this doesn't work atm though
    conda:
        "../envs/gurobi_env.yaml"
    log:
        "working_directory/gurobi/{scen}.log",
    threads: 4
    script:
        "run.py"

rule convert_sol:
    priority: 100
    input:
        sol_path = "working_directory/{scen}.sol",
        dp_path = "input_data/{scen}/data"
    params:
        res_folder = "results/{scen}/results_csv"
    output:
        res_path = "results/{scen}/res-csv_done.txt"
    conda:
        "../envs/otoole_env.yaml"
    shell:
        "python scripts_smk/convert.py config/otoole.yaml {input.sol_path} {params.res_folder} {input.dp_path}"

rule make_res:
    message: "Creating res for {wildcards.scen}"
    input:
        other = expand("input_data/{{scen}}/data/{files}", files=baseline_dp_files),
        dp_path = "input_data/{scen}/data"
    output:
        output_file = "visualisations/{scen}/res.graphml",
        output_png = "visualisations/{scen}/res.png"
    conda:
        "../envs/otoole_env.yaml"
    script:
        "make_res.py"

rule calc_result_variables: 
    priority: 100
    input: "results/{sce}/res-csv_done.txt"
    params: "results/{scen}/results/results_csv"
    output: 
        "results/{scen}/results/results_csv/AnnualShareOfProduction.csv"
        #,"results/{scen}/results/results_csv/ProductionFromFuelCells.csv" #needs to be uncommented in script, too
    script:
        "calc_result_variables.py"

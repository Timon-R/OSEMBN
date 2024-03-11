import json
import shutil
import gzip

wildcard_constraints: #one or more digits for each wildcard
    modelrun=r"\d+",
    scenarios=r"\d+"

def csv_from_scenario(wildcards): #returns the input csv folder for the scenario
    return SCENARIOS.loc[int(wildcards.scenario), 'csv'] 

def config_from_scenario(wildcards): #returns the config file for the scenario (config/otoole.yaml)
    return SCENARIOS.loc[int(wildcards.scenario), 'config']

rule create_model_data: 
    message: "Copying and modifying data for '{params.folder}'"
    input:
        csv=csv_from_scenario,
        sample="modelruns/{scenario}/model_{model_run}/sample_{model_run}.txt",
        config=config_from_scenario
    log: "log/create_modelrun/create_model_data_{scenario}_{model_run}.log"
    params:
        folder=directory("results/{scenario}/model_{model_run}/data"),
    conda: "../envs/otoole_env.yaml"
    output:
        csvs = expand("results/{{scenario}}/model_{{model_run}}/data/{x}.csv", x=INPUT_FILES)
    shell:
        "python scripts_smk/gsa/create_modelrun.py {input.csv} {params.folder} {input.sample} {input.config} > {log} 2>&1"

rule copy_otoole_config:
    message: "Copying otoole configuration file for '{params.folder}'"
    input:
        yaml=config_from_scenario,
        csvs=rules.create_model_data.output
    params:
        folder="results/{scenario}/model_{model_run}",
    output:
        yaml="results/{scenario}/model_{model_run}/config.yaml",
    run:
        shutil.copy(input.yaml, output.yaml)

rule generate_datafile: #=convert_dp
    message: "Generating datafile for '{output}'"
    input:
        csv = rules.create_model_data.output,
        config="results/{scenario}/model_{model_run}/config.yaml"
    output:
        datafile = temp("temp/{scenario}/model_{model_run}.txt")
    params:
        csv_dir = "results/{scenario}/model_{model_run}/data"
    conda: "../envs/otoole_env.yaml"
    log:
        "log/generate_datafile/otoole_{scenario}_{model_run}.log"
    shell:
        "otoole -v convert csv datafile {params.csv_dir} {output.datafile} {input.config} > {log} 2>&1"

rule modify_model_file: #pre_processing of the model file
    message: "Adding MODEX sets to model file"
    input:
        "temp/{scenario}/model_{model_run}.txt"
    output:
        temp("temp/{scenario}/model_{model_run}_modex.txt")
    threads:
        1
    conda: "../envs/otoole_env.yaml"
    shell:
        "python scripts_smk/pre_process.py otoole {input} {output}"

rule generate_lp_file:
    priority: 0
    message: "Generating the LP file for '{output}'"
    input:
        data="temp/{scenario}/model_{model_run}_modex.txt",
        model=config['model_file']
    resources:
        mem_mb=64000,
        disk_mb=16000,
        time=180
    threads:
        4
    output:
        temp(expand("temp/{{scenario}}/model_{{model_run}}.lp{zip_extension}", zip_extension=ZIP))
    benchmark:
        "benchmarks/gen_lp/{scenario}_{model_run}.tsv"
    log:
        "log/generate_lp_file/glpsol_{scenario}_{model_run}.log"
    conda: "../envs/otoole_env.yaml"
    shell:
        "glpsol -m {input.model} -d {input.data} --wlp {output} --check > {log} 2>&1"

rule unzip_lp:
    priority: 0
    message: "Unzipping LP file"
    input:
        "temp/{scenario}/model_{model_run}.lp.gz"
    output:
        temp("temp/{scenario}/model_{model_run}.lp")
    run:
        with gzip.open(input[0], 'rb') as f_in:
            with open(output[0], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

rule solve_lp:
    priority: 100
    message: "Solving the LP for '{output}' using {config[solver]}"
    input:
        "temp/{scenario}/model_{model_run}.lp"
    output:
        temp(expand("results/{{scenario}}/model_{{model_run}}/model_{{model_run}}.sol")) #the temp can be removed if needed for debugging
    log:
        "log/solve_lp/solver_{scenario}_{model_run}.log"
    conda:
        "../envs/gurobi_env.yaml"
    resources:
        mem_mb=30000,
        disk_mb=20000,
        time=720
    threads:
        4
    script:
        "run.py"        

rule process_solution:
    priority: 100
    message: "Processing {config[solver]} solution for model run {wildcards.model_run}"
    input:
        solution="results/{scenario}/model_{model_run}/model_{model_run}.sol",
        config="results/{scenario}/model_{model_run}/config.yaml",
    output: 
        expand("results/{{scenario}}/model_{{model_run}}/results/{csv}.csv", csv=OUTPUT_FILES),
        "results/{scenario}/model_{model_run}/res-csv_done.txt" #tells when it was executed
    conda: "../envs/otoole_env.yaml"
    log: "log/process_solution/process_solution_{scenario}_{model_run}.log"
    params:        
        input_folder= "results/{scenario}/model_{model_run}/data",
        folder="results/{scenario}/model_{model_run}/results"
    shell: 
        "python scripts_smk/convert.py {input.config} {input.solution} {params.folder} {params.input_folder} > {log} 2>&1"
   
rule get_statistics:
    priority: 100
    message: "Extract the {config[solver]} statistics from the sol file"
    input: "results/{scenario}/model_{model_run}/model_{model_run}.sol"
    output: "modelruns/{scenario}/model_{model_run}/{model_run}.stats"
    log: "log/get_statistics/get_statistics_{scenario}_{model_run}.log"
    shell: 
        "python scripts_smk/gsa/get_statistics.py {input} {output} > {log} 2>&1"

rule get_objective_value:
    input: expand("modelruns/{{scenario}}/model_{model_run}/{model_run}.stats",  model_run=MODELRUNS)
    output: "results/{scenario}/objective_{scenario}.csv"
    script:
        "gsa/get_objective_value.py"

rule calc_result_variables:
    priority: 100
    input: "results/{scenario}/model_{model_run}/res-csv_done.txt"
    params: "results/{scenario}/model_{model_run}/results"
    output: 
        "results/{scenario}/model_{model_run}/results/AnnualShareOfProduction.csv",
        "results/{scenario}/model_{model_run}/results/ProductionFromFuelCells.csv"
    script:
        "calc_result_variables.py"
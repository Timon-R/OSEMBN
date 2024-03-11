'''
Snakefile to run the baseline model
'''

# rule update_H2_values:
#     message: "Updating input folder based on H2 parameters"
#     input: 
#         input_file = lambda wildcards: "Hydrogen_baseline.xlsx" if wildcards.scen == "WP1_NetZero" else "Hydrogen_test.xlsx" if wildcards.scen == "WP1_NetZero_test" else None
#     output:
#         expand("input_data/{{scen}}/data/{files}", files=baseline_dp_files)
#     shell:
#         "python scripts_smk/hydrogen_to_csv.py {input.input_file} {wildcards.scen}"

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
    params:
        config = lambda wildcards: "config/otoole_osembe.yaml" if wildcards.scen == 'OSeMBE' else "config/otoole.yaml"
    shell:
        "otoole -v convert csv datafile {input.dp_path} {output.df_path} {params.config} > {log} 2>&1"


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
        model_path = lambda wildcards: "model/osemosys_osembe.txt" if wildcards.scen == 'OSeMBE' else "model/osemosys_test.txt" if wildcards.scen == 'Nordic_test' else "model/osemosys.txt"
    output:
        temp("working_directory/{scen}.lp")
    log:
        "working_directory/{scen}.log"
    threads:4 
    conda:
        "../envs/otoole_env.yaml"
    shell:
        "glpsol -m {params.model_path} -d {input.df_path} --wlp {output} --check > {log}"

rule run_model:
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
    input:
        sol_path = "working_directory/{scen}.sol",
        dp_path = "input_data/{scen}/data"
    params:
        res_folder = "results/{scen}/results_csv",
        config = lambda wildcards: "config/otoole_osembe.yaml" if wildcards.scen == 'OSeMBE' else "config/otoole.yaml"
    output:
        res_path = "results/{scen}/res-csv_done.txt"
    conda:
        "../envs/otoole_env.yaml"
    shell:
        "python scripts_smk/convert.py {params.config} {input.sol_path} {params.res_folder} {input.dp_path}"

#this would need to be modified from the template from OSEMBE, work with convert_sol first
# rule create_configs: # works
#     input:
#         config_tmpl = "config/iamc_config.yaml"
#     output:
#         config_scen = "working_directory/iamc_config_{scen}.yaml"
#     conda:
#         "envs/yaml_env.yaml"
#     shell:
#         "python scripts_smk/ed_config.py {wildcards.scen} {input.config_tmpl} {output.config_scen}"

# rule res_to_iamc: # doesn't work yet
#     input:
#         res_path = "results/{scen}/res-csv_done.txt",
#         config_file = "working_directory/iamc_config_{scen}.yaml"
#     params:
#         inputs_folder = "input_data/{scen}/data",
#         res_folder = "results/{scen}/results_csv"
#     output:
#         output_file = "results/{scen}.xlsx"
#     conda:
#         "envs/openentrance_env.yaml"
#     shell:
#         "python scripts_smk/resultify.py {params.inputs_folder} {params.res_folder} {input.config_file} {output.output_file}"

rule make_res: # doesn't work for the OSeMBE scenario -> modify config file (otoole_osembe.yaml) in python script
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

# rule make_dag:
#     output: "working_directory/dag.txt"
#     shell:
#         "snakemake --dag dummy_target > {output}"


# rule plot_dag:
#     input: "working_directory/dag.txt"
#     output: "dag.png"
#     conda: "envs/graphviz_env.yaml"
#     shell:
#         """
#         dot -Tpng {input} > {output}
#         start {output}
#         """

# rule clean_all: #removes all the results and working_directory files
#     shell:
#         "del /S /Q results\\* && del /S /Q working_directory\\*"

# rule clean_wd: 
#     shell:
#         "del /S /Q working_directory\\*"
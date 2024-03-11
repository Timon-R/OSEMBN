#this seems to be working
rule create_sample:
    input:
        "config/parameters.csv"
        #,"config/results.csv" # consider commenting this out so it doesn't run every time changing the results csv
    message: "Creating sample for '{params.replicates}' trajectories and '{params.parameters}' parameters"
    params:
        replicates=config['replicates'],
        parameters=config['parameters']
    output: "modelruns/{scenario}/morris_sample.txt"
    conda: "../envs/sample_env.yaml"
    log: "log/create_{scenario}_sample.log"
    shell:
        "python scripts_smk/gsa/create_sample.py {params.parameters} {output} {params.replicates} > {log} 2>&1"

rule expand_sample:
    params:
        parameters=config['parameters']
    input: "modelruns/{scenario}/morris_sample.txt"
    output: expand("modelruns/{{scenario}}/model_{model_run}/sample_{model_run}.txt", model_run=MODELRUNS)
    conda: "../envs/sample_env.yaml"
    log: "log/expand_{scenario}_sample.log"
    script:
        "gsa/expand_sample.py"

rule scale_sample:
    params:
        parameters=config['parameters']
    input:
        "modelruns/{scenario}/morris_sample.txt"
    output:
        "modelruns/{scenario}/morris_sample_scaled.txt"
    conda: "../envs/sample_env.yaml"
    log: "log/expand_{scenario}_sample.log"
    shell:
        "python scripts_smk/gsa/scale_sample.py {input} {params.parameters} {output} > {log} 2>&1" # the log isn't here in the original
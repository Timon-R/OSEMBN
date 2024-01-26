<<<<<<< HEAD
# OSEMBN

This repo contains the Open Source Energy Modeling Base for the Nordic countries (OSEMBN). It was derived from the [OSeMBE_ECEMF model](https://github.com/KTH-dESA/OSeMBE_ECEMF) using the scenario WP1_NetZero.


## Structure of the repository

The config folder contains configuration files for running the model.
The envs folder contains yaml files for conda environments needed to run the model. They are used in the snakemake workflow.
The input_data folder contains the input data for the different scenarios.
The scripts_py folder contains python scripts that are independend of the snakemake workflow.
The scripts_smk folder contains python scripts that are utilized in the snakeamke workflow.

## Scenarios



## Running the model


This workflow allows to run one or multiple scenarios.
Starting from an OSeMOSYS datapackage going through all steps,
running the model with the Gurobi solver and producing the results in IAMC format.

In addition to the standard OSeMOSYS outputs, the workflow can produce CSV files containing the dual values for all constraints in the model.

### Installation

Install snakemake using conda into a new environment called `snakemake`:

```bash
conda install -c conda-forge mamba
mamba create -c bioconda -c conda-forge -n snakemake snakemake-minimal
```

The workflow manages dependencies through conda environments.
Dependencies are defined per rule and are installed upon first running the workflow.

### Adding new scenarios

1. Place datapackage(s) in the folder `input_data`. Each datapackage should be placed in a folder
that is named after the scenario, e.g. `baseline`.

### Running the workflow

3. ***Optional***: To retrieve dual values from your model you need to edit the list of `constraints` in the file `run.py`.
4. Open terminal or command prompt and change to the directory of the snakefile.
5. ***Optional***: Perform a dry run to test snakemake with the command: `snakemake -n`
5. Start the scenario runs with the command `snakemake --cores <number of cores to be used> --use-conda`

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
The model contains 5 scenarios.

1. Nordic_before_interconnectors
This scenario differs from the OSeMBE scenario WP1_NetZero only in the way, that all the non-Nordic sets are deleted. This includes technologies, fuels and emissions. This also means that all the technologies that represented interconnectors to other, non-Nordic countries are deleted, too so that the Nordics are completely isolated.

2. Nordic_without_H2
This scenario contains interconnector technologies to non-Nordic countries, just as the original OSeMBE model. However, each interconnector, such as DKELDEPH2 (Denmark to Germany) has been split into two technologies ending with IH2 for imports to the Nordic country and EH2 for exports from the Nordic country. This was necessary, as the annual activity limit which was used as a contraint doesn't distuinguish between modes.
The TotalTechnologyAnnualyActivityUpperLimit and -LowerLimit have been used to set the imports and exports to non-Nordic countries to the results from the OSeMBE WP1_NetZero scenario.
It has to be noted, however, that this restraint neglects the temporal resolutions smaller than a year. This means, that the imports and exports take place at different time slices. However, then annual values are the same.
The capacity for those interconnectors have been set to 8 GW, which is higher than for the OSeMBE model to avoid the model to not be able to meet the contraint. This could be reduced to a lower value but has to be at least slightly higher than for the OSeMBE model because leads to errors otherwise (as the model can't meet the contraint).

3. Nordic
This model includes added hydrogen technologies (more information about this follows). However it has the same emissions penalty for CO2 as the OSeMBE model which lead to negative emissions from 2030 onwards, exploiting the biomass CCS technology that has a high carbon capture efficiency of 70-80%.

4. Nordic_co2_limit
The emissions penalty for CO2 has been deleted and replaced with an emission limit that linearly reduces the emissions from the baseyear to 0 at 2050.

5. Nordic_em_free
This scenario gives the model complete freedom for emissions. Neither an emission penalty nor an emission limit has been set.

## Running the model

The model can be run via the snakemake workflow or via the python script in the scripts_py folder.

### Installation of snakemake

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

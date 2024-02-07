
# OSEMBN

This repo contains the Open Source Energy Modeling Base for the Nordic countries (OSEMBN). It was derived from the [OSeMBE_ECEMF model](https://github.com/KTH-dESA/OSeMBE_ECEMF) using the scenario WP1_NetZero.


## Structure of the repository

The config folder contains configuration files for running the model.
The envs folder contains yaml files for conda environments needed to run the model. They are used in the snakemake workflow.
The input_data folder contains the input data for the different scenarios.
The scripts_py folder contains python scripts that are independend of the snakemake workflow.
The scripts_smk folder contains python scripts that are utilized in the snakemake workflow.

## Scenarios
The model contains 5 scenarios.

1. **Nordic_before_interconnectors:**
This scenario differs from the OSeMBE scenario WP1_NetZero only in that all non-Nordic sets are deleted. This includes technologies, fuels and emissions. This also means that all technologies that represented interconnectors with other non-Nordic countries are also removed, so that the Nordics are completely isolated.

2. **Nordic_without_H2:**
This scenario includes interconnector technologies to non-Nordic countries, just like the original OSeMBE model. However, each interconnector, such as DKELDEPH2 (Denmark to Germany), has been split into two technologies ending with IH2 for imports into the Nordic country and EH2 for exports from the Nordic country. This was necessary because the annual activity limit used as a constraint doesn't distinguish between modes. The TotalTechnologyAnnualActivityUpperLimit and -LowerLimit were used to set the imports and exports to non-Nordic countries to the results from the OSeMBE WP1_NetZero scenario. However, it should be noted that this constraint neglects the temporal resolutions smaller than one year. This means that imports and exports take place in different time slices. However, the annual values are then the same. The capacity for these interconnectors has been set at 8 GW, which is higher than for the OSeMBE model, to avoid the model not being able to fulfil the constraint. This could be reduced to a lower value, but must be at least slightly higher than for the OSeMBE model, otherwise errors will occur (as the model can't meet the constraint).

3. **Nordic:**
This model includes additional hydrogen technologies (more information on this will be added later). It has the same emissions penalty for CO2 as the OSeMBE model, leading to negative emissions from 2030, exploiting biomass CCS technology, which has a high carbon capture efficiency of 70-80%.

4. **Nordic_co2_limit:**
The CO2 emissions penalty has been removed and replaced with an emissions cap that linearly reduces emissions from the base year (2015) to 0 in 2050. Between 2050 and 2060, it stays at 0.

5. **Nordic_em_free:**
This scenario gives the model complete freedom for emissions. Neither an emissions penalty nor an emissions limit has been set.

## Code deciphering

The model follows the nomenclature of [the OSeMBE model](https://osembe.readthedocs.io/en/latest/). The scripts code_decipherer.py and the script data_decipherer in the folder scripts_py allow to decode the codes used in the model for technologies, emissions and fuels for better understanding.

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

## Licenses

Copyright (C) 2024 by Timon Renzelmann.
Software is released under the [MIT license](./LICENSE).
Data is licensed under the [CC-BY-SA-4.0 license](./LICENSE_for_data) 


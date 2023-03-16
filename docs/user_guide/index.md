# User Guide

In this guide, we will describe:

- how to install the package
- how to use the software, including any requirements
- the different modes supported by the software

`benchcab` has been designed to work on NCI machine exclusively. It might be extended later on to other systems.

## Pre-requisites

To use `benchcab`, you need to join the following projects at NCI:

- [ks32][ks32_mynci]
- [hh5][hh5_mynci]

## Installation

The package is already installed for you in the Conda environments under the hh5 project. You simply need to load the module for the conda environment:

```bash
   module use /g/data/hh5/public/modules
   module load conda
```

You need to load the module on each new session at NCI on login or compute nodes.

!!! Tip "Save the module location"

    You should not put any `module load` or `module add` commands in your `$HOME/.bashrc` file. But you can safely store the `module use /g/data/hh5/public/modules` command in your `$HOME/.bashrc` file. This means you won't have to type this line again in other sessions you open on Gadi.

## Usage

`benchcab` will run the exact same configurations on two CABLE branches specified by the user, e.g. a user branch (with personal changes) against the head of the trunk. The results should be attached with all new [tickets](https://trac.nci.org.au/trac/cable/report/1).

The code will: (i) check out and (ii) build the code branches. Then it will run each executable across N standard science configurations for a given number of sites. It is possible to produce some plots locally from the output produced. But [the modelevaluation website](https://modelevaluation.org/) can be used for further benchmarking and evaluation.

### Create a work directory

#### Choose a location

You can run the benchmark from any directory you want under /scratch or /g/data. /scratch is preferred as the data in the run directory does not need to be preserved for a long time. The code will create sub-directories as needed. Please ensure you have enough space to store the CABLE outputs in your directory, at least temporary, until you upload them to [modelevaluation.org](https://modelevaluation.org/). You will need about 70GB for the outputs of a full evaluation case.

!!! Warning "The HOME directory is unsuitable"
    
    Do not use your $HOME directory to contain the work directory as it does not have enough space to contain the outputs.

#### Setup the work directory

The simplest is to clone an existing work directory with git and then adapt it to your case. Such [an example work directory][bench_example] is available on GitHub under the CABLE-LSM organisation.
  
Once the work directory is cloned, you will need to adapt the `config.yaml` file to your case. Refer to [the description of the options][config_options] for this file.

## Run the simulations

Once you have a configuration file, you need to load the module for `benchcab`:

```bash
module use /g/data/hh5/public/modules
module load conda/analysis3-unstable
```

Then simply launch `benchcab` from within your work directory:

```bash
benchcab
```

For help on the available options for `benchcab`:

```bash
benchcab -h
```

## Check the status

The benchmarking will follow the steps:

1. Checkout both branches. The codes will be stored under `src/` directory in your work directory. The sub-directories are created automatically.
1. Compile the source code from both branches
1. Setup and launch a PBS job to run the simulations in parallel. The simulation inputs and outputs are stored under `runs/site/`.

When `benchcab` launches the PBS job, it will print out the job ID to the terminal. You can check the status of the job with `qstat`.

## Analyse the output with modelevaluation.org

Once the benchmarking has finished running all the simulations, you need to upload the output files to modelevaluation.org:

1. Open and log into modelevaluation.org
1. Navigate to the `NRI Land testing` workspace
1. Create a model profile for the two model branches you are using
1. Create a model output and upload the outputs in `runs/sites/outputs/` under your work directory
1. Launch the analysis

## Contacts

Please enter your questions as issues on [the benchcab repository][issues-benchcab].

Alternatively, you can also post discussions or questions on [the ACCESS-Hive forum][hive-forum].

[hh5_mynci]: https://my.nci.org.au/mancini/project/hh5
[ks32_mynci]: https://my.nci.org.au/mancini/project/ks32
[bench_example]: https://github.com/CABLE-LSM/bench_example.git
[config_options]: config_options.md
[hive-forum]: https://forum.access-hive.org.au
[issues-benchcab]: https://github.com/CABLE-LSM/benchcab/issues

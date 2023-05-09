# User Guide

In this guide, we will describe:

- how to install the package
- how to use the software, including any requirements
- the different modes supported by the software

`benchcab` has been designed to work on NCI machine exclusively. It might be extended later on to other systems.

!!! warning "Limitations"
    Currently, 

    * `benchcab` can only run simulations at flux sites. 
    * spin-up for CASA simulations are not supported.
## Pre-requisites

To use `benchcab`, you need to join the following projects at NCI:

- [ks32][ks32_mynci]
- [hh5][hh5_mynci]

## Installation

The package is already installed for you in the Conda environments under the hh5 project. You simply need to load the module for the conda environment:

```bash
   module use /g/data/hh5/public/modules
   module load conda/analysis3-unstable
```

You need to load the module on each new session at NCI on login or compute nodes.

!!! Tip "Save the module location"

    You should not put any `module load` or `module add` commands in your `$HOME/.bashrc` file. But you can safely store the `module use /g/data/hh5/public/modules` command in your `$HOME/.bashrc` file. This means you won't have to type this line again in other sessions you open on Gadi.

## Usage

`benchcab` allows you to run an ensemble of configurations for CABLE using any number of code versions. `benchcab` can be used along 3 major modes:

* *regression test:* running 2 versions of CABLE wih the same standard set of science configurations.
* *new feature:* running 2 versions of CABLE with the same standard set of science configurations except one version is patched to use a new feature.
* *ensemble run:* running any number of versions of CABLE with the same set of customised science configurations.

The regression and new feature run modes should be used as necessary when evaluating new development in CABLE.

The code will: (i) check out and (ii) build the code branches. Then it will run each executable across N standard science configurations for a given number of sites. It is possible to produce some plots locally from the output produced. But [the modelevaluation website](https://modelevaluation.org/) can be used for further benchmarking and evaluation.

### Create a work directory

#### Choose a location

You can run the benchmark from any directory you want under `/scratch` or `/g/data`. `/scratch` is preferred as the data in the run directory does not need to be preserved for a long time. The code will create sub-directories as needed. Please ensure you have enough space to store the CABLE outputs in your directory, at least temporary, until you upload them to [modelevaluation.org](https://modelevaluation.org/). You will need about 33GB for the outputs for the `forty-two-site` experiment (with 8 different science configurations).

!!! Warning "The HOME directory is unsuitable"
    
    Do not use your $HOME directory to contain the work directory as it does not have enough space to contain the outputs.

#### Setup the work directory

The simplest is to clone an existing work directory with git and then adapt it to your case. Such [an example work directory][bench_example] is available on GitHub under the CABLE-LSM organisation.
```bash
git clone git@github.com:CABLE-LSM/bench_example.git
```

Once the work directory is cloned, you will need to adapt the `config.yaml` file to your case. Refer to [the description of the options][config_options] for this file.


## Run the simulations

Change directory into the cloned example work directory
```bash
cd bench_example
```

!!! warning
    `benchcab` will stop if it is not run within a work directory with the proper structure.


Currently, `benchcab` can only run CABLE for flux sites. To run the flux site tests, run

```bash
benchcab run
```

The tool will follow the steps:

1. Checkout the code branches. The codes will be stored under `src/` directory in your work directory. The sub-directories are created automatically.
2. Compile the source code from all branches
3. Setup and launch a PBS job to run the simulations in parallel. When `benchcab` launches the PBS job, it will print out the job ID to the terminal. You can check the status of the job with `qstat`. `benchcab` will not warn you when the simulations are over.

For help on the available options for `benchcab`:

```bash
benchcab -h
```

!!! Tip
    It is possible to run each step of the workflow separately using sub-commands for `benchcab`. Refer to the help message to learn more.

## Directory structure and files

The following files and directories are created when `benchcab run` executes successfully:
```
.
├── benchmark_cable_qsub.sh
├── benchmark_cable_qsub.sh.o<jobid>
├── rev_number-1.log
├── runs
│   └── site
│       ├── logs
│       │   ├── <task>_log.txt
│       │   └── ...
│       ├── outputs
│       │   ├── <task>_out.nc
│       │   └── ...
│       └── tasks
│           ├── <task>
│           │   ├── cable (executable)
│           │   ├── cable.nml
│           │   ├── cable_soilparm.nml
│           │   └── pft_params.nml
│           └── ...
└── src
    ├── CABLE-AUX
    ├── <realisation-0>
    └── <realisation-1>
```

The `benchmark_cable_qsub.sh` file is the job script submitted to run the test suite and `benchmark_cable_qsub.sh.o<jobid>` contains the job's standard output/error stream.

The `rev_number-*.log` file keeps a record of the revision numbers used for each realisation specified in the config file.

The `src` directory contains the source code checked out from SVN for each branch specified in the config file (labelled `realisation-*` above) and the CABLE-AUX branch.

The `runs/site` directory contains the log files, output files, and tasks for running CABLE. CABLE runs are organised into tasks where a task consists of a branch (realisation), a meteorological forcing, and a science configuration. In the above directory structure, `<task>` uses the following naming convention:
```
<met_file_basename>_R<realisation_key>_S<science_config_key>
```
where `met_file_base_name` is the base file name of the meteorological forcing file in the FLUXNET dataset, `realisation_key` is the branch key specified in the config file, and `science_config_key` identifies the science configuration used.

The `runs/site/tasks/<task>` directory contains the executable, the input files for each task and the recorded standard output from the CABLE model run.

The output files and log files for all tasks are stored in the `runs/site/outputs` and `runs/site/logs` directories respectively.

!!! warning "Re-running `benchcab` multiple times in the same working directory"
    We recommend the user to manually delete the generated files when re-running `benchcab`. Re-running `benchcab` multiple times in the same working directory is currently not yet supported (see issue [CABLE-LSM/benchcab#20](https://github.com/CABLE-LSM/benchcab/issues/20)). To clean the current working directory, run the following command in the working directory
    ```bash
    rm benchmark_cable_qsub.sh* rev_number-*; rm -rf runs/ src/
    ```

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

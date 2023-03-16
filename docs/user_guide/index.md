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

The package is already installed for you in the Conda environments under hh5. For access:

1. [Join the hh5 project][mynci_hh5] if you are not yet a member
2. Load the module for the conda environment:

   ```bash
   module use /g/data/hh5/public/modules
   module load conda
   ```

You need to load the module on each new session at NCI on login or compute nodes.

## Usage

`benchcab` will run the exact same configurations on two CABLE branches specified by the user, e.g. a user branch (with personal changes) against the head of the trunk. The results should be attached with all new [tickets](https://trac.nci.org.au/trac/cable/report/1).

The code will: (i) check out and (ii) build the code branches. Then it will run each executable across N standard science configurations for a given number of sites. It is possible to produce some plots locally from the output produced. But [the modelevaluation website](https://modelevaluation.org/) can be used for further benchmarking and evaluation.

### Create a work directory

#### Choose a location

You can run the benchmark from any directory you want under /scratch or /g/data. /scratch is preferred as the data in the run directory does not need to be preserved for the long run. The code will create sub-directories as needed. Please ensure you have enough space to store the CABLE outputs in your directory, at least temporary until you upload them to [modelevaluation.org](https://modelevaluation.org/). You will need about 70GB.

!!! Warning "The HOME directory is unsuitable"
    
    Do not use your $HOME directory to contain the work directory as it does not have enough space to contain the outputs.

#### Clone an existing work directory as example
             u
The simplest is to start from an existing work directory and then adapt it to your case. Such [an example work directory][bench_example] is stored in the CABLE-LSM organisation in GitHub.
  
1. **Update the `config.yaml` file to suit your case**

## Run the benchmarking
### Start the benchmarking process
Once you have a configuration file, you need to load the modules for Python:
```
module use /g/data/hh5/public/modules
module load conda/analysis3-unstable
```
Then you simply launch the benchmarking:
```
benchcab
```
For help on the available options for the benchmarking:
```
benchcab -h
```

Note: This line
```
module use /g/data/hh5/public/modules
```
can be safely added anywhere in your $HOME/.bashrc file. You then need to log out and back in for it to take effect. If you do so, you can simply load the Python module with `module load` and you do not have to type the `module use` line everytime. It is not recommended to put any `module load` lines in your $HOME/.bashrc file however.

### Check the status
The benchmarking will follow the steps:
1. Checkout both branches. The codes will be stored under `src/` directory in your work directory. The directories are created automatically.
1. Compile the source code from both branches
1. Setup and launch a PBS job to run the simulations in parallel. The simulation inputs and outputs are stored under `runs/site/`. The directories are created automatically.

When the benchmarking will launch the PBS job, it will print out the job id to screen. You can check the status of the job with `qstat`.
## Use modelevaluation.org
Once the benchmarking has finished running all the simulations, you need to upload the output files to modelevaluation.org. The output files can be found under `runs/site/outputs`.

**Process still to be documented**

## Contacts
Please enter your questions as issues or discussions on the Github repository.



[hh5_mynci]: https://my.nci.org.au/mancini/project/hh5
[ks32_mynci]: https://my.nci.org.au/mancini/project/ks32
[bench_example]: https://github.com/CABLE-LSM/bench_example.git
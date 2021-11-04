# CABLE benchmarking

Repository to benchmark a user branch (with personal changes) against the head of the trunk. The results should be attached with all new [tickets](https://trac.nci.org.au/trac/cable/report/1).

The code will: (i) check out; (ii) build; and (iii) run both the head of the trunk and the user's personal branch across N standard science configurations. It is possible to produce some plots locally. But the outputs should be uploaded to [the modelevaluation website](https://modelevaluation.org/) for further benchmarking and evaluation.

## Permissions
To run the benchmarking, you will need access to the following projects at NCI:
* w35
* wd9
* hh5
You can request access via [my.nci.org.au](https://my.nci.org.au/mancini/login?next=/mancini/)
## Get the benchmarking code and run directory
Clone the directory to your preferred location:

    $ git clone https://github.com/ccarouge/CABLE_benchmarking.git

## Setup the benchmarking
### Update user_options.py
You will need to update the following entries in this file:
* user and qsub information
* name of the user branch
* paths to run the experiments
* list of met forcings to use
* list of science configurations to use
#### **qsub information**
It is possible to run the benchmarking on the login nodes or the compute nodes. To run all the stations, you will need to use the compute node. If you want to use the compute nodes, please update the information for the qsub script.

### **Name of the user branch**
Give the name of your branch in the `repo2` variable. And leave `share_branch=False`.
#### **Paths to run the experiments**
By default, the experiments will be setup in the benchmarking directory. It will create the following sub-directories:
* src: contains the source code for the trunk and the user branch
* runs: used to run the different experiments.
  * runs/namelists: store all the namelists
  * runs/logs: store a log file per experiment
  * runs/outputs: store a netCDF output per experiment

#### **List of met forcings to use**
The benchmarking should be done using data under `/g/data/w35/Shared_data/Observations/Fluxnet_data/Post-processed_PLUMBER2_outputs/Nc_files/Met/` 

#### **List of science configurations to use***
Each science configuration is listed using a Python dictionary with the format:
```
sci5 = {
    "cable_user%GS_SWITCH": "'medlyn'",
    "cable_user%FWSOIL_SWITCH": "'Haverd2013'",
}
```
You can choose the names you want for those dictionaries.

You then choose which science configurations to run using the `sci_configs` list:
```
sci_configs = [sci1, sci2]
```
Each element of the list is one of the science configuration defined previously.

## Run the benchmarking
Once you have updated `user_options.py`, you simply need to run on the command line:
```
./run_site_comparison.py 
```
## Contacts
Preferably enter your questions as issues or discussions on the Github repository.
* [Martin De Kauwe](http://mdekauwe.github.io/).
* [Gab Abramowitz](http://web.science.unsw.edu.au/~gabrielabramowitz/UNSW_homepage/Gab_Abramowitz_home_page.html).


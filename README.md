# CABLE benchmarking

Repository to benchmark CABLE. The benchmark will run the exact same configurations on two CABLE branches specified by the user, e.g. a user branch (with personal changes) against the head of the trunk. The results should be attached with all new [tickets](https://trac.nci.org.au/trac/cable/report/1).

The code will: (i) check out; (ii) build; and (iii) run branches across N standard science configurations. It is possible to produce some plots locally. But the outputs should be uploaded to [the modelevaluation website](https://modelevaluation.org/) for further benchmarking and evaluation.

## Permissions
To run the benchmarking, you will need access to the following projects at NCI:
* ua8
* wd9
* hh5

You can request access via [my.nci.org.au](https://my.nci.org.au/mancini/login?next=/mancini/). All of those projects accept all requests by default.

## Create a run directory.
1. **Choose a run directory.** 
You can run the benchmark from any directory you want. The code will create sub-directories as needed. Please ensure you have enough space to store the CABLE outputs in your directory, at least temporary until you upload them to [modelevaluation.org](https://modelevaluation.org/).

1. **Create a config file in this directory.** The default name is `config.yaml` but any name can be specified at run time. This file follows the YAML format. You can find an example configuration file [here](https://github.com/CABLE-LSM/bench_example.git) 

## Run the benchmarking
Once you have a configuration file, you need to load the modules for Python:
```
module use /g/data/hh5/public/modules
module load conda
```
Then you simply launch the benchmarking:
```
benchcab
```
For help on the available options for the benchmarking:
```
benchcab -h
```
## Contacts
Please enter your questions as issues or discussions on the Github repository.


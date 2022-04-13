# CABLE benchmarking

Repository to benchmark CABLE. The benchmark will run the exact same configurations on two CABLE branches specified by the user, e.g. a user branch (with personal changes) against the head of the trunk. The results should be attached with all new [tickets](https://trac.nci.org.au/trac/cable/report/1).

The code will: (i) check out; (ii) build; and (iii) run branches across N standard science configurations. It is possible to produce some plots locally. But the outputs should be uploaded to [the modelevaluation website](https://modelevaluation.org/) for further benchmarking and evaluation.

For the moment, the benchmarking only works on NCI supercomputer.
## Permissions
To run the benchmarking, you will need access to the following projects at NCI:
* ks32
* wd9
* hh5

You can request access via [my.nci.org.au](https://my.nci.org.au/mancini/login?next=/mancini/). All of those projects accept all requests by default.

## Create a work directory.
1. **Choose a work directory.** 
You can run the benchmark from any directory you want. The code will create sub-directories as needed. Please ensure you have enough space to store the CABLE outputs in your directory, at least temporary until you upload them to [modelevaluation.org](https://modelevaluation.org/). You will need about 70GB.

1. **Create a config file in the work directory.** 
   The default name is `config.yaml` but any name can be specified at run time. This file follows the YAML format. You can find an example configuration file [here](https://github.com/CABLE-LSM/bench_example.git) 
  
1. **Create a science configuration file in the work directory.**
   The default name is `site_configs.yaml` but any name can be specified at run time. This file follows the YAML format. You can find an example science configuration file [here](https://github.com/CABLE-LSM/bench_example.git)

## Run the benchmarking
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
## Contacts
Please enter your questions as issues or discussions on the Github repository.


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
You will need to update the following entries in `user_options.py`:
* user information
* name of the user branch
### user information
The program needs to know your user login name and the project you want to use to run the benchmarking
### Name of the user branch
Give the name of your branch in the `repo2` variable.
 
## Run the benchmarking
Once you have updated `user_options.py`, you need to load the modules for Python:
```
module use /g/data/hh5/public/modules
module load conda
```
Then you simply need to run on the command line:
```
./run_site_comparison.py 
```

## Contacts
Preferably enter your questions as issues or discussions on the Github repository.
* [Martin De Kauwe](http://mdekauwe.github.io/).
* [Gab Abramowitz](http://web.science.unsw.edu.au/~gabrielabramowitz/UNSW_homepage/Gab_Abramowitz_home_page.html).


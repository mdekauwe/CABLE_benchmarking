# CABLE benchmarking

Repository to benchmark a user branch (with personal changes) against the head of the trunk. The results should be attached with all new [tickets](https://trac.nci.org.au/trac/cable/report/1).

The code will: (i) check out; (ii) build; and (iii) run both the head of the trunk and the user's personal branch across N standard science configurations.

NB. the code is flexible enough that "trunk" could be any branch, allowing the user to compare across personal branches.

## Multi-site comparison

Runs both cable executables (trunk and the user's branch) across a suite of FLUXNET sites, plots seasonal cycles and comparison benchmark statistics. Whilst these plots are generated locally, the results of each repository should be uploaded to
[Gab's benchmarking website](https://modelevaluation.org/) for further benchmarking and evaluation.

To run the multi-site comparison, please update the relevant entries (paths, library locations, etc) within:

    $ run_comparison.py

This should be pretty self-evident, the expectation is that the user will only change entries between:

    #------------- User set stuff ------------- #
    user = "XXX579"

    ...
    # ------------------------------------------- #

In many cases we recommend you don't change the defaults, e.g. (however things **should** be robust to you doing as you please)

    src_dir = "src"
    run_dir = "runs"
    log_dir = "logs"
    plot_dir = "plots"

To pass different science configurations, the code expects the details to be passed as a [dictonary](https://docs.python.org/2/tutorial/datastructures.html#dictionaries). All options passed are added to the cable namelist file, so it is pretty flexible.

There are a couple of potential gotchas:

To pass a string flag, you need a double set of quotation marks as shown below. If you encounter a problem this is likely to be the issue ...

    sci = {
        "cable_user%GS_SWITCH": "'medlyn'",
    }

This isn't an issue for other flags, e.g.

    sci = {
        "output%restart": ".FALSE.",
        "fixedCO2": "400.0",
    }

To run a single site, you just need to set which site you wish to run in the python list variable, e.g.

    met_subset = ['TumbaFluxnet.1.4_met.nc']

This structure is very flexible, so if you want to run three sites, you just expand the entry:

    met_subset = ['TumbaFluxnet.1.4_met.nc', 'HarvardFluxnet.1.4_met.nc','HowardFluxnet.1.4_met.nc']

And to simply run all the met sites in a directory, leave the list empty:

    met_subset = []

Finally, if you are running more than a single-site, there are two MPI flags you should consider setting to speed up things:

    mpi = True
    num_cores = 4 # set to a number, if None it will use all cores...!



## Global comparison

Coming soon ...


## Code dependencies

The code has been written such that it has very few dependancies to ease personal set up. Nevertheless, it does depend on a few fairly standard python libraries:

* [numpy](http://numpy.scipy.org/)
* [pandas](https://pandas.pydata.org/)
* [xarray](http://xarray.pydata.org/en/stable/)

All of which can be easily built using [anaconda](https://www.anaconda.com/distribution/).

To install on raijin in your personal space:

Download [the linux anaconda file](https://www.anaconda.com/download/#linux). Then create an environment called "science" (or whatever sensible name springs to mind).

    $ conda create --name science python=3

then

    $ source activate science

then

    $ conda install docopt xarray matplotlib pandas scipy numpy

If you're working locally on a mac or linux machine, you could as easily use your favourite package manager (e.g. macports, apt-get, etc).

## Contacts
* [Martin De Kauwe](http://mdekauwe.github.io/).
* [Gab Abramowitz](http://web.science.unsw.edu.au/~gabrielabramowitz/UNSW_homepage/Gab_Abramowitz_home_page.html).

# User Guide

In this guide, we will describe:

- how to install the package
- how to use the software, including any requirements
- the different modes supported by the software

## Installation

### At NCI

The package is already installed for you in the Conda environments under hh5. For access:

1. [Join the hh5 project][mynci_hh5] if you are not yet a member
2. Load the module for the conda environment:

   ```bash
   module use /g/data/hh5/public/modules
   module load conda
   ```

You need to load the module for each new session at NCI on login or compute nodes.

### On other machines

The package is distributed via Anaconda on the ACCESS-NRI channel. To install the package in an existing conda environment:

```bash
conda install -c accessnri benchcab
```

[mynci_hh5]: https://my.nci.org.au/mancini/project/hh5
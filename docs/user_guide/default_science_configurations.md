# Default science configurations

A set of science configurations is defined in `benchcab`. This allows for running standardised testing of different version of CABLE. Test results using this default set are required for submission of new code development in CABLE. Occasionally, some code developments might also require test results using a different set of configurations to document their effect on the model results.

The science configurations are given as patches to apply to a default namelist file. You can find [the default namelist file](https://github.com/CABLE-LSM/bench_example/blob/dev/namelists/cable.nml) in the `bench_example` repository. Each science configuration is identified as "S<N>" where N in an integer, starting from 0 for the first listed configuration.

Currently, the default science configurations are defined internally by the following data structure:
```python
DEFAULT_SCIENCE_CONFIGURATIONS = [
    { # S0 configuration
        "cable": {
            "cable_user": {
                "GS_SWITCH": "medlyn",
                "FWSOIL_SWITCH": "Haverd2013",
            }
        }
    },
    { # S1 configuration
        "cable": {
            "cable_user": {
                "GS_SWITCH": "leuning",
                "FWSOIL_SWITCH": "Haverd2013",
            }
        }
    },
    { # S2 configuration
        "cable": {
            "cable_user": {
                "GS_SWITCH": "medlyn",
                "FWSOIL_SWITCH": "standard",
            }
        }
    },
    { # S3 configuration
        "cable": {
            "cable_user": {
                "GS_SWITCH": "leuning",
                "FWSOIL_SWITCH": "standard",
            }
        }
    },
]
```

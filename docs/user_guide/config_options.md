# config.yaml options

!!! note
    All keys listed here are required unless stated otherwise.

## Technical details

`user`

: NCI user ID to find the CABLE branch on SVN and run the simulations.

`project`

: NCI project ID to charge the simulations to.

`modules`

: NCI modules to use for compiling CABLE

## Simulations details

`realisations`

: Entries for each of the two CABLE branches to use (specified by keys `0` and `1`). Each entry contains the following keys:

    `name`
    : The base name of the branch on SVN, i.e. relative to:

        - `https://trac.nci.org.au/svn/cable` for the trunk
        - `https://trac.nci.org.au/svn/cable/branches/Share` for a shared branch
        - `https://trac.nci.org.au/svn/cable/branches/Users/{user_id}` for a user branch

    `revision`
    : The revision number to use for the branch.
    : This key is **optional** and can be omitted from the config file. By default `revision` is set to `-1` which indicates the HEAD of the branch to be used. The user may also explicitly specify `-1` to use the HEAD of the branch.

    `trunk`
    : Boolean value set to `True` if this branch is the trunk for CABLE. Else set to `False`.

    `share_branch`
    : Boolean value set to `True` if this branch is under `branches/Share` in the CABLE SVN repository. Else set to `False`.

    `patch`
    : Branch-specific namelist settings for `cable.nml`. Settings specified in `patch` get "patched" to the base namelist settings used for both branches. Any namelist settings specified here will overwrite settings defined in the default namelist file and in the science configurations. This means these settings will be set as stipulated in the `patch` for this branch for all science configurations run by `benchcab`.
    : The `patch` key must be a dictionary like data structure that is compliant with the [`f90nml`][f90nml-github] python package.
    : This key is **optional** and can be omitted from the config file. By default `patch` is empty and does not modify the namelist file.

    Example:
    ```yaml
    realisations: {
      0: { # head of the trunk
        name: "trunk",
        revision: -1,
        trunk: True,
        share_branch: False,
      },
      1: { # some development branch
        name: "test-branch",
        revision: -1,
        trunk: False,
        share_branch: False,
        patch: {
          cable: {
            cable_user: {
              FWSOIL_SWITCH: "Lai and Ktaul 2000"
            }
          }
        }
      }
    }
    ```

`experiment`

: Type of experiment to run. Experiments are defined in the **NRI Land testing** workspace on [modelevaluation.org][meorg]. This key specifies the met forcing files used in the test suite. To choose from:

    - [`forty-two-site-test`][forty-two-me]: to run simulations using 42 FLUXNET sites
    - [`five-site-test`][five-me]: to run simulations using 5 FLUXNET sites
    - `AU-Tum`: to run simulations at the Tumbarumba (AU) site
    - `AU-How`: to run simulations at the Howard Spring (AU) site
    - `FI-Hyy`: to run simulations at the Hyytiala (FI) site
    - `US-Var`: to run simulations at the Vaira Ranch-Ione (US) site
    - `US-Whs`: to run simulations at the Walnut Gulch Lucky Hills Shrub (US) site

`science_configurations`

: User defined science configurations. This key is **optional** and can be omitted from the config file. Science configurations that are specified here will replace the default science configurations.
: Example:
```yaml
science_configurations: {
  sci0: {
    cable: {
      cable_user: {
        GS_SWITCH: "medlyn",
        FWSOIL_SWITCH: "Haverd2013"
      }
    }
  },
  sci1: {
    cable: {
      cable_user: {
        GS_SWITCH: "leuning",
        FWSOIL_SWITCH: "Haverd2013"
      }
    }
  }
}
```

: Currently, the default science configurations are defined internally by the following data structure:
```python
DEFAULT_SCIENCE_CONFIGURATIONS = {
    "sci0": {"cable": {"cable_user": {"GS_SWITCH": "medlyn"}}},
    "sci1": {"cable": {"cable_user": {"GS_SWITCH": "leuning"}}},
    "sci2": {"cable": {"cable_user": {"FWSOIL_SWITCH": "Haverd2013"}}},
    "sci3": {"cable": {"cable_user": {"FWSOIL_SWITCH": "standard"}}},
    "sci4": {
        "cable": {
            "cable_user": {
                "GS_SWITCH": "medlyn",
                "FWSOIL_SWITCH": "Haverd2013",
            }
        }
    },
    "sci5": {
        "cable": {
            "cable_user": {
                "GS_SWITCH": "leuning",
                "FWSOIL_SWITCH": "Haverd2013",
            }
        }
    },
    "sci6": {
        "cable": {
            "cable_user": {
                "GS_SWITCH": "medlyn",
                "FWSOIL_SWITCH": "standard",
            }
        }
    },
    "sci7": {
        "cable": {
            "cable_user": {
                "GS_SWITCH": "leuning",
                "FWSOIL_SWITCH": "standard",
            }
        }
    },
}
```

[meorg]: https://modelevaluation.org/
[forty-two-me]: https://modelevaluation.org/experiment/display/urTKSXEsojdvEPwdR
[five-me]: https://modelevaluation.org/experiment/display/xNZx2hSvn4PMKAa9R
[f90nml-github]: https://github.com/marshallward/f90nml
# config.yaml options

!!! note "Required options"
    All keys listed here are required unless stated otherwise.

The different running modes of `benchcab` are solely dependent on the options used in `config.yaml`. The following gives some typical ways to configure `benchcab` for each mode, but the tool is not restricted to these choices of options:

=== "Regression test"

    For this test, you want to:

    * specify the details of 2 branches of CABLE
    * do not specify a `patch`
    * use the default set of science options, i.e. do not specify science options in `config.yaml`
    * choose the `experiment` suitable for your stage of development. A run with the `forty-two-site-test` will be required for submissions of new development to CABLE.

=== "New feature test"

    For this test, you want to:

    * specify the details of 2 branches of CABLE
    * specify a `patch` for **one** of the branches
    * use the default set of science options, i.e. do not specify science options in `config.yaml`
    * choose the `experiment` suitable for your stage of development. A run with the `forty-two-site-test` will be required for submissions of new development to CABLE.


=== "Ensemble mode"

    This running mode is quite open to customisations:

    * specify the number of CABLE's branches you need
    * use `patch` on branches as required
    * specify the science configurations you want to run. `patch` will be applied on top of the science configurations listed.


## Technical options

### `user`

: NCI user ID to find the CABLE branch on SVN and run the simulations.

### `project`

: NCI project ID to charge the simulations to.

### `modules`

: NCI modules to use for compiling CABLE

## Simulations options

### `realisations`

: Entries for each CABLE branch to use. Each entry is a dictionary, {}, that contains the following keys:

#### `name`

: The base name of the branch on SVN, i.e. relative to:

    - `https://trac.nci.org.au/svn/cable` for the trunk
    - `https://trac.nci.org.au/svn/cable/branches/Share` for a shared branch
    - `https://trac.nci.org.au/svn/cable/branches/Users/{user_id}` for a user branch

#### `trunk`

: Boolean value set to `True` if this branch is the trunk for CABLE. Else set to `False`.


#### `share_branch`

: Boolean value set to `True` if this branch is under `branches/Share` in the CABLE SVN repository. Else set to `False`.

#### `build_script`

: This key is **optional**. The path to a custom script to build the code in that branch, relative to the name of the branch. E.g: "offline/build.sh" to specify a build script under <name of branch>/offline/. The script specified with this option will run as is, ignoring the entries in the `modules` key of `config.yaml` file.

##### `revision`

: The revision number to use for the branch.
: This key is **optional** and can be omitted from the config file. By default `revision` is set to `-1` which indicates the HEAD of the branch to be used. The user may also explicitly specify `-1` to use the HEAD of the branch.

#### `patch`

: Branch-specific namelist settings for `cable.nml`. Settings specified in `patch` get "patched" to the base namelist settings used for both branches. Any namelist settings specified here will overwrite settings defined in the default namelist file and in the science configurations. This means these settings will be set as stipulated in the `patch` for this branch for all science configurations run by `benchcab`.
: The `patch` key must be a dictionary like data structure that is compliant with the [`f90nml`][f90nml-github] python package.
: This key is **optional** and can be omitted from the config file. By default `patch` is empty and does not modify the namelist file.

Example:
```yaml
realisations: [
  { # head of the trunk
    name: "trunk",
    revision: -1,
    trunk: True,
    share_branch: False,
  },
  { # some development branch
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
]
```

### `experiment`

: Type of experiment to run. Experiments are defined in the **NRI Land testing** workspace on [modelevaluation.org][meorg]. This key specifies the met forcing files used in the test suite. To choose from:

    - [`forty-two-site-test`][forty-two-me]: to run simulations using 42 FLUXNET sites
    - [`five-site-test`][five-me]: to run simulations using 5 FLUXNET sites
    - `AU-Tum`: to run simulations at the Tumbarumba (AU) site
    - `AU-How`: to run simulations at the Howard Spring (AU) site
    - `FI-Hyy`: to run simulations at the Hyytiala (FI) site
    - `US-Var`: to run simulations at the Vaira Ranch-Ione (US) site
    - `US-Whs`: to run simulations at the Walnut Gulch Lucky Hills Shrub (US) site

### `science_configurations`

: User defined science configurations. This key is **optional** and can be omitted from the config file. Science configurations that are specified here will replace [the default science configurations](default_science_configurations.md).
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

[meorg]: https://modelevaluation.org/
[forty-two-me]: https://modelevaluation.org/experiment/display/urTKSXEsojdvEPwdR
[five-me]: https://modelevaluation.org/experiment/display/xNZx2hSvn4PMKAa9R
[f90nml-github]: https://github.com/marshallward/f90nml
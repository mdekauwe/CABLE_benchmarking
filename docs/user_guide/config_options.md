# config.yaml options

!!! note "Required options"
    All keys listed here are required unless stated otherwise.

The different running modes of `benchcab` are solely dependent on the options used in `config.yaml`. The following gives some typical ways to configure `benchcab` for each mode, but the tool is not restricted to these choices of options:

=== "Regression test"

    For this test, you want to:

    * Specify the details of two branches of CABLE
    * Do not specify a [`patch`](#`patch`)
    * Use the default set of science options, i.e. do not specify [`science_configurations`](#`science_configurations`) in `config.yaml`
    * Choose the [`experiment`](#`experiment`) suitable for your stage of development. A run with the `forty-two-site-test` will be required for submissions of new development to CABLE.

=== "New feature test"

    For this test, you want to:

    * Specify the details of two branches of CABLE
    * Specify a [`patch`](#`patch`) for **one** of the branches
    * Use the default set of science options, i.e. do not specify [`science_configurations`](#`science_configurations`) in `config.yaml`
    * Choose the [`experiment`](#`experiment`) suitable for your stage of development. A run with the `forty-two-site-test` will be required for submissions of new development to CABLE.


=== "Ensemble mode"

    This running mode is quite open to customisations:

    * Specify the number of CABLE's branches you need
    * Use [`patch`](#`patch`) on branches as required
    * Specify the [science configurations](#`science_configurations`) you want to run. [`patch`](#`patch`) will be applied on top of the science configurations listed.


## Technical options

### `project`

: NCI project ID to charge the simulations to.

### `modules`

: NCI modules to use for compiling CABLE

### `pbs`

: Contains settings specific to the PBS scheduler at NCI for the PBS script running the CABLE simulations at FLUXNET sites and the bitwise comparison for these simulations.

#### `ncpus`

: The number of CPU cores to allocate for the PBS job, i.e. the `-l ncpus=<4>` PBS flag (see [PBS Directives Explained][nci-pbs-directives]). 
: This key is **optional** and can be omitted from the config file. By default `ncpus` is set to `18`.

#### `mem`

: The total memory limit for the PBS job, i.e. the `-l mem=<10GB>` PBS flag (see [PBS Directives Explained][nci-pbs-directives]).
: This key is **optional** and can be omitted from the config file. By default `mem` is set to `30GB`.

#### `walltime`

: The wall clock time limit for the PBS job, i.e. `-l walltime=<HH:MM:SS>` PBS flag (see [PBS Directives Explained][nci-pbs-directives]).
: This key is **optional** and can be omitted from the config file. By default `walltime` is set to `6:00:00`.

#### `storage`

: A list of extra storage flags required for the PBS job, i.e. `-l storage=<scratch/a00>` (see [PBS Directives Explained][nci-pbs-directives]).
: This key is **optional** and can be omitted from the config file. By default `storage` is set to `[]`.

Example:
```yaml
pbs:
  ncpus: 16
  mem: 64GB
  walltime: 00:01:00
  storage: [scratch/a00, gdata/xy11]
```

### `multiprocessing`

: Enables or disables multiprocessing for executing embarrassingly parallel tasks.
: This key is **optional** and can be omitted from the config file. By default `multiprocessing` is set to `True`.


## Simulations options

### `realisations`

: Entries for each CABLE branch to use. Each entry is a dictionary, `{}`, that contains the following keys:

#### `path`

: The path of the branch relative to the SVN root of the CABLE repository (`https://trac.nci.org.au/svn/cable`).
: Example:

    - to checkout `https://trac.nci.org.au/svn/cable/trunk`, set `path: "trunk"`
    - to checkout `https://trac.nci.org.au/svn/cable/branches/Users/foo/my_branch`, set `path: "branches/Users/foo/my_branch"`

#### `name`

: An alias name used internally by `benchcab` for the branch. The `name` key also specifies the directory name when checking out the branch, that is, `name` is the optional `PATH` argument to `svn checkout`.
: This key is **optional** and can be omitted from the config file. By default `name` is set to the base name of [`path`](#`path`).

#### `build_script`

: This key is **optional**. The path to a custom shell script to build the code in that branch, relative to the name of the branch. **Note:** any lines in the provided shell script that call the [environment modules API][environment-modules] will be ignored. To specify modules to use for the build script, please specify them using the [`modules`](#`modules`) key.
: Example: `build_script: offline/build.sh` to specify a build script under `<name_of_branch>/offline/`.

#### `revision`

: The revision number to use for the branch.
: This key is **optional** and can be omitted from the config file (in which case the HEAD of the branch is used).

#### `patch`

: Branch-specific namelist settings for `cable.nml`. Settings specified in `patch` get "patched" to the base namelist settings used for both branches. Any namelist settings specified here will overwrite settings defined in the default namelist file and in the science configurations. This means these settings will be set as stipulated in the `patch` for this branch for all science configurations run by `benchcab`.
: The `patch` key must be a dictionary like data structure that is compliant with the [`f90nml`][f90nml-github] python package.
: This key is **optional** and can be omitted from the config file (in which case `patch` does not modify the namelist file).

Example:
```yaml
realisations: [
  { # head of the trunk
    path: "trunk",
  },
  { # some development branch
    path: "branches/Users/foo/my_branch",
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

: User defined science configurations. This key is **optional** and can be omitted from the config file. Science configurations that are specified here will replace [the default science configurations](default_science_configurations.md). In the output filenames, each configuration is identified with S<N\> where N is an integer starting from 0 for the first listed configuration and increasing by 1 for each subsequent configuration.
: Example:
```yaml
science_configurations: [
  { # S0 configuration
    cable: {
      cable_user: {
        GS_SWITCH: "medlyn",
        FWSOIL_SWITCH: "Haverd2013"
      }
    }
  },
  { # S1 configuration
    cable: {
      cable_user: {
        GS_SWITCH: "leuning",
        FWSOIL_SWITCH: "Haverd2013"
      }
    }
  }
]
```

[meorg]: https://modelevaluation.org/
[forty-two-me]: https://modelevaluation.org/experiment/display/urTKSXEsojdvEPwdR
[five-me]: https://modelevaluation.org/experiment/display/xNZx2hSvn4PMKAa9R
[f90nml-github]: https://github.com/marshallward/f90nml
[environment-modules]: https://modules.sourceforge.net/
[nci-pbs-directives]: https://opus.nci.org.au/display/Help/PBS+Directives+Explained
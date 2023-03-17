# config.yaml options

## Technical details

`project`

:    NCI project ID to charge the simulations to.

`user`

:    NCI user ID to find the CABLE branch on SVN and run the simulations.

`modules`

:    NCI modules to use for compiling CABLE

## Simulations details

`realisations`

: Detail of the branches to use for the evaluation. It contains entries for each of the two branches ("0" and "1"). For each branch, you need to give:

    - `name`: the name of the branch on SVN, relative to:
        - https://trac.nci.org.au/svn/cable for the trunk
        - https://trac.nci.org.au/svn/cable/branches/Share for a shared branch
        - https://trac.nci.org.au/svn/cable/branches/Users/{user_id} for a user branch
    - `revision`: Default=-1. Revision version to use for the branch. Specify "-1" to use the HEAD of the branch.
    - `trunk`: True if this branch is the trunk for CABLE. Else set to False.
    - `share_branch`: True if this branch is under `branches/Share` in the CABLE svn repository, else set to False.

`experiment`

: Type of experiment to run. To choose from:

    - [forty-two-site-test][forty-two-me]: to run simulations using 42 FLUXNET sites
    - [five-site-test][five-me]: to run simulations using 5 FLUXNET sites
    - AU-Tum: to run simulations at the Tumbarumba (AU) site
    - AU-How: to run simulations at the Howard Spring (AU) site
    - FI-Hyy: to run simulations at the Hyytiala (FI) site
    - US-Var: to run simulations at the Vaira Ranch-Ione (US) site
    - US-Whs: to run simulations at the Walnut Gulch Lucky Hills Shrub (US) site

[forty-two-me]: https://modelevaluation.org/experiment/display/urTKSXEsojdvEPwdR
[five-me]: https://modelevaluation.org/experiment/display/xNZx2hSvn4PMKAa9R

# benchcab

[![Documentation status][readthedocs_badge]][docs] [![Test coverage][codecov_badge]][codecov_summary] [![Conda package status][conda_badge]][conda]

`benchcab` is a testing framework that tests the CABLE land surface model across a range of model configurations and model versions. The tool checks out the model versions specified by the user, builds the required executables, and runs each model version across N standard science configurations. Model outputs are then piped into a benchmark analysis via [modelevaluation.org][meorg] from which the user can assess model performance.

The full documentation is available at [benchcab.readthedocs.io][docs].

## Acknowledgements

- `benchcab` is a continuation of the efforts made by Martin De Kauwe ([@mdekauwe](https://github.com/mdekauwe)) and Gab Abramowitz ([@gabsun](https://github.com/gabsun)) in developing a CABLE benchmarking framework - we thank them for their contribution.

[conda_badge]: https://img.shields.io/conda/v/accessnri/benchcab
[codecov_badge]: https://codecov.io/gh/CABLE-LSM/benchcab/branch/master/graph/badge.svg?token=JJYE1YZDXQ
[readthedocs_badge]: https://readthedocs.org/projects/benchcab/badge
[conda]: https://anaconda.org/accessnri/benchcab
[codecov_summary]: https://codecov.io/gh/CABLE-LSM/benchcab
[docs]: https://benchcab.readthedocs.io
[meorg]: https://modelevaluation.org

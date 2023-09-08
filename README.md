# benchcab

[![codecov](https://codecov.io/gh/CABLE-LSM/benchcab/branch/master/graph/badge.svg?token=JJYE1YZDXQ)](https://codecov.io/gh/CABLE-LSM/benchcab)

`benchcab` is a testing framework that tests the CABLE land surface model across a range of model configurations and model versions. The tool checks out the model versions specified by the user, builds the required executables, and runs each model version across N standard science configurations. Model outputs are then piped into a benchmark analysis via [modelevaluation.org][meorg] from which the user can assess model performance.

The full documentation is available at [benchcab.readthedocs.io][docs].

## Acknowledgements

- `benchcab` is a continuation of the efforts made by Martin De Kauwe ([@mdekauwe](https://github.com/mdekauwe)) and Gab Abramowitz ([@gabsun](https://github.com/gabsun)) in developing a CABLE benchmarking framework - we thank them for their contribution.

[docs]: https://benchcab.readthedocs.io
[meorg]: https://modelevaluation.org

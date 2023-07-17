# Expected output from benchcab

Below you will find examples of the expected output printed by `benchcab` to the screen when running the full workflow, with `benchcab run`. 

Other sub-commands should print out part of this output.

```
$ benchcab run
Creating src directory: /scratch/tm70/sb8430/bench_example/src
Checking out repositories...
Successfully checked out trunk at revision 9550
Successfully checked out test-branch at revision 9550
Successfully checked out CABLE-AUX at revision 9550
Writing revision number info to rev_number-1.log

Compiling CABLE serially for realisation trunk...
Successfully compiled CABLE for realisation trunk
Compiling CABLE serially for realisation test-branch...
Successfully compiled CABLE for realisation test-branch

Setting up run directory tree for fluxsite tests...
Creating runs/fluxsite/logs directory: /scratch/tm70/sb8430/bench_example/runs/fluxsite/logs
Creating runs/fluxsite/outputs directory: /scratch/tm70/sb8430/bench_example/runs/fluxsite/outputs
Creating runs/fluxsite/tasks directory: /scratch/tm70/sb8430/bench_example/runs/fluxsite/tasks
Creating runs/fluxsite/analysis directory: /scratch/tm70/sb8430/bench_example/runs/fluxsite/analysis
Creating runs/fluxsite/analysis/bitwise-comparisons directory: /scratch/tm70/sb8430/bench_example/runs/fluxsite/analysis/bitwise-comparisons
Creating task directories...
Setting up tasks...
Successfully setup fluxsite tasks

Creating PBS job script to run fluxsite tasks on compute nodes: benchmark_cable_qsub.sh
PBS job submitted: 82479088.gadi-pbs
The CABLE log file for each task is written to runs/fluxsite/logs/<task_name>_log.txt
The CABLE standard output for each task is written to runs/fluxsite/tasks/<task_name>/out.txt
The NetCDF output for each task is written to runs/fluxsite/outputs/<task_name>_out.nc
```

The PBS schedule job should print out the following to the job log file:
```
Running fluxsite tasks...
Successfully ran fluxsite tasks

Running comparison tasks...
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S0_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S0_out.nc are identical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S1_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S1_out.nc are identical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S2_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S2_out.nc are identical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S3_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S3_out.nc are identical
Successfully ran comparison tasks
```

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

Setting up run directory tree for FLUXNET tests...
Creating runs/site/logs directory: /scratch/tm70/sb8430/bench_example/runs/site/logs
Creating runs/site/outputs directory: /scratch/tm70/sb8430/bench_example/runs/site/outputs
Creating runs/site/tasks directory: /scratch/tm70/sb8430/bench_example/runs/site/tasks
Creating runs/site/analysis directory: /scratch/tm70/sb8430/bench_example/runs/site/analysis
Creating runs/site/analysis/bitwise-comparisons directory: /scratch/tm70/sb8430/bench_example/runs/site/analysis/bitwise-comparisons
Creating task directories...
Setting up tasks...
Successfully setup FLUXNET tasks

Creating PBS job script to run FLUXNET tasks on compute nodes: benchmark_cable_qsub.sh
PBS job submitted: 82479088.gadi-pbs
The CABLE log file for each task is written to runs/site/logs/<task_name>_log.txt
The CABLE standard output for each task is written to runs/site/tasks/<task_name>/out.txt
The NetCDF output for each task is written to runs/site/outputs/<task_name>_out.nc
```

The PBS schedule job should print out the following to the job log file:
```
Running FLUXNET tasks...
Successfully ran FLUXNET tasks

Running comparison tasks...
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S2_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S2_out.nc are identitical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S6_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S6_out.nc are identitical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S7_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S7_out.nc are identitical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S3_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S3_out.nc are identitical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S0_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S0_out.nc are identitical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S5_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S5_out.nc are identitical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S4_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S4_out.nc are identitical
Success: files AU-Tum_2002-2017_OzFlux_Met_R0_S1_out.nc AU-Tum_2002-2017_OzFlux_Met_R1_S1_out.nc are identitical
Successfully ran comparison tasks
```

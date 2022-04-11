qsub_fname = "benchmark_cable_qsub.sh"
ncpus = 96
mem = "384GB"
wall_time = "3:00:00"

#
## MPI stuff
#
mpi = False
num_cores = ncpus  # set to a number, if None it will use all cores...!
multiprocess = True

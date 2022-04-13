qsub_fname = "benchmark_cable_qsub.sh"
ncpus = 18
mem = "30GB"
wall_time = "6:00:00"

#
## MPI stuff
#
mpi = False
num_cores = ncpus  # set to a number, if None it will use all cores...!
multiprocess = True

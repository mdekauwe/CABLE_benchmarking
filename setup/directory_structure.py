import os

#
## user directories ...
#
src_dir = "src"
aux_dir = "src/CABLE-AUX"
run_dir = "runs"
log_dir = "logs"
plot_dir = "plots"
output_dir = "outputs"
restart_dir = "restart_files"
namelist_dir = "namelists"

if not os.path.exists(src_dir):
    os.makedirs(src_dir)

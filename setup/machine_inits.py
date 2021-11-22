import user_options
import datetime
import os
import sys
import shutil
from scripts.set_default_paths import set_paths

now = datetime.datetime.now()
date = now.strftime("%d_%m_%Y")
cwd = os.getcwd()
(sysname, nodename, release, version, machine) = os.uname()

(met_dir, NCDIR, NCMOD, FC, FCMPI, CFLAGS, LD, LDFLAGS) = set_paths(nodename)

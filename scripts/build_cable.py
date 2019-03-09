#!/usr/bin/env python

"""
Build CABLE executables ...

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (09.03.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import subprocess
import datetime

class BuildCable(object):

    def __init__(self, src_dir=None, NCDIR=None, NCMOD=None, FC=None,
                 CFLAGS=None, LD=None, LDFLAGS=None):

        self.src_dir = src_dir
        self.NCDIR = NCDIR
        self.NCMOD = NCMOD
        self.FC = FC
        self.CFLAGS = CFLAGS
        self.LD = LD
        self.LDFLAGS = LDFLAGS

    def main(self, repo_name=None, trunk=False):

        build_dir = "%s/%s" % (repo_name, "offline")
        cwd = os.getcwd()
        os.chdir(os.path.join(self.src_dir, build_dir))

        ofname = self.adjust_build_script()
        self.build_cable(ofname)

        os.chdir(cwd)

    def adjust_build_script(self):

        cmd = "echo `uname -n | cut -c 1-4`"
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        host, error = p.communicate()
        host = str(host, 'utf-8').strip()
        if error is 1:
            raise("Error checking if repo exists")

        fname = "build.ksh"
        f = open(fname, "r")
        lines = f.readlines()
        f.close()

        ofname = "my_build.ksh"
        of = open(ofname, "w")

        i = 0
        while i < len(lines):
            line = lines[i]
            if 'known_hosts()' in line:
                print("known_hosts()", end="\n", file=of)
                print("{", end="\n", file=of)
                print("  set -A kh  pear jigg nXXX raij ces2 ccrc mael %s" %\
                      (str(host)), end="\n", file=of)
                print("}", end="\n\n", file=of)
                print("host_%s (){" % (host), end="\n", file=of)
                print("    export NCDIR=%s" % (self.NCDIR), end="\n", file=of)
                print("    export NCMOD=%s" % (self.NCMOD), end="\n", file=of)
                print("    export FC=%s" % (self.FC), end="\n", file=of)
                print("    export CFLAGS=%s" % (self.CFLAGS), end="\n", file=of)
                print("    export LD=%s" % (self.LD), end="\n", file=of)
                print("    export LDFLAGS=%s" % (self.LDFLAGS), end="\n", file=of)
                print("    build_build", end="\n", file=of)
                print("    cd ../", end="\n", file=of)
                print("    build_status", end="\n", file=of)

                print("}", end="\n\n", file=of)

                i += 5
            else:
                print(line, end="", file=of)
            i += 1

        of.close()

        return (ofname)

    def build_cable(self, ofname):

        cmd = "chmod +x %s" % (ofname)
        error = subprocess.call(cmd, shell=True)
        if error is 1:
            raise("Error changing file to executable")

        cmd = "./%s" % (ofname)
        error = subprocess.call(cmd, shell=True)
        if error is 1:
            raise("Error building executable")

        os.remove(ofname)

if __name__ == "__main__":

    now = datetime.datetime.now()
    date = now.strftime("%d_%m_%Y")

    #------------- Change stuff ------------- #
    src_dir = "src"
    NCDIR = '/opt/local/lib/'
    NCMOD = '/opt/local/include/'
    FC = 'gfortran'
    CFLAGS = '-O2'
    LD = "'-lnetcdf -lnetcdff'"
    LDFLAGS = "'-L/opt/local/lib -O2'"
    repo1 = "Trunk_%s" % (date)
    repo2 = "CMIP6-MOSRS"
    # ------------------------------------------- #

    B = BuildCable(src_dir=src_dir, NCDIR=NCDIR, NCMOD=NCMOD, FC=FC,
                   CFLAGS=CFLAGS, LD=LD, LDFLAGS=LDFLAGS)
    B.main(repo_name=repo1)
    B.main(repo_name=repo2)

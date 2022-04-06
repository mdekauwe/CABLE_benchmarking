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
from pathlib import Path
from typing import Iterable

class BuildCable(object):
    def __init__(
        self,
        ModToLoad:Iterable,
        src_dir=None,
        NCDIR=None,
        NCMOD=None,
        FC=None,
        CFLAGS=None,
        LD=None,
        LDFLAGS=None,
        debug=False,
        mpi=False,
    ):

        self.src_dir = src_dir
        self.NCDIR = NCDIR
        self.NCMOD = NCMOD
        self.FC = FC
        self.CFLAGS = CFLAGS
        self.LD = LD
        self.LDFLAGS = LDFLAGS
        self.debug = debug
        self.mpi = mpi
        self.ModToLoad = ModToLoad

    @staticmethod
    def find_purge_line(filelines, filename=""):
        """Find the line with module purge in the list of file lines.
        Check there is only 1 such line. Return the index of the line.

        filelines: list of strings such as returned by readlines()
        filename: name of input file"""

        purge_line = [
            purge_ind for purge_ind, ll in enumerate(filelines) if "module purge" in ll
        ]
        # Check we found only 1 module purge line.
        assert (
            len(purge_line) == 1
        ), f"{filename} should contain exactly one line with 'module purge'"
        purge_line = purge_line[0]

        return purge_line

    def add_module_load(self,lines, nindent):
        """Read in the environment file using config data.
        Add lines to load each module listed in environment file
        at the end of the list of strings, lines

        lines: list of strings
        nindent: integer, number of indent spaces to add for each line"""

        loclines = lines.copy()

        # Append new lines to the list of lines for each module
        for mod in self.ModToLoad:
            # Add newline if not in "mod"
            if "\n" not in mod:
                mod = mod + "\n"
            toadd = "".join([" " * nindent, "module load ", mod])
            loclines.append(toadd)

        return loclines

    def change_build_lines(self,filelines, filename=""):
        """Get the lines from the build script and modify them:
            - remove all the module load and module add lines
            - read in the environment file for Gadi
            - insert the module load lines for the modules in the env. file
        filelines: list of strings such as returned by readlines()
        filename: name of input file"""

        # Remove any line loading a module
        nomodulelines = [
            ll
            for ll in filelines
            if all([substring not in ll for substring in ["module load", "module add"]])
        ]

        # Find the line with "module purge"
        purge_line = self.find_purge_line(nomodulelines, filename=filename)

        # Get the indentation right: copy the indentation from the module purge line
        nindent = nomodulelines[purge_line].find("module purge")

        outlines = nomodulelines[: purge_line + 1]  # Take all lines until module purge

        # append lines to load the correct modules
        outlines = self.add_module_load(outlines, nindent)

        # add the end of the file as in the original file
        outlines.extend(nomodulelines[purge_line + 1 :])

        return outlines

    def adjust_build_script(self):

        cmd = "echo `uname -n | cut -c 1-4`"
        p = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        host, error = p.communicate()
        host = str(host, "utf-8").strip()
        if error == 1:
            raise ("Error checking if repo exists")

        # Need to customise the build script with the modules
        # we want to use.
        fname = "build3.sh"
        f = open(fname, "r")
        lines = f.readlines()
        f.close()

        if self.mpi:
            ofname = "my_build_mpi.ksh"
        else:
            ofname = "my_build.ksh"
        of = open(ofname, "w")

        # We find all the "module load" lines and remove them from
        # the list of lines.
        # Then after the line "module purge", we add a line for
        # each module listed in gadi_env.sh
        outlines = self.change_build_lines(lines, filename=fname)

        of.writelines(outlines)
        of.close()

        return ofname

    def build_cable(self, ofname):

        cmd = "chmod +x %s" % (ofname)
        error = subprocess.call(cmd, shell=True)
        if error == 1:
            raise ("Error changing file to executable")

        # cmd = "./%s clean" % (ofname)
        # The following add the "mpi" option to the build if we want to compile with MPI
        # cmd = "./%s" % (ofname)
        cmd = f"./{ofname} {'mpi'*self.mpi}"
        error = subprocess.call(cmd, shell=True)
        if error == 1:
            raise ("Error building executable")

        os.remove(ofname)

    def clean_if_needed(self):
        """Clean a previous compilation if latest executable doesn't have the name we want."""

        wanted_exe = f"cable{'-mpi'*self.mpi}"

        exe_list=[Path("cable-mpi"), Path("cable") ]
        exe_found = [ this_exe for this_exe in exe_list if this_exe.is_file() ]

        clean_compil = False
        if len(exe_found) > 0:
            newest_exe = max( exe_found, key=lambda x: x.stat().st_mtime )
            clean_compil = newest_exe != wanted_exe
        
        # Clean compilation if needed
        if clean_compil:
            cmd = f"rm -fr .tmp"
            error = subprocess.call(cmd, shell=True)
            if error == 1:
                raise ("Error cleaning previous compilation")

    def main(self, repo_name=None):

        build_dir = "%s/%s" % (repo_name, "offline")
        cwd = os.getcwd()
        os.chdir(os.path.join(self.src_dir, build_dir))

        self.clean_if_needed()
        ofname = self.adjust_build_script()
        self.build_cable(ofname)

        os.chdir(cwd)


if __name__ == "__main__":

    now = datetime.datetime.now()
    date = now.strftime("%d_%m_%Y")
    mpi = False
    # ------------- Change stuff ------------- #
    ver = "4.7.1"
    src_dir = "src"
    NCDIR = "/apps/netcdf/%s/lib" % (ver)
    NCMOD = "/apps/netcdf/%s/include" % (ver)

    if mpi:
        FC = "mpif90"
    else:
        FC = "ifort"
    CFLAGS = "-O2"
    LD = "'-lnetcdf -lnetcdff'"
    LDFLAGS = "'-L/opt/local/lib -O2'"
    repo1 = "Trunk"
    repo2 = "integration"
    # ------------------------------------------- #

    B = BuildCable(
        src_dir=src_dir,
        NCDIR=NCDIR,
        NCMOD=NCMOD,
        FC=FC,
        CFLAGS=CFLAGS,
        LD=LD,
        LDFLAGS=LDFLAGS,
        mpi=mpi,
    )
    B.main(repo_name=repo1)
    B.main(repo_name=repo2)

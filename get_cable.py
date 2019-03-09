#!/usr/bin/env python

"""
Get the head of the CABLE trunk, the user branch and CABLE-AUX

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (09.03.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import subprocess
import datetime

class GetCable(object):

    def __init__(self, src_dir=None, root="https://trac.nci.org.au/svn/cable",
                 user=None):

        self.src_dir = src_dir
        self.root = root
        self.user = user
        self.msg="\"checked out repo\""
        self.aux_dir = "CABLE-AUX"

    def main(self, repo_name=None, trunk=False):

        self.initialise_stuff()

        self.get_repo(repo_name, trunk)

    def initialise_stuff(self):

        if not os.path.exists(self.src_dir):
            os.makedirs(self.src_dir)

    def get_repo(self, repo_name, trunk=False):

        cwd = os.getcwd()
        os.chdir(self.src_dir)

        # Checkout the head of the trunk ...
        if trunk:

            # Check if we have a local copy of the trunk, if we do we won't
            # write over this, otherwise we will check one out
            cmd = "svn info %s/branches/Users/%s/%s" % \
                    (self.root, self.user, repo_name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            output, error = p.communicate()
            if error is 1:
                raise("Error checking if repo exists")

            if "non-existent" in str(output):
                cmd = "svn copy %s/trunk %s/branches/Users/%s/%s -m %s" % \
                        (self.root, self.root, self.user, repo_name, self.msg)
                error = subprocess.call(cmd, shell=True)
                if error is 1:
                    raise("Error checking out repo")

            cmd = "svn checkout %s/branches/Users/%s/%s" % \
                    (self.root, self.user, repo_name)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise("Error downloading repo")

        # Checkout CABLE-AUX
        if not os.path.exists(self.aux_dir):
            cmd = "svn checkout %s/branches/Share/%s %s" % \
                    (self.root, self.aux_dir, self.aux_dir)
            error = subprocess.call(cmd, shell=True)
            if error is 1:
                raise("Error checking out CABLE-AUX")

        os.chdir(cwd)




if __name__ == "__main__":

    now = datetime.datetime.now()
    date = now.strftime("%d_%m_%Y")

    #------------- Change stuff ------------- #
    src_dir = "src"
    user = "mgk576"
    repo1 = "Trunk_%s" % (date)
    #repo2 = "CABLE_trunk"
    # ------------------------------------------- #

    G = GetCable(src_dir=src_dir, user=user)
    G.main(repo_name=repo1, trunk=True)

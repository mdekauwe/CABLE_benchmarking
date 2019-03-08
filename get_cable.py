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


class GetCable(object):

    def __init__(self, src_dir=None):

        self.src_dir = src_dir

    def main(self):

        self.initialise_stuff()

    def initialise_stuff(self):
        
        if not os.path.exists(self.src_dir):
            os.makedirs(self.src_dir)


if __name__ == "__main__":

    #------------- Change stuff ------------- #
    src_dir = "src"


    # ------------------------------------------- #

    G = GetCable(src_dir=src_dir)
    G.main()

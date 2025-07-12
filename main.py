### --- BasicReduction --- ###
### --- Owner: Barbara Joachimczyk --- ###
### ------------------------------------------------------------------------------------------------------ ###

#region Imports
from astropy.time import Time
from astropy import units as u
from astropy.visualization import ZScaleInterval
import matplotlib.pyplot as plt 
import numpy as np 
import glob
import time
from itertools import chain
from masters import Masters
from sorting_files import SortBDFFiles
import argparse
from building_masters import CreateMasterFrames
from reduction import CalculateScienceFrames
#endregion

def run():
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument("-sort", type=bool, help="Sorts calibration files.", required=False, default=False)
    parser.add_argument("-mast", type=bool, help="Builds master frames from sorted files.", required=False, default=False)
    parser.add_argument("-red", type=bool, help="Performs reduction process.", required=False, default=True)
    parser.add_argument("-fc", type=str, choices = ["noisify", "normal"], help="Choose the type of flat correction.", required=False, default="normal")
    parser.add_argument("-path", type=str, help = "Path to the observation file.", required=True)
    args =  parser.parse_args()

    if args.sort == True:
        SortBDFFiles(args.path)
    if args.mast == True:
        CreateMasterFrames(args.path, flat_correction=args.fc)
    if args.red == True:
        CalculateScienceFrames(path=args.path, debugMode=True)

if __name__ == "__main__":
    run()
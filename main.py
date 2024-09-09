### --- BasicReduction --- ###
### --- Owner: Barbara Joachimczyk --- ###
### ------------------------------------------------------------------------------------------------------ ###

#region Imports


from astropy.time import Time
from astropy import units as u

from astropy.visualization import ZScaleInterval

import matplotlib.pyplot as plt 
import numpy as np 

# from os import renames
#from os.path import isfile, join, exists
# from astropy.io import fits
# from astropy.io import fits


import glob
import time
from itertools import chain

from masters import Masters
import sorting_files

from building_masters import CreateMasterFrames
from reduction import CalculateScienceFrames
#endregion

#region Global variables

#endregion

path = r"D:\20220106"
#sorting_files.SortBDFFiles(path)
CreateMasterFrames(path)
CalculateScienceFrames(path, False)

### --- BasicReduction --- ###
### --- Owner: Barbara Joachimczyk --- ###
### ------------------------------------------------------------------------------------------------------ ###

#region Imports

from masters import Masters
import sorting_files
from subframeParams import SubframeParams

from building_masters import CreateMasterFrames
from reduction import CalculateScienceFrames
#endregion

path = r"C:\Users\Hofek\Documents\!UMK\!Bazik\subframe\20220804"
subframeParams = SubframeParams(500,500,250,250)

#sorting_files.SortBDFFiles(path)
CreateMasterFrames(path, subframeParams)
CalculateScienceFrames(path, True, subframeParams)


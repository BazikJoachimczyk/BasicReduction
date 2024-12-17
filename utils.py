from os import listdir, makedirs
from os import renames
from os.path import isfile, join, exists
from astropy.io import fits
import numpy as np
from astroquery.astrometry_net import AstrometryNet
from astroquery.astrometry_net import conf
from astropy.wcs import WCS
from subframeParams import SubframeParams


def FitsFilesData(path, subframeParams = None):
    """
    Z plików fits w danym folderze tworzy macierz danych do wykonywania obliczeń.

    Parameters:
    - path: ścieżka do folderu danych obserwacyjnych

    """ 
    master_list = []
    for file_name in listdir(path):
        if file_name.endswith('.fits') or file_name.endswith('.fit'):
            full_path = join(path, file_name)
            with fits.open(full_path) as hdul:
                data = hdul[0].data
                # header = hdul[0].header
                # bzero = np.uint16(header['BZERO'])
                # data += bzero
                # print(bzero)
                if (subframeParams == None):
                    master_list.append(data)
                else:
                    master_list.append(CutSubframe(data, subframeParams))

    master_list = np.array(master_list)


    return master_list

def GetCoordsFromAstrometry(path, debugMode = False):

    frames = listdir(path)
    conf.api_key = 'adwuagneiedgziwi'                   # ustawiam API (konto barbarajoachimczyk na Astrometry.net)
    Astrometry = AstrometryNet()


    Ra = 0                                              # inicjuję współrzędne, które wypełni Astrometry
    Dec = 0
    Counter = 0

    if (debugMode):
        return Ra,Dec
    
    print('File sent to Astrometry.net: ', join(path,frames[0]))
    
    while Counter < 3:    
        try:
            wcs_header = Astrometry.solve_from_image(join(path,frames[0]), force_image_upload=True)
            wcs = WCS(wcs_header)                          
            Ra = (wcs.wcs.crval[0] *24) / 360 
            Dec = wcs.wcs.crval[1]
            break
        except Exception as e:
            print(f"Astrometry error: {e}")
            Counter += 1
        
    if Counter ==3:
        print("Astrometry Error: file not sent.")
        
  
    return Ra, Dec

#offset params start from bottom left corner
def CutSubframe(data, subframeParams : SubframeParams):
    result = np.zeros((subframeParams.Width, subframeParams.Height))

    for row in range(subframeParams.OffsetX, subframeParams.Width + subframeParams.OffsetX):
        for column in range(subframeParams.OffsetY, subframeParams.Height + subframeParams.OffsetY):            
            result[column - subframeParams.OffsetY][row - subframeParams.OffsetX] = data[column][row]            

    return result
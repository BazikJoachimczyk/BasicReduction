from os import listdir, makedirs
from os import renames
from os.path import isfile, join, exists
from astropy.io import fits
import numpy as np
from astroquery.astrometry_net import AstrometryNet
from astroquery.astrometry_net import conf
from astropy.wcs import WCS
import random


def FitsFilesData(path):
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
                master_list.append(data)
    master_list = np.array(master_list)

    return master_list

def FitsFilesDataFromList(file_list):
    """
    Z plików fits w zadanej liście tworzy macierz danych do wykonywania obliczeń.

    Parameters:
    - file_list: lista pełnych ścieżek do plików .fits lub .fit

    Returns:
    - ndarray: tablica 3D typu np.ndarray 
    """
    data_list = []
    for path in file_list:
        if path.endswith('.fits') or path.endswith('.fit'):
            with fits.open(path) as hdul:
                data = hdul[0].data
                data_list.append(data)
    return np.array(data_list)

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

def Noisify(data, sigma = 1):
    mean = data.mean()
    std = data.std() 
           
    result = np.zeros((len(data),len(data[0])))
    for i in range(len(data)):
        for j in range(len(data[i])):
            if (data[i][j] <= mean+(std*sigma)):
                result[i][j] = data[i][j]
            else:
                result[i][j] = random.randrange(int(mean-std), int(mean+std))

    return result

def SectorsNoisify(data, sectorColumns, sectorRows):
    width = len(data)
    height = len(data[0])

    columnStep = int(width/sectorColumns)
    rowStep = int(height/sectorRows)              

    result = np.zeros((len(data),len(data[0])))
    for rowOffset in range(sectorRows):
        for columnOffset in range(sectorColumns):
            #create temp array
            sectorData = np.zeros((columnStep, rowStep))
            
            #select sector
            for i in range(rowOffset*rowStep, rowOffset*rowStep+rowStep):        
                for j in range(columnOffset*columnStep, columnOffset*columnStep+columnStep):                                                             
                    sectorData[i-rowOffset*rowStep][j-columnOffset*columnStep] = data[i][j]  

            #fix sector
            sectorData = Noisify(sectorData, 1)
            
            #return sector to original
            for i in range(rowOffset*rowStep, rowOffset*rowStep+rowStep):        
                for j in range(columnOffset*columnStep, columnOffset*columnStep+columnStep):                                                            
                    result[i][j] = sectorData[i-rowOffset*rowStep][j-columnOffset*columnStep]                                              
    return result
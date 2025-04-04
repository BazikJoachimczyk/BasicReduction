from os import listdir
from os.path import join
from frame import Frame
import numpy as np
from utils import FitsFilesData, Noisify, SectorsNoisify
from masters import Masters
import json

masterFrames = Masters()  

def CreateMasterFrames(path, flat_correction:str):
    """
    Przeszukuje folder z obserwacji po ramki kalibracyjne, z których tworzy masterbiasy, masterdarki i masterflaty.

    Parameters:
    - path: ścieżka do folderu danych obserwacyjnych

    Returns:
    - potwierdzenie stworzenia masterframes.
    """ 

    bias_path = join(path, 'bdf', "Bias")
    dark_path = join(path, 'bdf', 'Dark')
    flat_path = join(path, 'bdf', 'Flat')


    ### BIAS
    bias_subpath = listdir(bias_path)
    info = {
        "Stage": 1,
        "Description": "Calculating masterbias frames."
    }
    print(json.dumps(info))

    for i in range(len(bias_subpath)):
        bias_sub_subpath = listdir(join(bias_path,bias_subpath[i])) # lista plików w podfolderze
        mbias_frame = Frame(join(bias_path, bias_subpath[i]))
        mbias_frame.OpenHeader(join(bias_path, bias_subpath[i], bias_sub_subpath[-1]))    # kradnę header ostatniego
        data_b = FitsFilesData(join(bias_path, bias_subpath[i]))            # array pikseli z pliku
        mbias_frame.data = np.median(data_b, axis=0)
        mbias_frame.name = 'Masterbias' + str(mbias_frame.bin) + '.fits'
        mbias_frame.history = 'Masterbias calculated by median.'
        mbias_frame.SaveBDFFitsFrame()
        masterFrames.bias.append(mbias_frame)

    ### DARK
    dark_subpath = listdir(dark_path)               # lista folderów darków różnej długości
    info = {
        "Stage": 2,
        "Description": "Calculating masterdark frames."
    }
    print(json.dumps(info))

    for i in range(len(dark_subpath)):
        dark_sub_subpath = listdir(join(dark_path,dark_subpath[i])) # lista plików w podfolderze
        mdark_frame = Frame(join(dark_path, dark_subpath[i]))
        mdark_frame.OpenHeader(join(dark_path, dark_subpath[i], dark_sub_subpath[-1]))    # kradnę header ostatniego
        data_d = FitsFilesData(join(dark_path, dark_subpath[i]))            # array pikseli z pliku
        med_data_d = np.median(data_d, axis=0)
        med_data_d = med_data_d - masterFrames.GetBiasByBinning(mdark_frame.bin, mdark_frame.subx, mdark_frame.suby).data    # odejmuję masterbias
        med_data_d[med_data_d < 0] =0                       # Wyzerowuję wartości ujemne; konieczne w przypadku darka o krótkim czasie ekspozycji, w którym pojawiły się ujemne zliczenia po odjęciu Bias
        mdark_frame.data = med_data_d                       # zapisuje do obieku Frame
        mdark_frame.name = 'Masterdark' + str(int(mdark_frame.exp)) + '.fits'
        mdark_frame.history = 'Dark calculated by median. Bias substracted.'
        mdark_frame.SaveBDFFitsFrame()
        masterFrames.dark.append(mdark_frame)

    ### FLAT
    flat_subpath = listdir(flat_path)
    info = {
        "Stage": 3,
        "Description": "Calculating masterflat frames."
    }
    print(json.dumps(info))

    for i in range(len(flat_subpath)):
        flat_sub_subpath = listdir(join(flat_path,flat_subpath[i]))
        mflat_frame = Frame(join(flat_path, flat_subpath[i]))
        mflat_frame.OpenHeader(join(flat_path, flat_subpath[i], flat_sub_subpath[-1]))
        data_f = FitsFilesData(join(flat_path, flat_subpath[i]))
        data_f = data_f - masterFrames.GetBiasByBinning(mflat_frame.bin, mflat_frame.subx, mflat_frame.suby).data
        dark_for_flat = masterFrames.GetDarkByExpTime(mflat_frame.exp, mflat_frame.bin, mflat_frame.subx, mflat_frame.suby, mflat_frame.temp)      
        if dark_for_flat == None:
            print('No masterdark frame available for flat: ', str(join(flat_path, flat_subpath[i]), ': build without masterdark.'))
            continue
        else:
            data_f = data_f - dark_for_flat.data  
        med_data_f = np.median(data_f, axis=0)
        if flat_correction == 'noisify':
            med_data_f = Noisify(med_data_f) # globalne znalezienie smug i nalozenie szumu
            med_data_f = SectorsNoisify(med_data_f, 100,100) # nakladanie szumu sektorowo
        norm_data_f = med_data_f / np.median(med_data_f)
        mflat_frame.data = norm_data_f
        mflat_frame.name = 'masterflat' + '_' + str(mflat_frame.filter) + '.fits'
        mflat_frame.history = 'Masterflat normalized. Bias and dark substracted.'
        mflat_frame.SaveBDFFitsFrame()
        masterFrames.flat.append(mflat_frame)

    # info = {
    #     "Stage": 4,
    #     "Description": "Master frames done."
    # }
    # print(json.dumps(info))

    return
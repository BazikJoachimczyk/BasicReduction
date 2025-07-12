from os import listdir
from os.path import join, exists
from frame import Frame
import numpy as np
from utils import FitsFilesData, Noisify, SectorsNoisify, FitsFilesDataFromList
import json
from collections import defaultdict
from astropy.io import fits
 


def CreateMasterFrames1(path, flat_correction:str):

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
        data_b = FitsFilesDataFromList(join(bias_path, bias_subpath[i]))            # array pikseli z pliku
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
        data_d = FitsFilesDataFromList(join(dark_path, dark_subpath[i]))            # array pikseli z pliku
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
        data_f = FitsFilesDataFromList(join(flat_path, flat_subpath[i]))
        data_f = data_f - masterFrames.GetBiasByBinning(mflat_frame.bin, mflat_frame.subx, mflat_frame.suby).data
        dark_for_flat = masterFrames.GetDarkByExpTime(mflat_frame.exp, mflat_frame.bin, mflat_frame.subx, mflat_frame.suby, mflat_frame.temp)      
        if dark_for_flat == None:
            print('No masterdark frame available for flat: ', join(flat_path, flat_subpath[i], ': build without masterdark.'))
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


def CreateMasterFrames(path, flat_correction:str):
    """
    Przeszukuje folder z obserwacji po ramki kalibracyjne, z których tworzy masterbiasy, masterdarki i masterflaty.

    Parameters:
    - path: ścieżka do folderu danych obserwacyjnych

    Returns:
    - potwierdzenie stworzenia masterframes.
    """ 

    bias_path = join(path, 'bdf', "Bias")
    bias_groups = defaultdict(list)
    dark_path = join(path, 'bdf', 'Dark')
    dark_groups = defaultdict(list)
    flat_path = join(path, 'bdf', 'Flat')
    flat_groups = defaultdict(list)

    ### BIAS
    bias_files = listdir(bias_path)
    info = {
        "Stage": 1,
        "Description": "Calculating masterbias frames."
    }
    print(json.dumps(info))

    for file in bias_files:
        bias = Frame(join(bias_path, file))
        bias.OpenHeader(join(bias_path, file))
        key = (bias.temp, bias.binx, bias.biny, bias.subx, bias.suby)
        bias_groups[key].append(join(bias_path, file))

    for key, files in bias_groups.items():
        data = FitsFilesDataFromList(files)  
        master_bias_data = np.median(data, axis=0)
        mbias = Frame(files[0])
        mbias.OpenHeader(files[0])
        mbias.path = bias_path
        mbias.data = master_bias_data
        mbias.temp, mbias.binx, mbias.biny, mbias.subx, mbias.suby = key
        mbias.name = f"Masterbias_T{key[0]}_BX{key[1]}_BY{key[2]}_X{key[3]}_Y{key[4]}.fits"
        mbias.history = "Masterbias calculated from grouped bias frames."
        mbias.SaveBDFFitsFrame()

    ### DARK
    dark_files = listdir(dark_path)
    info = {
        "Stage": 2,
        "Description": "Calculating masterdark frames."
    }
    print(json.dumps(info))    

    # Grupowanie darków
    for file in dark_files:
        dark = Frame(join(dark_path, file))
        dark.OpenHeader(join(dark_path, file))
        key = (dark.temp, dark.exp, dark.binx, dark.biny, dark.subx, dark.suby)
        dark_groups[key].append(join(dark_path,file))

    # Przetwarzanie grup
    for key, files in dark_groups.items():
        temp, exp, binx, biny, subx, suby = key

        # Znajdź odpowiadający masterbias
        mbias_path = join(bias_path, f"Masterbias_T{temp}_BX{binx}_BY{biny}_X{subx}_Y{suby}.fits")
        if not exists(mbias_path):
            print(f"No masterbias found for: {key}.")
            continue

        # Otwieram masterbiasa
        with fits.open(mbias_path) as hdul:
            mbias_data = hdul[0].data
        masterbias = mbias_data

        # Redukcja biasowa i zbieranie zredukowanych darków
        reduced_dark_data = []
        for file in files:
            full_path = join(dark_path, file)
            with fits.open(full_path) as hdul:
                dark_data = hdul[0].data
                reduced = dark_data - masterbias
                reduced[reduced < 0] = 0
                reduced_dark_data.append(reduced)

        reduced_dark_data = np.array(reduced_dark_data)
        master_dark_data = np.median(reduced_dark_data, axis=0)

        # Zapis masterdarka
        mdark = Frame(files[0])
        mdark.OpenHeader(files[0])
        mdark.data = master_dark_data
        mdark.path = dark_path
        mdark.temp, mdark.exp, mdark.binx, mdark.biny, mdark.subx, mdark.suby = key
        mdark.name = f"Masterdark_T{temp}_E{exp}_BX{binx}_BY{biny}_X{subx}_Y{suby}.fits"
        mdark.history = f"Masterdark calculated using masterbias."
        mdark.SaveBDFFitsFrame()


    ### FLAT
    flat_files = listdir(flat_path)
    info = {
        "Stage": 3,
        "Description": "Calculating masterflat frames."
    }
    print(json.dumps(info))    

    # Grupowanie flatów
    for file in flat_files:
        flat = Frame(join(flat_path, file))
        flat.OpenHeader(join(flat_path, file))
        key = (flat.filter, flat.temp, flat.exp, flat.binx, flat.biny, flat.subx, flat.suby)
        flat_groups[key].append(join(flat_path,file))

    # Przetwarzanie grup
    for key, files in flat_groups.items():
        filter, temp, exp, binx, biny, subx, suby = key

        # Ścieżka do masterbiasa
        mbias_path = join(bias_path, f"Masterbias_T{temp}_BX{binx}_BY{biny}_X{subx}_Y{suby}.fits")
        masterbias = None
        if not exists(mbias_path):
            print(f"No masterbias found for: {key}.")
        else:
            with fits.open(mbias_path) as hdul:
                masterbias = hdul[0].data

        # Ścieżka do masterdarka
        mdark_path = join(dark_path, f"Masterdark_T{temp}_BX{binx}_BY{biny}_X{subx}_Y{suby}.fits")
        masterdark = None
        if not exists(mdark_path):
            print(f"No masterdark found for: {key}.")
        else:
            with fits.open(mdark_path) as hdul:
                masterdark = hdul[0].data

        # Redukcja flatów (bez normalizacji na tym etapie)
        reduced_flats = []
        for file in files:
            full_path = join(flat_path, file)
            with fits.open(full_path) as hdul:
                flat_data = hdul[0].data
                if masterbias is not None:
                    flat_data = flat_data - masterbias
                if masterdark is not None:
                    flat_data = flat_data - masterdark
                reduced_flats.append(flat_data)

        reduced_flats = reduced_flats
        master_flat_data = np.median(reduced_flats, axis=0) # tu mam medianę masterflata
        #print('\nMasterflatdata:', master_flat_data, '\n')
        #print('\nMasterflatdatamedian:', np.median(master_flat_data), '\n')
        #master_flat_data = master_flat_data.astype(np.float64)

        if flat_correction == 'noisify':
            #master_flat_data = Noisify(master_flat_data)
            master_flat_data = SectorsNoisify(master_flat_data, 50,50)


        # Normalizacja całego masterflata
        norm_mflat_data = ((master_flat_data) / float(np.median(master_flat_data)))

        # Zapis masterflata
        mflat = Frame(files[0])
        mflat.OpenHeader(files[0])
        mflat.path = flat_path
        mflat.data = norm_mflat_data
        #mflat.filter, mflat.temp, mflat.exp, mflat.bin, mflat.subx, mflat.suby = key
        if flat_correction == 'noisify':
            mflat.name = f"MasterflatNoisified_F{filter}_T{temp}_BX{binx}_BY{biny}_X{subx}_Y{suby}.fits"    
        else:
            mflat.name = f"Masterflat_F{filter}_T{temp}_BX{binx}_BY{biny}_X{subx}_Y{suby}.fits"
        mflat.history = f"Masterflat calculated from reduced flats."
        mflat.SaveBDFFitsFrame()
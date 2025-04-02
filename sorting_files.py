#from os import listdir, makedirs, renames
import os
from os.path import isfile, join, exists
from astropy.io import fits
import json

def SortBDFFiles(path):                   
    """
    Sortuje pliki w folderach na ramki naukowe oraz kalibracyjne z podziałem na długość ekspozycji i filtry. Tworzy odpowiednie masterfitsy.

    Parameters:
    - path: ścieżka do folderu danych obserwacyjnych

    Returns:
    - potwierdzenie posortowania plików fits.
    """   
    info = {
            "Stage": 1,
            "Description": "Sorting calibration frames."
            }
    print(json.dumps(info))

    subfolders = os.listdir(path)
    for file in (subfolders):
        if file == 'bdf':                       # znajduje folder "bdf" i sortuje pliki według typu

            bdf_folder_path = join(path, "bdf")
            bdf_contains = os.listdir(bdf_folder_path)                 # tworzy listę plików w folderze bdf
            
            for i in range(len(bdf_contains)):                      # sprawdza header każdego pliku w celu dopasowania do odpowiedniego podfolderu
                fits_file = fits.open(join(bdf_folder_path, bdf_contains[i]))
                fits_header = fits_file[0].header
                fits_exptime = str(int(fits_header['EXPTIME']))
                fits_binx = str(fits_header['XBINNING'])
                fits_biny = str(fits_header['YBINNING'])
                fits_subx = str(fits_header['XORGSUBF'])
                fits_suby = str(fits_header['YORGSUBF'])

                if fits_header['IMAGETYP'] == 'Bias Frame':             # tworzenie podfolderu z biasami
                    fits_file.close()
                    
                    fits_file = os.renames(join(bdf_folder_path, bdf_contains[i]), join(bdf_folder_path, "Bias", "Bias_" + fits_binx + 'x' + fits_biny + '_' + fits_subx + 'x' + fits_suby, bdf_contains[i]))

                elif fits_header['IMAGETYP'] == 'Dark Frame':           # tworzenie podfolderu z darkami z podziałem na czas ekspozycji
                    fits_file.close()

                    fits_file = os.renames(join(bdf_folder_path, bdf_contains[i]),join(bdf_folder_path, "Dark", 'Dark_' + fits_exptime + '_' +  fits_binx + 'x' + fits_biny + '_' + fits_subx + 'x' + fits_suby, bdf_contains[i]) )

                elif fits_header['IMAGETYP'] == 'Light Frame' or 'Flat Frame' or 'Flat Field':      # tworzenie podfolderu z flatami z podziałem na filtry
                    
                    try:
                        fits_file.close()
                        fits_filter = str(fits_header['FILTER'])
                        fits_file = os.renames(join(bdf_folder_path, bdf_contains[i]),join(bdf_folder_path, "Flat", 'Flat_' + fits_filter + '_' + fits_binx + 'x' + fits_biny + '_' + fits_subx + 'x' + fits_suby, bdf_contains[i]) )
                    except:
                        fits_file.close()
                        fits_file = os.renames(join(bdf_folder_path, bdf_contains[i]),join(bdf_folder_path, "Flat", 'Flat_' +  fits_filter + '_' +  fits_binx + 'x' + fits_biny + '_' + fits_subx + 'x' + fits_suby, bdf_contains[i]))

    return 
from os import listdir, rename, makedirs
from astropy.nddata import CCDData
from os.path import join, exists
from utils import stage_print

from os import listdir, rename, makedirs
from astropy.nddata import CCDData
from os.path import join, exists
from utils import stage_print

def sort_bdf(path: str) -> None:
    stage_print("1", "Sorting bdf files.")

    folders = listdir(path)
    for folder in folders:
        if folder.lower() == 'bdf' and folder != 'bdf':
            original = join(path, folder)
            target = join(path, 'bdf')
            rename(original, target)
            print(f"Renamed {folder} -> bdf")
            break

    bdf_folder = join(path, 'bdf')
    for file in listdir(bdf_folder):
        if file.endswith('.fit') or file.endswith('.fits'):
            filepath_full = join(bdf_folder, file)
            bdf_fits = CCDData.read(filepath_full, unit='adu')

            imagetyp = bdf_fits.header['IMAGETYP']
            temp = str(int(bdf_fits.header['SET-TEMP']))
            exp = str(int(bdf_fits.header.get('EXPTIME', 0)))
            binx = str(int(bdf_fits.header['XBINNING']))
            biny = str(int(bdf_fits.header['YBINNING']))
            subx = str(int(bdf_fits.header['XORGSUBF']))
            suby = str(int(bdf_fits.header['YORGSUBF']))

            if imagetyp == 'Bias Frame':
                folderpath = join(bdf_folder, f"Bias_temp{temp}_binx{binx}_biny{biny}_subx{subx}_suby{suby}")
                if not exists(folderpath):
                    makedirs(folderpath)
                rename(filepath_full, join(folderpath, file))

            elif imagetyp == 'Dark Frame':
                folderpath = join(bdf_folder, f"Dark_exp{exp}_temp{temp}_binx{binx}_biny{biny}_subx{subx}_suby{suby}")
                if not exists(folderpath):
                    makedirs(folderpath)
                rename(filepath_full, join(folderpath, file))

            elif imagetyp in ['Flat Frame', 'Light Frame', 'Flat Field']:
                filt = str(bdf_fits.header['FILTER'])
                folderpath = join(bdf_folder, f"Flat_{filt}_binx{binx}_biny{biny}_subx{subx}_suby{suby}")
                if not exists(folderpath):
                    makedirs(folderpath)
                rename(filepath_full, join(folderpath, file))

            else:
                stage_print('-1', 'Unreckognizable imagetype.')
                raise ValueError(f'Unreckognizable imagetype: {file}.')

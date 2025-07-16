from os import listdir
import argparse
from os.path import join, isdir
from utils import stage_print, get_bias, get_dark
from astropy.nddata import CCDData
import astropy.units as u
import numpy as np
import ccdproc

def create_masterbias_frames(path:str) -> None:
    stage_print("1", "Building master bias frames.")

    folders = listdir(join(path, "bdf"))

    for folder in folders:
        if "Bias" in folder:
            bias_folder = join(path, 'bdf', folder)
            if isdir(bias_folder):
                biases = [CCDData.read(join(bias_folder, file), unit='adu') 
                          for file in listdir(bias_folder) 
                          if file.endswith('.fit') or file.endswith('.fits')]

                masterbias = ccdproc.combine(
                    img_list = biases,
                    method = "median"
                )
                masterbias.write(join(bias_folder, "Masterbias.fits"), overwrite=True)

def create_masterdark_frames(path:str) -> None:
    stage_print("2", "Building master dark frames.")

    folders = listdir(join(path, 'bdf'))

    for folder in folders:
        if "Dark" in folder:
            dark_folder = join(path, 'bdf', folder)
            if isdir(dark_folder):
                darks = [CCDData.read(join(dark_folder, file), unit='adu') for file in listdir(dark_folder) if file.endswith('.fit') or file.endswith('.fits')]
                temp = str(int(darks[0].header['SET-TEMP']))
                binx = str(int(darks[0].header['XBINNING']))
                biny = str(int(darks[0].header['YBINNING']))
                subx = str(int(darks[0].header['XORGSUBF']))
                suby = str(int(darks[0].header['YORGSUBF']))
                
                masterbias_path = get_bias(path=path, temp = temp, binx=binx, biny=biny, subx=subx, suby=suby)

                if masterbias_path is not None:
                    masterbias = CCDData.read(masterbias_path, unit='adu')
                else:
                    stage_print("-1", f"No matching bias for dark with parameters: temp: {temp}, binx: {binx}, biny: {biny}, subx: {subx}, suby: {suby}.")
                    raise ValueError
                
                darks_bias_corrected = [ccdproc.subtract_bias(dark, masterbias) for dark in darks]

                masterdark = ccdproc.combine(
                    img_list = darks_bias_corrected,
                    method = 'median',
                )
                masterdark.write(join(dark_folder, "Masterdark.fits"), overwrite=True)

def create_masterflat_frames(path: str) -> None:
    stage_print("3", "Building master flat frames.")

    folders = listdir(join(path, 'bdf'))

    for folder in folders:
        if "Flat" in folder:
            flat_folder = join(path, 'bdf', folder)
            if isdir(flat_folder):
                flats = [CCDData.read(join(flat_folder, file), unit='adu') for file in listdir(flat_folder) if file.endswith('.fit') or file.endswith('.fits')]
                exp = str(int(flats[0].header['EXPTIME']))
                temp = str(int(flats[0].header['SET-TEMP']))
                filt = str(flats[0].header['FILTER'])
                binx = str(int(flats[0].header['XBINNING']))
                biny = str(int(flats[0].header['YBINNING']))
                subx = str(int(flats[0].header['XORGSUBF']))
                suby = str(int(flats[0].header['YORGSUBF']))
                masterbias_path = get_bias(path=path, temp=temp, binx=binx, biny=biny, subx=subx, suby=suby)
                if masterbias_path is not None:
                    masterbias = CCDData.read(masterbias_path, unit='adu')
                    flats_bias_corrected = [ccdproc.subtract_bias(flat, masterbias) for flat in flats]
                else:
                    stage_print("-1", f"No matching bias for flat with parameters: filter: {filt}, temp: {temp}, binx: {binx}, biny: {biny}, subx: {subx}, suby: {suby}.")
                    raise ValueError

                masterdark_path = get_dark(path=path, exp=exp, temp=temp, binx=binx, biny=biny, subx=subx, suby=suby)
                if masterdark_path is not None:
                    masterdark = CCDData.read(masterdark_path, unit='adu')
                    flats_dark_corrected = [
                        ccdproc.subtract_dark(
                            flat,
                            masterdark,
                            scale=False,
                            data_exposure=float(flat.header['EXPTIME']) * u.second,
                            dark_exposure=float(masterdark.header['EXPTIME']) * u.second) for flat in flats_bias_corrected
                                        ]
                else:
                    stage_print("-1", f"No matching dark for flat with parameters: filter: {filt}, exp: {exp}, binx: {binx}, biny: {biny}, subx: {subx}, suby: {suby}.")
                    raise ValueError

                flats_normalized = [
                                CCDData(data=flat.data / np.median(flat.data), unit=flat.unit, meta=flat.header)
                                for flat in flats_dark_corrected
                            ]

                masterflat = ccdproc.combine(
                    flats_normalized,
                    method='median',
                    sigma_clip=True,
                    sigma_clip_low_thresh=3,
                    sigma_clip_high_thresh=3
                )

                masterflat.write(join(flat_folder, 'Masterflat.fits'), overwrite=True)

def build_all_masters(path:str) -> None:
    create_masterbias_frames(path)
    create_masterdark_frames(path)
    create_masterflat_frames(path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sort BDF files in given path.")
    parser.add_argument("--path", type=str, help="Path to the observation folder")
    args = parser.parse_args()

    build_all_masters(args.path)
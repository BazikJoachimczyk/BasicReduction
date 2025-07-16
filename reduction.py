from os.path import join, exists
import argparse
from os import listdir, makedirs
from utils import stage_print, get_bias, get_dark, get_flat
from astropy.nddata import CCDData
import astropy.units as u
import ccdproc

def reduction(path: str, flat_path: str = None) -> None:
    stage_print("1", "Science frames reduction.")
    folders = listdir(path)

    if 'bdf' in folders:
        folders.remove('bdf')
    else:
        raise ValueError(f"No bdf folder found in: {path}")

    for folder in folders:
        folder_path = join(path, folder)
        science_files = listdir(folder_path)

        for science_frame in science_files:
            if not (science_frame.endswith('.fit') or science_frame.endswith('.fits')):
                continue

            science_frame_path = join(folder_path, science_frame)
            science = CCDData.read(science_frame_path, unit='adu')

            exp = float(science.header['EXPTIME'])
            temp = str(int(science.header['SET-TEMP']))
            filt = str(science.header['FILTER'])
            binx = str(int(science.header['XBINNING']))
            biny = str(int(science.header['YBINNING']))
            subx = str(int(science.header['XORGSUBF']))
            suby = str(int(science.header['YORGSUBF']))


            masterbias_path = get_bias(path=path, temp=temp, binx=binx, biny=biny, subx=subx, suby=suby)
            if masterbias_path is not None:
                masterbias = CCDData.read(masterbias_path, unit='adu')
            else:
                raise ValueError(f"No matching bias found for: {science_frame_path}")

            masterdark_path = get_dark(path=path, exp=str(int(exp)), temp=temp, binx=binx, biny=biny, subx=subx, suby=suby)
            if masterdark_path is not None:
                masterdark = CCDData.read(masterdark_path, unit='adu')
            else:
                raise ValueError(f"No matching dark found for: {science_frame_path}")

            if flat_path is not None:
                masterflat_path = flat_path
            else:
                masterflat_path = get_flat(path=path, filt=filt, binx=binx, biny=biny, subx=subx, suby=suby)

            if masterflat_path is not None:
                masterflat = CCDData.read(masterflat_path, unit='adu')
            else:
                raise ValueError(f"No matching flat found for: {science_frame_path}")
            
            science_bias_corr = ccdproc.subtract_bias(science, masterbias)
            science_bias_corr.header['HISTORY'] = f"Bias subtracted using {masterbias_path}"
            science_dark_corr = ccdproc.subtract_dark(
                science_bias_corr,
                masterdark,
                scale=False,
                data_exposure=exp * u.second,
                dark_exposure=float(masterdark.header['EXPTIME']) * u.second
            )
            science_dark_corr.header['HISTORY'] = f"Dark subtracted using {masterdark_path}"
            science_flat_corr = ccdproc.flat_correct(science_dark_corr, masterflat)
            science_flat_corr.header['HISTORY'] = f"Flat-field corrected using {masterflat_path}"
            science_flat_corr.header['HISTORY'] = "Reduced using AstroLog BasicReduction pipeline"

            science_pipeline_path = join(path, folder, 'Pipeline')
            if not exists(science_pipeline_path):
                makedirs(science_pipeline_path)
            science_flat_corr.write(join(science_pipeline_path, science_frame), overwrite=True)

            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reduce science frames.")
    parser.add_argument("--path", type=str, help="Path to the observation folder")
    parser.add_argument("--flat_path", type=str, default=None, help="Optional path to master flat frame")
    args = parser.parse_args()

    reduction(args.path, args.flat_path)
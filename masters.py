### Klasa obiektów: Masters. Przechowuje obiekty typu Frame(), które są wyznaczonymi masterramkami w celu wykorzystania ich we właściwej redukcji ramek naukowych.

from frame import Frame
from os.path import join
from os import listdir
from astropy.io import fits

class Masters():
    def __init__(self, path):
        self.bias = []
        self.dark = []
        self.flat = []
        self.path = path

    def FillMasters(self):
        bias_path = join(self.path, 'bdf', "Bias")
        dark_path = join(self.path, 'bdf', 'Dark')
        flat_path = join(self.path, 'bdf', 'Flat')

        bias_files = listdir(bias_path)
        dark_files = listdir(dark_path)
        flat_files = listdir(flat_path)

        for file in bias_files:
            if "master" in file.lower():
                bias = Frame(join(bias_path, file))
                bias.OpenBDFHeader(join(bias_path, file))
                with fits.open(join(bias_path, file)) as hdul:
                    bias.data = hdul[0].data
                self.bias.append(bias)

        for file in dark_files:
            if "master" in file.lower():
                dark = Frame(join(dark_path, file))
                dark.OpenBDFHeader(join(dark_path, file))
                with fits.open(join(dark_path, file)) as hdul:
                    dark.data = hdul[0].data
                self.dark.append(dark)

        for file in flat_files:
            if "master" in file.lower():
                flat = Frame(join(flat_path, file))
                flat.OpenBDFHeader(join(flat_path, file))
                with fits.open(join(flat_path, file)) as hdul:
                    flat.data = hdul[0].data
                self.flat.append(flat)
            

    def GetDarkByExpTime(self, exp, binx, biny, subx, suby, temp):
        found_dark = None
        for dark in self.dark:
            if (dark.exp == exp and dark.binx == binx and dark.biny == biny and dark.subx == subx and dark.suby == suby and dark.temp == temp):
                found_dark = dark
        if found_dark == None: 
            print(f'[ERROR] Dark not found. Failed to find one with params: Exp {exp}, Binx {binx}, Biny {biny}, Subx {subx}, Suby {suby}')  
            return
        return found_dark

    def GetFlatByFilter(self, filter, binx, biny, subx, suby):
        found_flat = None
        for flat in self.flat:
            if (flat.filter == filter and flat.binx == binx and flat.biny == biny and flat.subx == subx and flat.suby == suby):
                found_flat = flat
        if found_flat == None:
            print(f'[ERROR] Flat not found. Failed to find one with params: Filter {filter}, Binx {binx}, Biny {biny}, Subx {subx}, Suby {suby}')
            return
        return found_flat
    
    def GetBiasByBinning(self, binx, biny, subx, suby):
        found_bias = None
        for bias in self.bias:
            if (bias.binx == binx and bias.biny == biny and bias.subx == subx and bias.suby == suby):
                found_bias = bias
        if found_bias == None:
            print(f'[ERROR] Bias not found. Failed to find one with params: Binx {binx}, Biny {biny}, Subx {subx}, Suby {suby}')
            return
        return found_bias
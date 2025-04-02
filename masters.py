### Klasa obiektów: Masters. Przechowuje obiekty typu Frame(), które są wyznaczonymi masterramkami w celu wykorzystania ich we właściwej redukcji ramek naukowych.

from frame import Frame

class Masters():
    def __init__(self):
        self.bias = []
        self.dark = []
        self.flat = []

    def GetDarkByExpTime(self, exp, bin, subx, suby, temp):
        found_dark = None
        for dark in self.dark:
            if (dark.exp == exp and dark.bin == bin and dark.subx == subx and dark.suby == suby and dark.temp == temp):
                found_dark = dark
        if found_dark == None: 
            print(f'[ERROR] Dark not found. Failed to find one with params: Exp {exp}, Bin {bin}, Subx {subx}, Suby {suby}')  
            return
        return found_dark

        
    def GetFlatByFilter(self, filter, bin, subx, suby):
        found_flat = None
        for flat in self.flat:
            if (flat.filter == filter and flat.bin == bin and flat.subx == subx and flat.suby == suby):
                found_flat = flat
        if found_flat == None:
            print(f'[ERROR] Flat not found. Failed to find one with params: Filter {filter}, Bin {bin}, Subx {subx}, Suby {suby}')
            return
        return found_flat
    
    def GetBiasByBinning(self, bin, subx, suby):
        found_bias = None
        for bias in self.bias:
            if (bias.bin == bin and bias.subx == subx and bias.suby == suby):
                found_bias = bias
        if found_bias == None:
            print(f'[ERROR] Bias not found. Failed to find one with params: Bin {bin}, Subx {subx}, Suby {suby}')
            return
        return found_bias
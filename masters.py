### Klasa obiektów: Masters. Przechowuje obiekty typu Frame(), które są wyznaczonymi masterramkami w celu wykorzystania ich we właściwej redukcji ramek naukowych.

from frame import Frame

class Masters():
    def __init__(self):
        self.bias = []
        self.dark = []
        self.flat = []

    def GetDarkByExpTime(self, exp, bin, subx, suby):
        for dark in self.dark:
            if (dark.exp == exp and dark.bin == bin and dark.subx == subx and dark.suby == suby):
                return dark
        if dark == None:
            for dark in self.dark:
                if (dark.bin == bin and dark.subx == subx and dark.suby == suby):
                    scaling_factor = dark.exp / exp
                    ScaledDark = Frame()
                    ScaledDark.data = dark.data * scaling_factor
                    ScaledDark.exp = exp
                    ScaledDark.bin = bin 
                    ScaledDark.subx = subx 
                    ScaledDark.suby = suby
                    self.dark.append(ScaledDark)
                    print(f'Scaling dark from Exp: {dark.exp}, Bin: {dark.bin}, Subx: {dark.subx}, Suby: {dark.suby}')
                    return dark


        print(f'[ERROR] Dark not found. Failed to find one with params: Exp {exp}, Bin {bin}, Subx {subx}, Suby {suby}')  

    def GetFlatByFilter(self, filter, bin, subx, suby):
        for flat in self.flat:
            if (flat.filter == filter and flat.bin == bin and flat.subx == subx and flat.suby == suby):
                return flat
        print('[ERROR] Flat not found.')

    def GetBiasByBinning(self, bin, subx, suby):
        for bias in self.bias:
            if (bias.bin == bin and bias.subx == subx and bias.suby == suby):
                return bias        
        print(f'[ERROR] Bias not found. Failed to find one with params: Bin {bin}, Subx {subx}, Suby {suby}')
 
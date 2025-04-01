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
            
        # if found_dark == None:
        #     for dark in self.dark:
        #         if (dark.bin == bin and dark.subx == subx and dark.suby == suby):
        #             scaling_factor =  exp /dark.exp 
        #             ScaledDark = Frame(dark.path)
        #             ScaledDark.name = 'MasterdarkScaled_' + 'exp' + str(int(exp)) + '.fits'
        #             ScaledDark.data = dark.data * scaling_factor
        #             ScaledDark.exp = exp
        #             ScaledDark.bin = bin 
        #             ScaledDark.subx = subx 
        #             ScaledDark.suby = suby
        #             ScaledDark.imagetype = dark.imagetype
        #             ScaledDark.temp = dark.temp
        #             ScaledDark.filter = dark.filter
        #             ScaledDark.bitpix = dark.bitpix
        #             ScaledDark.bscale = dark.bscale
        #             ScaledDark.bzero = dark.bzero
        #             ScaledDark.history = f'Artificial dark scaled from dark: exp {dark.exp}, bin {dark.bin}, subx{dark.subx}, suby {dark.suby}'
        #             self.dark.append(ScaledDark)
        #             ScaledDark.SaveBDFFitsFrame()
        #             print(f'Scaling dark from Exp: {dark.exp}, Bin: {dark.bin}, Subx: {dark.subx}, Suby: {dark.suby}')
        #             return ScaledDark
        # else:
        return found_dark

        print(f'[ERROR] Dark not found. Failed to find one with params: Exp {exp}, Bin {bin}, Subx {subx}, Suby {suby}')  

    def GetFlatByFilter(self, filter, bin, subx, suby):
        for flat in self.flat:
            if (flat.filter == filter and flat.bin == bin and flat.subx == subx and flat.suby == suby):
                return flat
        print(f'[ERROR] Flat not found. Failed to find one with params: Filter {filter}, Bin {bin}, Subx {subx}, Suby {suby}')

    def GetBiasByBinning(self, bin, subx, suby):
        for bias in self.bias:
            if (bias.bin == bin and bias.subx == subx and bias.suby == suby):
                return bias        
        print(f'[ERROR] Bias not found. Failed to find one with params: Bin {bin}, Subx {subx}, Suby {suby}')
 
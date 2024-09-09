### Klasa obiektów: Masters. Przechowuje obiekty typu Frame(), które są wyznaczonymi masterramkami w celu wykorzystania ich we właściwej redukcji ramek naukowych.

class Masters():
    def __init__(self):
        self.bias = None
        self.dark = []
        self.flat = []

    def GetDarkByExpTime(self, exp, bin, subx, suby):
        for dark in self.dark:
            if (dark.exp == exp and dark.bin == bin and dark.subx == subx and dark.suby == suby):
                return dark
        
        print(f'[ERROR] Dark not found. Failed to find one with params: Exp {exp}, Bin {bin}, Subx {subx}, Suby {suby}')  

    def GetFlatByFilter(self, filter, bin, subx, suby):
        for flat in self.flat:
            if (flat.filter == filter and flat.bin == bin and flat.subx == subx and flat.suby == suby):
                return flat
        return self.flat
        print('[ERROR] Flat not found.')          
        
 
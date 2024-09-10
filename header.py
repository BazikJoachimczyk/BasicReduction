### Klasa obiektów: Header. Przechowuje dane dotyczące headera. Uzupełnia się poprzez uruchomienie funkcji OpenHeader(), której argumentem jest ścieżka pliku, którego danymi z headera uzupełniany jest obiekt Header.
from os import listdir, makedirs
from astropy.io import fits

class Header:
    def __init__(self):
        self.imagetype = ''
        self.exp = 0
        self.temp = 0
        self.filter = ''
        self.bin = []
        self.subx = 0
        self.suby = 0
        self.bscale = 0
        self.bzero = 0
        self.history = ''
        self.jd = 0
        self.object = ''
        self.ra = 0
        self.dec = 0

    def OpenHeader(self, path):
        fits_file = fits.open(path)
        fits_header = fits_file[0].header
        self.imagetype = fits_header['IMAGETYP']
        self.exp = fits_header['EXPTIME']
        self.temp = fits_header['SET-TEMP']
        self.bin = str(fits_header['XBINNING']) + ' ' + str(fits_header['YBINNING']) 
        self.subx =  str(fits_header['XORGSUBF']) 
        self.suby =  str(fits_header['YORGSUBF'])
        self.bscale = fits_header['BSCALE']
        self.bzero = fits_header['BZERO']
        self.jd = fits_header['JD']
        self.object = fits_header['OBJECT']
        if 'FILTER' in fits_header:
            self.filter = fits_header['FILTER']

        fits_file.close()
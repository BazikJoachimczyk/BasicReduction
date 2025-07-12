### Klasa obiektów: Frame. Dziedziczy wartości Headera, uzupełniając je o nowe, potrzebne do stworzenia kompletnej ramki typu fits, która zapisuje poprzez uruchomienie funkcji SaveFitsFile().

from header import Header
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from astropy.time import Time
from astropy import units as u
from astropy.io import fits
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from os.path import join
import numpy as np

Observatory = EarthLocation(lat=53.093999*u.deg, lon=18.555925*u.deg, height=70*u.m)

class Frame(Header):
    def __init__(self, path):
        Header.__init__(self)
        self.path = path
        self.data = []
        self.history = ''
        self.name = '' 
        self.bitpix = 16


    def CalculateAirmass(self):
        ObservationTime = Time(self.jd, format='jd')           # czas obserwacji w formacie rozpoznawanym przez Astropy
        ObjectCoordinates = SkyCoord(self.ra, self.dec, unit=(u.hourangle, u.deg))     # współrzędne obiektu z Headera 

        ObjectAltAz = ObjectCoordinates.transform_to(AltAz(obstime=ObservationTime, location=Observatory))          # przekształcam współrzędne na horyzontalne

        Airmass = ObjectAltAz.secz                              # secant odległości zenitalnej, czyli airmass 

        return float(Airmass) 
    

    def SaveBDFFitsFrame(self):
        hdu = fits.PrimaryHDU(data = (self.data ))#- self.bzero))
        hdull = fits.HDUList([hdu])
        save_header = hdull[0].header
        save_header['IMAGETYP'] = self.imagetype
        save_header['EXPTIME'] = self.exp
        save_header['SET_TEMP'] = self.temp 
        save_header['FILTER'] = self.filter
        save_header['XORGSUBF'] = self.subx
        save_header['XBINNING'] = self.binx
        save_header['YBINNING'] = self.biny
        save_header['YORGSUBF'] = self.suby
        save_header['BITPIX'] = self.bitpix
        #save_header['BSCALE'] = self.bscale
        #save_header['BZERO'] = self.bzero
        save_header['HISTORY'] = self.history
        hdull.writeto(join(self.path, self.name), overwrite=True)


    def SaveFitsFullHeader(self, headerPath): 
        data = np.array((self.data - self.bzero), dtype = np.float32)             

        hdu = fits.PrimaryHDU(data)
        hdull = fits.HDUList([hdu]) 


        with fits.open(headerPath) as openfits:
            save_header = openfits[0].header

        save_header['MJD'] = self.jd - 2400000.5
        save_header['HISTORY'] = self.history
        save_header['RA'] = self.ra
        save_header['DEC'] = self.dec
        save_header['AIRMASS'] = self.CalculateAirmass()
        hdull[0].header = save_header


        hdull.writeto(join(self.path, self.name), overwrite=True)
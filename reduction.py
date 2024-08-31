def Reduction(path, object, filename, Coords):                 # WERSJA Z TABLICY

            
            fits_frame = Frame(join(path, object, filename))
            fits_frame.OpenHeader(join(path, object, filename))

            with fits.open(join(path, object, filename)) as hdull:
                data = hdull[0].data
            
            masterbias = masterFrames.bias
            masterdark = masterFrames.GetDarkByExpTime(fits_frame.exp, fits_frame.bin, fits_frame.subx, fits_frame.suby)
            masterflat = masterFrames.GetFlatByFilter(fits_frame.filter, fits_frame.bin, fits_frame.subx, fits_frame.suby)

            data = data - masterbias.data
            data = data - masterdark.data
            data = data / masterflat.data 
            
            data[data > 65535] = 65535

            fits_frame.data = data 
            fits_frame.name = 'out_' + filename
            fits_frame.path = join(path, object, 'Pipeline_' + fits_frame.filter + '_' + str(int(fits_frame.exp)))
            fits_frame.history = 'Reduction: Dark -' + str(masterdark.exp) + '; Flat -' + str(masterflat.filter)
            fits_frame.ra = Coords[0]
            fits_frame.dec = Coords[1]

            if not exists(fits_frame.path):
                makedirs(fits_frame.path)


            fits_frame.SaveFitsFullHeader(join(path, object, filename))

def CalculateScienceFrames(path):

    objects = listdir(path)             # lista obiektów obserwowanych w nocy
    objects.remove('bdf')               # wyrzucam folder BDF bo to nie obiekt

    for object in objects:              # pętla dla folderów każdego obserwowanego obiektu
                                        # wkradam się z wyznaczeniem współrzędnych na podstawie jednego zdjęcia
        Coords = GetCoordsFromAstrometry(join(path,object))

        frames = listdir(join(path ,object))

        for frame in frames:
            if frame.endswith('.fit') or frame.endswith('.fits'):
                Reduction(path, object, frame, Coords)


            print('Out: ', frame)
    return
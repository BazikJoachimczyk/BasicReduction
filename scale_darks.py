import os
from astropy.io import fits
import numpy as np

import os
from astropy.io import fits
import numpy as np

def scale_darks(input_folder, output_folder, target_exposure_time):
    # Sprawdzenie, czy folder wyjściowy istnieje, jeśli nie - utworzenie
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Przetwarzanie każdego pliku w folderze input
    for filename in os.listdir(input_folder):
        if filename.endswith(".fit"):  # Zmieniono na obsługę plików .fit
            filepath = os.path.join(input_folder, filename)

            # Odczyt danych z pliku FITS
            with fits.open(filepath) as hdul:
                data = hdul[0].data
                header = hdul[0].header

                # Odczyt czasu ekspozycji z nagłówka
                original_exposure_time = header.get('EXPTIME', None)
                if original_exposure_time is None:
                    print(f"Brak informacji o czasie ekspozycji w pliku {filename}")
                    continue

                # Obliczanie współczynnika skalowania
                scaling_factor = target_exposure_time / original_exposure_time
                print(f"Przetwarzanie pliku: {filename}")
                print(f"Oryginalny czas ekspozycji: {original_exposure_time} s, Docelowy czas ekspozycji: {target_exposure_time} s")
                print(f"Współczynnik skalowania: {scaling_factor}")

                # Skalowanie danych darka
                scaled_data = data * scaling_factor

                # Aktualizacja nagłówka pliku FITS
                header['EXPTIME'] = target_exposure_time
                header.add_history(f"Dark scaled from {original_exposure_time} s to {target_exposure_time} s")

                # Zapis przeskalowanego darka do nowego pliku w folderze wyjściowym
                output_filepath = os.path.join(output_folder, filename)
                fits.writeto(output_filepath, scaled_data, header, overwrite=True)
                print(f"Plik zapisany: {output_filepath}\n")

    print(f"Skalowanie darków zakończone. Pliki zapisano w folderze: {output_folder}")

# Przykład użycia:

# Przykład użycia:
scale_darks(r"G:\90 obserwacje\20220228\bdf\Dark\Dark_40_2x2_0x0", r"G:\90 obserwacje\20220228\bdf\Dark\Dark_400_2x2_scaled", 400) 
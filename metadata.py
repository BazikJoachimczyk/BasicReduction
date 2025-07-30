from ccdproc import CCDData
from os import listdir
from os.path import join, isdir
import json
import argparse

class MetaData:
    def __init__(self, filepath: str):
        ccd = CCDData.read(filepath, unit='adu')
        hdr = ccd.header

        self.ImageType = hdr.get('IMAGETYP')
        self.ObjectName = hdr.get('OBJECT', 'Unknown')
        self.Count = 1  # Można później zliczać
        self.Exposure = hdr.get('EXPTIME', 0)
        self.BinX = hdr.get('XBINNING', 1)
        self.BinY = hdr.get('YBINNING', 1)
        self.FilterName = hdr.get('FILTER', 'Unknown')
        self.Temperature = hdr.get('SET-TEMP', None)
        self.SubframeX = hdr.get('XORGSUBF', 0)
        self.SubframeY = hdr.get('YORGSUBF', 0)

    def to_dict(self):
        return {
            "ObjectName": self.ObjectName,
            "ImageTyp": self.ImageType,
            "Count": self.Count,
            "Exposure": self.Exposure,
            "BinX": self.BinX,
            "BinY": self.BinY,
            "FilterName": self.FilterName,
            "Temperature": self.Temperature,
            "SubframeX": self.SubframeX,
            "SubframeY": self.SubframeY
        }

    def __repr__(self):
        import json
        return json.dumps(self.to_dict(), indent=2)
    

def collect_metadata(night_path: str) -> list:

    folders = [f for f in listdir(night_path) if isdir(join(night_path, f))]
    metadata_list = []

    for folder in folders:
        folder_path = join(night_path, folder)

        if folder.lower() == "bdf":
            subfolders = [sf for sf in listdir(folder_path) if isdir(join(folder_path, sf))]
            for sub in subfolders:
                subpath = join(folder_path, sub)
                files = [f for f in listdir(subpath) if f.endswith('.fit') or f.endswith('.fits')]
                if not files:
                    continue

                first_file = join(subpath, files[0])
                meta = MetaData(first_file)
                meta.ObjectName = sub  # Nazwa folderu jako "typ ramki"
                meta.Count = len(files)
                metadata_list.append(meta)
        else:
            files = [f for f in listdir(folder_path) if f.endswith('.fit') or f.endswith('.fits')]
            if not files:
                continue

            first_file = join(folder_path, files[0])
            meta = MetaData(first_file)
            meta.Count = len(files)
            metadata_list.append(meta)

    return metadata_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count metadata")
    parser.add_argument("--path", type=str, help="Path to the observation folder")
    args = parser.parse_args()

    metadata_list = collect_metadata(args.path)
    metadata_dicts = [meta.to_dict() for meta in metadata_list]
    
    print(json.dumps(metadata_dicts))    
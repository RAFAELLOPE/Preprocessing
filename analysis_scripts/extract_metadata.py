import os
import glob
import numpy as np
import pandas as pd
import pydicom
from argparse import ArgumentParser
from collections import OrderedDict

def image_plane(IOP):
    IOP_round = [round(x) for x in IOP]
    plane = np.cross(IOP_round[0:3], IOP_round[3:6])
    plane = [abs(x) for x in plane]
    if plane[0] == 1:
        return "Sagittal"
    elif plane[1] == 1:
        return "Coronal"
    elif plane[2] == 1:
        return "Axial"

def extract_metadata(studies: list):
    metadata = OrderedDict({
                            'Study_Id':list(),
                            'Serie_Id': list(),
                            'Accession_Number': list(),
                            'Series_Description': list(),
                            'TR (Repetition Time)': list(),
                            'TE (Echo Time)':list(),
                            'TI (Inversion Time)': list(),
                            'Image Plane': list(),
                            'Study Date': list(),
                            'MR Adquisition Type': list(),
                            'Patient Sex': list(),
                            'Patient Birthday': list(),
                            'Manufacturer': list(),
                            'Manufacturers Model Name': list(),
                            'Magnetic Field Strength': list(),
                            'Spacing Between Slices': list()
                            })
    for s in studies:
        if len(glob.glob(os.path.join(s, '*.dcm'))) > 0:
            img = glob.glob(os.path.join(s, '*.dcm'))[0]  #Take only the first image in the serie
            ds = pydicom.dcmread(img, stop_before_pixels=True)
            metadata['Study_Id'].append(ds[0x0020, 0x0010].value if (0x0020, 0x0010) in ds else '')
            metadata['Serie_Id'].append(ds[0x0020, 0x00E].value if (0x0020, 0x00E) in ds else '')
            metadata['Accession_Number'].append(ds[0x0008, 0x0050].value if (0x0008, 0x0050) in ds else '')
            metadata['Series_Description'].append(ds[0x0008, 0x103E].value if (0x0008, 0x103E) in ds else '')
            metadata['TI (Inversion Time)'].append(ds[0x0018,0x0082].value if (0x0018,0x0082) in ds else '')
            metadata['TR (Repetition Time)'].append(ds[0x0018,0x0080].value if (0x0018,0x0080) in ds else None)
            metadata['TE (Echo Time)'].append(ds[0x0018,0x0081].value if (0x0018,0x0081) in ds else None)
            metadata['Image Plane'].append(image_plane(ds[0x0020,0x0037].value) if (0x0020,0x0037) in ds else '')
            metadata['Study Date'].append(ds[0x0008,0x0020].value if (0x0008,0x0020) in ds else None)
            metadata['MR Adquisition Type'].append(ds[0x0018,0x0023].value if (0x0018,0x0023) in ds else '')
            metadata['Patient Sex'].append(ds[0x0010,0x0040].value if (0x0010,0x0040) in ds else '')
            metadata['Patient Birthday'].append(ds[0x0010,0x0030].value if (0x0010,0x0030) in ds else None)
            metadata['Manufacturer'].append(ds[0x0008,0x0070].value if (0x0008,0x0070) in ds else '')
            metadata['Manufacturers Model Name'].append(ds[0x0008,0x1090].value if (0x0008,0x1090) in ds else '')
            metadata['Magnetic Field Strength'].append(ds[0x0018,0x0087].value if (0x0018,0x0087) in ds else None)
            metadata['Spacing Between Slices'].append(ds[0x0018,0x0088].value if (0x0018,0x0088) in ds else None)

    return pd.DataFrame(metadata)
    
def manage_arguments():
    parser = ArgumentParser()
    parser.add_argument('--input_directory', 
                        help='Path where dicom files are stored',
                        type=str,
                        required=True,
                        metavar='-i',
                        default='')

    parser.add_argument('--output_file', 
                        help='Path where metadata CSV file is going to be stored',
                        type=str,
                        required=True,
                        metavar='-o',
                        default='')
    return parser.parse_args()

def main(args):
    input_directory = args.input_directory
    output_file = args.output_file
    assert os.path.exists(input_directory), "Input directory does not exist"
    assert output_file.endswith('.csv'), "Output file should have extension CSV"
    studies = glob.glob(os.path.join(input_directory, '*', '*'))
    df = extract_metadata(studies)
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    args = manage_arguments()
    main(args)

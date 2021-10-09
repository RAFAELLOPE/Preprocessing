import os
import glob
import numpy as np
import pandas as pd
import pydicom
from collections import OrderedDict
from striprtf.striprtf import rtf_to_text
import io
from db.db_access import DatabaseAccess

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

def anonymize_rtf(rtf_in: str, filename:str) -> str:
    text = rtf_to_text(rtf_in)
    text_in = io.StringIO(text)
    text_out = io.StringIO()
    for line in text_in:
        if ('Paciente' in line) or ('Solicitado por:' in line):
            continue
        else:
            text_out.write(line)
    text_out.seek(0)
    anonymize_rtf = text_out.getvalue()
    return anonymize_rtf

def get_forms(accesion_nums: list, **db_params) -> pd.DataFrame:
    df_result = pd.DataFrame()
    db_access = DatabaseAccess(db_params)
    L = len(accesion_nums)
    N = 1000 if 1000 < L else L
    for s in range(0, L, N):
        acc_nums = accesion_nums[s: s + N]
        if len(accesion_nums) > 1:
            sql_query = f"SELECT * \
                          FROM CITAS_INFORMES \
                          WHERE IDCita IN {acc_nums}"
        else:
            sql_query = f"SELECT * \
                          FROM CITAS_INFORMES \
                          WHERE IDCita = {acc_nums}"
        df_result = db_access.run_query(sql_query)
        if df_result.empty():
            print('NO ACCESSION NUMBERS RETURNED')
        else:
            df_result.rename(['Id_Date', 'Form'], axis=1, inplace=True)
    return df_result

def extract_dicom_metadata(series: list) -> pd.DataFrame:
    metadata = OrderedDict({
                            'Study_Id':list(),
                            'Study_Instance_UID':list(),
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
                            'Spacing Between Slices': list(),
                            'Slice Thickness': list(),
                            'Pixel Spacing': list(),
                            'Samples per Pixel': list(),
                            'Rows': list(),
                            'Columns': list(),
                            'Bits Allocated': list(),
                            'Bits Stored': list(),
                            'High Bit': list(),
                            'Pixel Representation': list(),
                            })
    for s in series:
        if len(glob.glob(os.path.join(s, '*.dcm'))) > 0:
            img = glob.glob(os.path.join(s, '*.dcm'))[0]  #Take only the first image in the serie
            ds = pydicom.dcmread(img, stop_before_pixels=True)
            metadata['Study_Id'].append(ds[0x0020, 0x0010].value if (0x0020, 0x0010) in ds else None)
            metadata['Study_Instance_UID'].append(ds[0x0020, 0x000D].value if (0x0020, 0x000D) in ds else None)
            metadata['Serie_Id'].append(ds[0x0020, 0x00E].value if (0x0020, 0x00E) in ds else None)
            metadata['Accession_Number'].append(ds[0x0008, 0x0050].value if (0x0008, 0x0050) in ds else None)
            metadata['Series_Description'].append(ds[0x0008, 0x103E].value if (0x0008, 0x103E) in ds else None)
            metadata['TI (Inversion Time)'].append(ds[0x0018,0x0082].value if (0x0018,0x0082) in ds else None)
            metadata['TR (Repetition Time)'].append(ds[0x0018,0x0080].value if (0x0018,0x0080) in ds else None)
            metadata['TE (Echo Time)'].append(ds[0x0018,0x0081].value if (0x0018,0x0081) in ds else None)
            metadata['Image Plane'].append(image_plane(ds[0x0020,0x0037].value) if (0x0020,0x0037) in ds else None)
            metadata['Study Date'].append(ds[0x0008,0x0020].value if (0x0008,0x0020) in ds else None)
            metadata['MR Adquisition Type'].append(ds[0x0018,0x0023].value if (0x0018,0x0023) in ds else None)
            metadata['Patient Sex'].append(ds[0x0010,0x0040].value if (0x0010,0x0040) in ds else None)
            metadata['Patient Birthday'].append(ds[0x0010,0x0030].value if (0x0010,0x0030) in ds else None)
            metadata['Manufacturer'].append(ds[0x0008,0x0070].value if (0x0008,0x0070) in ds else None)
            metadata['Manufacturers Model Name'].append(ds[0x0008,0x1090].value if (0x0008,0x1090) in ds else None)
            metadata['Magnetic Field Strength'].append(ds[0x0018,0x0087].value if (0x0018,0x0087) in ds else None)
            metadata['Spacing Between Slices'].append(ds[0x0018,0x0088].value if (0x0018,0x0088) in ds else None)
            metadata['Slice Thickness'].append(ds[0x0018,0x0050].value if (0x0018,0x0050) in ds else None)
            metadata['Pixel Spacing'].append(ds[0x0028,0x0030].value if (0x0028,0x0030) in ds else None)
            metadata['Samples per Pixel'].append(ds[0x0028,0x0002].value if (0x0028,0x0002) in ds else None)
            metadata['Rows'].append(ds[0x0028,0x0010].value if (0x0028,0x0010) in ds else None)
            metadata['Columns'].append(ds[0x0028,0x0011].value if (0x0028,0x0011) in ds else None)
            metadata['Bits Allocated'].append(ds[0x0028,0x0100].value if (0x0028,0x0100) in ds else None)
            metadata['Bits Stored'].append(ds[0x0028,0x0101].value if (0x0028,0x0101) in ds else None)
            metadata['High Bit'].append(ds[0x0028,0x0102].value if (0x0028,0x0102) in ds else None)
            metadata['Pixel Representation'].append(ds[0x0028,0x0103].value if (0x0028,0x0103) in ds else None)
    return pd.DataFrame(metadata)

def extract_metadata(series: list) -> pd.DataFrame:
    df_meta = extract_dicom_metadata(series)
    df_meta['Id_Date'] = df_meta['Accession_Number']


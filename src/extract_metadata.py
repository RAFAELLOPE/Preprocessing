import os
import glob
import numpy as np
import pandas as pd
import pydicom
from collections import OrderedDict
import re
from enum import Enum
from typing import Union
import datetime
from db.db_access import DatabaseAccess

class RegexAccNum(Enum):
    NORMAL = "1.(\d+).(\d{1}).(\d{1})"

def get_id_date_ext(acc_num:str, db_access: DatabaseAccess) -> Union[int, None]:
    id_date = None
    query = f"SELECT IDCita FROM CITAS_EXPLORACIONES WHERE AANN_Externo = {acc_num}"
    df_result = db_access.run_query(query)
    try:
        id_date = int(df_result['IDCita'])
    except Exception as err:
        print(err)
    return id_date

def get_id_date(acc_num:str, db_access:DatabaseAccess) -> Union[int, None]:
    id_date = None
    try:
        if re.match(RegexAccNum.NORMAL.value, acc_num):
            id_date = int(re.match(RegexAccNum.NORMAL.value, acc_num).group(1))
        else:
            id_date = get_id_date_ext(acc_num, db_access)
    except Exception as err:
        print(err)
    return id_date

def image_plane(IOP) -> str:
    IOP_round = [round(x) for x in IOP]
    plane = np.cross(IOP_round[0:3], IOP_round[3:6])
    plane = [abs(x) for x in plane]
    if plane[0] == 1:
        return "Sagittal"
    elif plane[1] == 1:
        return "Coronal"
    elif plane[2] == 1:
        return "Axial"

def extract_dicom_metadata(series: list) -> pd.DataFrame:
    metadata = OrderedDict({
                            'OriginalSeriesDir': list(),
                            'OriginalPatientId': list(),
                            'StudyId':list(),
                            'StudyInstanceUID':list(),
                            'SeriesInstanceUID': list(),
                            'AccessionNumber': list(),
                            'SeriesDescription': list(),
                            'RepetitionTime': list(),
                            'EchoTime':list(),
                            'InversionTime': list(),
                            'ImagePlane': list(),
                            'StudyDate': list(),
                            'MRAdquisitionType': list(),
                            'PatientSex': list(),
                            'PatientBirthday': list(),
                            'Manufacturer': list(),
                            'ManufacturersModelName': list(),
                            'MagneticFieldStrength': list(),
                            'SpacingBetweenSlices': list(),
                            'SliceThickness': list(),
                            'PixelSpacing': list(),
                            'SamplesPerPixel': list(),
                            'Rows': list(),
                            'Columns': list(),
                            'BitsAllocated': list(),
                            'BitsStored': list(),
                            'HighBit': list(),
                            'PixelRepresentation': list(),
                            })
    for s in series:
        if len(glob.glob(os.path.join(s, '*.dcm'))) > 0:
            img = glob.glob(os.path.join(s, '*.dcm'))[0]  #Take only the first image in the serie
            ds = pydicom.dcmread(img, stop_before_pixels=True)
            metadata['OriginalSeriesDir'].append(s)
            metadata['OriginalPatientId'].append(ds[0x0010, 0x0020].value if (0x0020, 0x0010) in ds else None)
            metadata['StudyId'].append(ds[0x0020, 0x0010].value if (0x0020, 0x0010) in ds else None)
            metadata['StudyInstanceUID'].append(ds[0x0020, 0x000D].value if (0x0020, 0x000D) in ds else None)
            metadata['SeriesInstanceUID'].append(ds[0x0020, 0x00E].value if (0x0020, 0x00E) in ds else None)
            metadata['AccessionNumber'].append(ds[0x0008, 0x0050].value if (0x0008, 0x0050) in ds else None)
            metadata['SeriesDescription'].append(ds[0x0008, 0x103E].value if (0x0008, 0x103E) in ds else None)
            metadata['InversionTime'].append(ds[0x0018,0x0082].value if (0x0018,0x0082) in ds else None)
            metadata['RepetitionTime'].append(ds[0x0018,0x0080].value if (0x0018,0x0080) in ds else None)
            metadata['EchoTime'].append(ds[0x0018,0x0081].value if (0x0018,0x0081) in ds else None)
            metadata['ImagePlane'].append(image_plane(ds[0x0020,0x0037].value) if (0x0020,0x0037) in ds else None)
            metadata['StudyDate'].append(datetime.datetime.strptime(ds[0x0008,0x0020].value, '%Y%m%d') 
                                         if (0x0008,0x0020) in ds else None)
            metadata['MRAdquisitionType'].append(ds[0x0018,0x0023].value if (0x0018,0x0023) in ds else None)
            metadata['PatientSex'].append(ds[0x0010,0x0040].value if (0x0010,0x0040) in ds else None)
            metadata['PatientBirthday'].append(ds[0x0010,0x0030].value if (0x0010,0x0030) in ds else None)
            metadata['Manufacturer'].append(ds[0x0008,0x0070].value if (0x0008,0x0070) in ds else None)
            metadata['ManufacturersModelName'].append(ds[0x0008,0x1090].value if (0x0008,0x1090) in ds else None)
            metadata['MagneticFieldStrength'].append(ds[0x0018,0x0087].value if (0x0018,0x0087) in ds else None)
            metadata['SpacingBetweenSlices'].append(ds[0x0018,0x0088].value if (0x0018,0x0088) in ds else None)
            metadata['SliceThickness'].append(ds[0x0018,0x0050].value if (0x0018,0x0050) in ds else None)
            metadata['PixelSpacing'].append(ds[0x0028,0x0030].value if (0x0028,0x0030) in ds else None)
            metadata['SamplesPerPixel'].append(ds[0x0028,0x0002].value if (0x0028,0x0002) in ds else None)
            metadata['Rows'].append(ds[0x0028,0x0010].value if (0x0028,0x0010) in ds else None)
            metadata['Columns'].append(ds[0x0028,0x0011].value if (0x0028,0x0011) in ds else None)
            metadata['BitsAllocated'].append(ds[0x0028,0x0100].value if (0x0028,0x0100) in ds else None)
            metadata['BitsStored'].append(ds[0x0028,0x0101].value if (0x0028,0x0101) in ds else None)
            metadata['HighBit'].append(ds[0x0028,0x0102].value if (0x0028,0x0102) in ds else None)
            metadata['PixelRepresentation'].append(ds[0x0028,0x0103].value if (0x0028,0x0103) in ds else None)
    return pd.DataFrame(metadata)

def extract_metadata(series: list, db_access:DatabaseAccess) -> pd.DataFrame:
    transformedPatientIDs = OrderedDict()
    df_meta = extract_dicom_metadata(series)
    
    for i, p in enumerate(set(df_meta['OriginalPatientId'])):
        transformedPatientIDs[p] = 'Sub-' + str(i)
    
    df_meta['PatientID'] = df_meta['OriginalPatientId'].apply(lambda x: transformedPatientIDs[x])
    df_meta['DateID'] = df_meta['AccessionNumber'].apply(lambda x: get_id_date(x, db_access))
    return df_meta

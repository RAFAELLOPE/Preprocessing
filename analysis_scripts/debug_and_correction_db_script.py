import glob
import os
from collections import OrderedDict
import numpy as np
import pandas as pd
import pydicom
import datetime
import dicom2nifti


def convert2nifti(df: pd.DataFrame) -> bool:
    success = True
    for s_org, s_des in zip(df['OriginalSeriesDir'], df['NiftiPath']):
        if os.path.exists(s_des):
            continue
        else:
            try: 
                dicom2nifti.convert_dicom \
                           .dicom_series_to_nifti(original_dicom_directory=s_org,
                                                  output_file=s_des)
            except Exception as e:
                print(f'DICOM-TO-NIFIT ERROR IN SERIE {s_org}; ERROR {e}')
                success = False
                continue
    return success

def get_nifti_files_with_missing_metadata(neuro_db_path:str, df:pd.DataFrame) -> list:
    nifti_processed = set(glob.glob(os.path.join(neuro_db_path, '*', '*', '*', '*.nii.gz')))
    nifti_paths = set(df['NiftiPath'])
    missing_nifti_paths = list(nifti_processed.difference(nifti_paths))
    missing_metadata = list()
    for p in missing_nifti_paths:
        r_path = p.split('/')[:-2]
        report_path = os.path.join('/'.join(r_path), 'Report', '*.txt')
        dateId = glob.glob(report_path)[0].split('/')[-1].split('.')[0]
        missing_metadata.append((p, dateId))
    return missing_metadata

    
def get_empty_folders(neuro_db_path:str)->list:
    neuro_db_paths = glob.glob(os.path.join(neuro_db_path, '*', '*', '*'))
    empty_folders = list()
    for path in neuro_db_paths:
        if (len(os.listdir(path)) == 0) & (not 'Report' in path):
            r_path = path.split('/')[0:-1]
            report_path = os.path.join('/'.join(r_path), 'Report', '*.txt')
            dateId = glob.glob(report_path)[0].split('/')[-1].split('.')[0]
            empty_folders.append((path, dateId))
    return empty_folders

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

def extract_metadata(series: list, subject:str, dateId:str) -> pd.DataFrame:
    df_meta = extract_dicom_metadata(series)
    df_meta['PatientID'] = subject
    df_meta['DateID'] = dateId
    return df_meta

if __name__ == "__main__":
    neuro_db_root_path = ''
    dcm_db_root_path = ''
    metadata_csv_path = ''
    df_metadata = pd.DataFrame()

    #empty_folders = get_empty_folders(neuro_db_path=neuro_db_root_path)
    df = pd.read_csv(metadata_csv_path)
    missing_metadata = get_nifti_files_with_missing_metadata(neuro_db_root_path, df)
    missing_studies = [(i.split('/')[-2], i.split('/')[5], d) 
                     for i, d in missing_metadata]
    missing_studies_unique = list(set(missing_studies))

    for study, subject, dateId in missing_studies_unique:
        series = glob.glob(os.path.join(dcm_db_root_path, study, '*'))
        df_tmp = extract_metadata(series, subject, dateId)
        df_metadata = pd.concat([df_metadata, df_tmp])
    
    #df_metadata.drop_duplicates(inplace=True)
    #df_metadata.reset_index(drop=True)
    
    df_metadata['NiftiPath'] = df_metadata.apply(lambda x: os.path.join(neuro_db_root_path,
                                                 str(x['PatientID']),
                                                 str(x['StudyDate'].date()),
                                                 str(x['StudyInstanceUID']),
                                                 str(x['SeriesInstanceUID']) + '.nii.gz'),
                                                 axis=1              
                                                )
    df_metadata['FormPath'] = df_metadata.apply(lambda x: os.path.join(neuro_db_root_path,
                                                str(x['PatientID']),
                                                str(x['StudyDate'].date()),
                                                'Report',
                                                str(x['DateID']) + '.txt'),
                                                axis=1
                                                )
    
    #result_nifit_conversion = convert2nifti(df_metadata)
    df = pd.concat([df, df_metadata])
    #df.drop_duplicates(inplace=True)
    #df.reset_index(drop=True)
    df.to_csv(metadata_csv_path, index=False)



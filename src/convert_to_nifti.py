import dicom2nifti
import os
import pandas as pd

def convert2nifti(df: pd.DataFrame) -> bool:
    success = True
    for s_org, s_des in zip(df['OriginalSeriesDir'], df['NiftiPath']):
        try: 
            dicom2nifti.convert_dicom \
                       .dicom_series_to_nifti(original_dicom_directory=s_org,
                                              output_file=s_des)
        except Exception as e:
            print(e)
            success = False
            continue
    return success
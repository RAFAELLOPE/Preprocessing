import dicom2nifti
import pandas as pd
import logging
import os

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
                logging.error(f'DICOM-TO-NIFIT ERROR IN SERIE {s_org}; ERROR {e}')
                success = False
                continue
    return success
import dicom2nifti
import os

def convert2nifti(series:list, path_to_nifti_files: str = None) -> bool:
    success = True
    for s in series:
        study = s.split('/')[-2]
        output_folder = os.path.join(path_to_nifti_files, study)
        output_file = os.path.join(output_folder, s + '.nii.gz')
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        try: 
            dicom2nifti.convert_dicom \
                       .covert_dicom_series_to_nifti(dicom_directory=s,
                                                     output_file=output_file)
        except Exception as e:
            print(e)
            success = False
            continue
    return success
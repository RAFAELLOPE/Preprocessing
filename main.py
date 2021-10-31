from argparse import ArgumentParser
import os
import glob
import logging
import pandas as pd
import json
from src.convert_to_nifti import convert2nifti
from src.extract_metadata import extract_metadata
from src.extract_forms import extract_forms
from db.db_access import DatabaseAccess


FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(messge)s")
LOG_FILE = "logging/preprocessing.log"

def create_directory_structure(df: pd.DataFrame) -> None:
    nifti_paths = set(df['NiftiPath'])
    report_paths = set(df['FormPath'])
    
    for npath in (nifti_paths):
        npath ='/'.join(npath.split("/")[:-1])
        try:
            os.makedirs(npath)
        except:
            continue
    
    for rpath in (report_paths):
        rpath = rpath ='/'.join(rpath.split("/")[:-1])
        try:
            os.makedirs(rpath)
        except:
            continue


def manage_arguments():
    parser = ArgumentParser()
    parser.add_argument('--input_directory',
                        help='Path where dicom files are stored',
                        type=str,
                        required=True,
                        metavar='-i',
                        default='')
    
    parser.add_argument('--output_directory',
                        help='Path where metadata and nifti images are going to be stored',
                        type=str,
                        required=True,
                        metavar='-o',
                        default='')
    
    return parser.parse_args()

def main(args):
    input_directory = args.input_directory
    output_directory = args.output_directory
    assert os.path.exists(input_directory)
    assert os.path.exists(output_directory)
    ouput_file = os.path.join(output_directory, 'metadata.csv')
    original_series = glob.glob(os.path.join(input_directory, '*','*'))
    with open('config.json', 'r') as f:
        config = json.load(f)

    irix_access = DatabaseAccess(**config['Database_params_Irix'])
    forms_access = DatabaseAccess(**config['Database_params_IrixInformes'])
    
    # Extract and save metadata
    df = extract_metadata(original_series, irix_access)

    # Generate nifti and report paths
    df['NiftiPath'] = df.apply(lambda x: os.path.join(output_directory,
                                                      str(x['PatientID']),
                                                      str(x['StudyDate'].date()),
                                                      str(x['StudyInstanceUID']),
                                                      str(x['SeriesInstanceUID']) + '.nii.gz'),
                                axis=1              
                              )

    df['FormPath'] = df.apply(lambda x: os.path.join(output_directory,
                                                     str(x['PatientID']),
                                                     str(x['StudyDate'].date()),
                                                     'Report',
                                                     str(x['DateID']) + '.txt'),
                                axis=1
                               )
    # Output csv with metadata
    df.to_csv(ouput_file, index=False)

    # Create directory structure
    create_directory_structure(df)

    # Extract reports
    result_form_extraction = extract_forms(df, forms_access)
    if(result_form_extraction):
        print('Form extraction successfully done')
    else:
        print('Error while extracting forms. Check log.')


    # Convert images to nifti
    result_nifit_conversion = convert2nifti(df)
    if(result_nifit_conversion):
        print('Nifti conversion successfully done')
    else:
        print('Error while converting to nifti. Check log.')


if __name__ == "__main__":
    args = manage_arguments()
    main(args)

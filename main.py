from argparse import ArgumentParser
import os
import glob
from src.convert_to_nifti import convert2nifti
from src.extract_metadata import extract_metadata
import logging

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(messge)s")
LOG_FILE = "logging/preprocessing.log"

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
    series = glob.glob(os.path.join(input_directory, '*','*'))
    
    # Extract and save metaddata
    df = extract_metadata(series)
    df.to_csv(ouput_file, index=False)
    
    # Convert images to nifti
    result = convert2nifti(series, output_directory)
    if(result):
        print('Nifti conversion successfully done')
    else:
        print('Error while converting to nifti. Check log.')

if __name__ == "__main__":
    args = manage_arguments()
    main(args)

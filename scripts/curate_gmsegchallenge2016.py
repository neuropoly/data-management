# Convert the input non-BIDS GmSegChallenge2016 dataset to the BIDS compliant dataset
# Details about the GmSegChallenge2016 challenge: http://niftyweb.cs.ucl.ac.uk/program.php?p=CHALLENGE
#
# The GmSegChallenge2016 dataset contains data from 4 different sites:
#   - University College London (UCL)
#   - Ecole Polytechnique de Montreal (EPM)
#   - Vanderbilt University (VDB)
#   - University Hospital Zurich (UHZ)
#
# The GmSegChallenge2016 dataset contains training and test data
#
# Example of input training data:
#   site1-sc01-image.nii.gz
#   site1-sc01-levels.txt
#   site1-sc01-mask-r1.nii.gz
#   site1-sc01-mask-r2.nii.gz
#   site1-sc01-mask-r3.nii.gz
#   site1-sc01-mask-r4.nii.gz
#   ...
#
# '-mask-r' contains both WM (pixel value 2) and GM (pixel value 1) --> WM, GM, SC segs are created within this script
#
# USAGE:
#   1) Download train and test data from Dropbox (links provided by Julien)
#   2) Run the script:
#       python3 <PATH_TO_THIS_SCRIPT>/curate_gmsegchallenge2016.py
#       -i-train <PATH_TO_TRAIN_DATA>
#       -i-test <PATH_TO_TEST_DATA>
#       -o <PATH_TO_OUTPUT_BIDS_DATASET>
#
# Authors: Jan Valosek
#

import os
import sys
import csv
import shutil
import json
import argparse
import logging
import datetime

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # default: logging.DEBUG, logging.INFO
hdlr = logging.StreamHandler(sys.stdout)
logging.root.addHandler(hdlr)

# Output BIDS prefix
prefix = 'sub-'

# There are four sites
# Details: http://niftyweb.cs.ucl.ac.uk/program.php?p=CHALLENGE
sites_conv_dict = {
    'site1': 'ucl',     # University College London
    'site2': 'epm',     # Ecole Polytechnique de Montreal
    'site3': 'uhz',     # University Hospital Zurich
    'site4': 'vdb'      # Vanderbilt University
    }

# Raters name (based on https://www.sciencedirect.com/science/article/pii/S1053811917302185#s0025)
rater_to_name = {
    1: 'Marios C. Yiannakas',
    2: 'Sara M. Dupont',
    3: 'Gergely David',
    4: 'Bailey Lyttle'
    }

# Dictionary for image filename conversion
images_conv_dict = {
    'image.nii.gz': 'T2star.nii.gz',        # raw T2star image
    }

# Dictionary for derivatives filename conversion
# mask-r contains both WM (pixel value 2) and GM (pixel value 1)
derivatives_conv_dict = {
    'mask-r': 'desc-manual_mask',
    }


def copy_file(path_file_in, path_dir_out, file_out):
    """
    Copy file from input non-BIDS dataset to BIDS compliant dataset
    :param path_file_in: path of the input non-BIDS file which will be copied
    :param path_dir_out: path of the output BIDS directory; for example sub-ucl001/anat
    :param file_out: filename of the output BIDS file; for example 'sub-ucl001_T2star.nii.nii.gz'
    :return:
    """
    # Make sure that the input file exists, if so, copy it
    if os.path.isfile(path_file_in):
        # Create anat folder if does not exist
        if not os.path.isdir(path_dir_out):
            os.makedirs(path_dir_out, exist_ok=True)
        # Construct path to the output file
        path_file_out = os.path.join(path_dir_out, file_out)
        logger.info(f'Copying {path_file_in} to {path_file_out}')
        shutil.copyfile(path_file_in, path_file_out)
        # Create a dummy json sidecar (for raw images)
        create_dummy_json_sidecar_if_does_not_exist(path_file_out)


def create_wm_seg(path_file_in, path_dir_out, file_out, rater):
    """
    Create WM seg from the input segmentation which contains both WM (pixel value 2) and GM (pixel value 1)
    :param path_file_in: path of the input non-BIDS file which will be copied
    :param path_dir_out: path of the output BIDS directory; for example sub-ucl001/anat
    :param file_out: filename of the output BIDS file; for example 'sub-ucl001_T2star.nii.nii.gz'
    :return:
    """
    # Make sure that the input file exists
    if os.path.isfile(path_file_in):
        # Create anat folder if does not exist
        if not os.path.isdir(path_dir_out):
            os.makedirs(path_dir_out, exist_ok=True)
        # Construct path to the output file
        path_file_out = os.path.join(path_dir_out, file_out)
        # Create WMseg (binarize WM (pixel value 2) and threshold out GM (pixel value 1))
        os.system('sct_maths -i ' + path_file_in + ' -bin 1 -o ' + path_file_out)
        logger.info(f'Using {path_file_in} to create WMseg: {path_file_out}')
        # Create a json sidecar
        data_json = {
            "Author": rater,
            "Label": "WM-seg-manual"
        }
        write_json(path_dir_out, file_out.replace('.nii.gz', '.json'), data_json)


def create_sc_seg(path_file_in, path_dir_out, file_out, rater):
    """
    Create SC seg from the input segmentation which contains both WM (pixel value 2) and GM (pixel value 1)
    :param path_file_in: path of the input non-BIDS segmentation
    :param path_dir_out: path of the output BIDS derivatives directory; for example derivatives/labels/sub-ucl01/anat
    :param file_out: filename of the output BIDS file; for example 'sub-ucl01_seg-manual1.nii.gz'
    :return:
    """
    # Make sure that the input file exists
    if os.path.isfile(path_file_in):
        # Create anat folder if does not exist
        if not os.path.isdir(path_dir_out):
            os.makedirs(path_dir_out, exist_ok=True)
        # Construct path to the output file
        path_file_out = os.path.join(path_dir_out, file_out)
        # Create SCseg (binarize both WM (pixel value 2) and GM (pixel value 1))
        os.system('sct_maths -i ' + path_file_in + ' -bin 0 -o ' + path_file_out)
        logger.info(f'Using {path_file_in} to create SCseg: {path_file_out}')
        # Create a json sidecar
        data_json = {
            "Author": rater,
            "Label": "SC-seg-manual"
            }
        write_json(path_dir_out, file_out.replace('.nii.gz', '.json'), data_json)


def create_gm_seg(path_file_in, path_dir_out, file_out, rater):
    """
    Create GM seg from the input segmentation which contains both WM (pixel value 2) and GM (pixel value 1)
    :param path_file_in: path of the input non-BIDS segmentation
    :param path_dir_out: path of the output BIDS derivatives directory; for example derivatives/labels/sub-ucl01/anat
    :param file_out: filename of the output BIDS file; for example 'sub-ucl01_seg-manual1.nii.gz'
    :return:
    """
    # Make sure that the input file exists
    if os.path.isfile(path_file_in):
        # Create anat folder if does not exist
        if not os.path.isdir(path_dir_out):
            os.makedirs(path_dir_out, exist_ok=True)
        # Construct path to the output file
        path_file_out = os.path.join(path_dir_out, file_out)
        # Create GMseg (threshold out WM pixels with values 2)
        os.system('sct_maths -i ' + path_file_in + ' -uthr 1 -o ' + path_file_out)
        logger.info(f'Using {path_file_in} to create GMseg: {path_file_out}')
        # Create a json sidecar
        data_json = {
            "Author": rater,
            "Label": "GM-seg-manual"
            }
        write_json(path_dir_out, file_out.replace('.nii.gz', '.json'), data_json)


def create_dummy_json_sidecar_if_does_not_exist(path_file_out):
    """
    Create an empty json sidecar
    :param path_file_out:
    :return:
    """
    # Work only with .nii.gz
    if path_file_out.endswith('.nii.gz'):
        path_json_sidecar = path_file_out.replace('.nii.gz', '.json')
        if not os.path.exists(path_json_sidecar):
            os.system('touch ' + path_json_sidecar)


def write_json(path_output, json_filename, data_json):
    """
    :param path_output: path to the output BIDS folder
    :param json_filename: json filename, for example: participants.json
    :param data_json: JSON formatted content
    :return:
    """
    with open(os.path.join(path_output, json_filename), 'w') as json_file:
        json.dump(data_json, json_file, indent=4)
        logger.info(f'{json_filename} created in {path_output}')


def create_participants_tsv(participants_tsv_list, path_output):
    """
    Write participants.tsv file
    :param participants_tsv_list: list containing ['participant_id', 'source_id', 'pathology', 'institution_id', 'institution'],
    example:[sub-torontoDCM001, DCM, 001, 01, toronto]
    :param path_output: path to the output BIDS folder
    :return:
    """
    with open(os.path.join(path_output, 'participants.tsv'), 'w') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
        tsv_writer.writerow(['participant_id', 'source_id', 'pathology', 'institution_id', 'institution'])
        for item in participants_tsv_list:
            tsv_writer.writerow(item)
        logger.info(f'participants.tsv created in {path_output}')


def create_participants_json(path_output):
    """
    Create participants.json file
    :param path_output: path to the output BIDS folder
    :return:
    """
    # Create participants.json
    data_json = {
        "participant_id": {
            "Description": "Unique Participant ID",
            "LongName": "Participant ID"
        },
        "source_id": {
            "Description": "Subject ID in the unprocessed data",
            "LongName": "Subject ID in the unprocessed data"
        },
        "pathology": {
            "Description": "Pathology",
            "LongName": "Pathology name"
        },
        "institution_id": {
            "Description": "Institution ID in the unprocessed data",
            "LongName": "Institution ID in the unprocessed data"
        },
        "institution": {
            "Description": "Human-friendly institution name",
            "LongName": "BIDS Institution ID"
        }
    }
    write_json(path_output, 'participants.json', data_json)


def create_dataset_description(path_output, datasettype):
    """
    Create dataset_description.json file
    :param path_output: path to the output BIDS folder
    :param datasettype: raw or derivative (https://bids-specification.readthedocs.io/en/stable/glossary.html#datasettype-metadata)
    :return:
    """
    data_json = {
        "BIDSVersion": "BIDS 1.8.0",
        "Name": "GmSegChallenge2016",
        "DatasetType": datasettype,
        "License": "see LICENSE file",
        "ReferencesAndLinks": "http://niftyweb.cs.ucl.ac.uk/program.php?p=CHALLENGE"
    }
    write_json(path_output, 'dataset_description.json', data_json)


def copy_license(path_dataset, path_output):
    """
    Copy license file
    :param path_dataset:
    :param path_output:
    :return:
    """
    path_file_in = os.path.join(path_dataset, 'license.txt')
    # Make sure that the input file exists
    if os.path.isfile(path_file_in):
        # Construct path to the output file
        path_file_out = os.path.join(path_output, 'LICENSE')
        # Copy
        logger.info(f'Copying {path_file_in} to {path_file_out}')
        shutil.copyfile(path_file_in, path_file_out)


def copy_script(path_output):
    """
    Copy the script itself to the path_output/code folder
    :param path_output: path to the output BIDS folder
    :return:
    """
    path_script_in = sys.argv[0]
    path_code = os.path.join(path_output, 'code')
    if not os.path.isdir(path_code):
        os.makedirs(path_code, exist_ok=True)
    path_script_out = os.path.join(path_code, sys.argv[0].split(sep='/')[-1])
    logger.info(f'Copying {path_script_in} to {path_script_out}')
    shutil.copyfile(path_script_in, path_script_out)


def get_parser():
    parser = argparse.ArgumentParser(description='Convert dataset to BIDS format.')
    parser.add_argument("-i-train",
                        help="Path to the training dataset",
                        required=True)
    parser.add_argument("-i-test",
                        help="Path to the testing dataset",
                        required=True)
    parser.add_argument("-o",
                        help="Path to the output BIDS folder",
                        required=True,
                        )
    return parser


def main():

    # Parse the command line arguments
    parser = get_parser()
    args = parser.parse_args()

    # Make sure that input args are absolute paths
    if os.path.isdir(args.i_train):
        path_train = os.path.abspath(args.i_train)
    if os.path.isdir(args.i_test):
        path_test = os.path.abspath(args.i_test)
    if os.path.isdir(args.o):
        path_output = os.path.abspath(args.o)

    # Check if input path is valid
    if not os.path.isdir(path_train):
        print(f'ERROR - {path_train} does not exist.')
        sys.exit()
    # Check if input path is valid
    if not os.path.isdir(path_test):
        print(f'ERROR - {path_test} does not exist.')
        sys.exit()
    # Remove output folder if already exists and create an empty one again
    if os.path.isdir(path_output):
        shutil.rmtree(path_output)
    os.makedirs(path_output, exist_ok=True)

    # Construct path to derivatives/labels
    path_derivatives = os.path.join(path_output, 'derivatives', 'labels')
    os.makedirs(path_derivatives, exist_ok=True)

    FNAME_LOG = os.path.join(path_output, 'bids_conversion.log')
    # Dump log file there
    if os.path.exists(FNAME_LOG):
        os.remove(FNAME_LOG)
    fh = logging.FileHandler(os.path.join(os.path.abspath(os.curdir), FNAME_LOG))
    logging.root.addHandler(fh)
    print("INFO: log file will be saved to {}".format(FNAME_LOG))

    # Print current time and date to log file
    logger.info('\nAnalysis started at {}'.format(datetime.datetime.now()))

    # Initialize list for participants.tsv
    participants_tsv_list = list()

    # Loop across sites (site1, site2, ...)
    for site_in, site_out in sites_conv_dict.items():
        # Loop across subjects (there are 20 subjects for each site)
        for index in range(1, 21):
            # Construct output subjectID, e.g., 'sub-ucl001'
            subject_out = prefix + site_out + f'{index:03d}'
            # Loop across files
            for image_in, image_out in images_conv_dict.items():
                # Loop across train and test datasets
                for path_dataset in path_train, path_test:
                    # Construct input subjectID, e.g., 'site1-sc01'
                    subject_in = site_in + '-sc' + f'{index:02d}'
                    # Construct input filename, e.g., 'site1-sc01-image.nii.gz'
                    file_in = subject_in + '-' + image_in
                    # Construct input path
                    path_file_in = os.path.join(path_dataset, file_in)

                    # Construct output filename, e.g., 'sub-ucl001_T2star.nii.gz'
                    file_out = subject_out + '_' + image_out
                    # Construct output path
                    path_dir_out = os.path.join(path_output, subject_out, 'anat')

                    # Copy file and create a dummy json sidecar if does not exist
                    copy_file(path_file_in, path_dir_out, file_out)
            # Loop across derivatives
            for image_in, image_out in derivatives_conv_dict.items():
                # Loop across 4 raters
                for rater in range(1, 5):
                    # Construct input filename, e.g., 'site1-sc01-mask-r1.nii.gz'
                    file_in = site_in + '-sc' + f'{index:02d}' + '-' + image_in + str(rater) + '.nii.gz'
                    # Construct input path
                    # Note: manual labels are available only fot the training dataset
                    path_file_in = os.path.join(path_train, file_in)

                    # Construct output SC seg filename, e.g., 'sub-ucl001_T2star_label-SC_desc-manual_mask1.nii.gz'
                    file_out_sc = subject_out + 'T2star_label-SC_' + image_out + str(rater) + '.nii.gz'
                    # Construct output GM seg filename, e.g., 'sub-ucl001_T2star_label-GM_desc-manual_mask1.nii.gz'
                    file_out_gm = subject_out + 'T2star_label-GM_' + image_out + str(rater) + '.nii.gz'
                    # Construct output WM seg filename, e.g., 'sub-ucl001_T2star_label-WM_desc-manual_mask1.nii.gz'
                    file_out_wm = subject_out + 'T2star_label-WM_' + image_out + str(rater) + '.nii.gz'
                    # Construct output derivatives path
                    path_dir_out = os.path.join(path_derivatives, subject_out, 'anat')
                    create_sc_seg(path_file_in, path_dir_out, file_out_sc, rater_to_name[rater])
                    create_gm_seg(path_file_in, path_dir_out, file_out_gm, rater_to_name[rater])
                    create_wm_seg(path_file_in, path_dir_out, file_out_wm, rater_to_name[rater])

            # Format: ['participant_id', 'source_id', 'pathology', 'institution_id', 'institution']
            participants_tsv_list.append([subject_out, subject_in, 'HC', site_in, site_out])

    create_participants_tsv(participants_tsv_list, path_output)
    create_participants_json(path_output)
    create_dataset_description(path_output, 'raw')
    create_dataset_description(os.path.join(path_output, 'derivatives'), 'derivative')
    copy_license(path_dataset, path_output)
    copy_script(path_output)


if __name__ == "__main__":
    main()

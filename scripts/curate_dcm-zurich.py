# Convert the input non-BIDS dcm-zurich dataset to the BIDS compatible dataset
# The dcm-zurich dataset contains data from DCM patients:
# Spinal cord MRI data:
#     - sagittal T2w
#     - axial T2w (upper (top) FOV)
#     - axial T2w (lower (bottom) FOV)
#     - sagittal T1w (not presented for all subjects)
#
# Note: axial T2w (upper (top) FOV) and axial T2w (lower (bottom) FOV) are stitched (merged) into one axial T2w file
# Note: "non-stitched" files (axial T2w (upper (top) FOV) and axial T2w (lower (bottom) FOV)) are included under raw
#
# Sample of the input dcm-zurich dataset:
# ├── 250791
# │		├── t2_tse_sag_384_25mm_0005
# │		│	└── s250791-113456-00001-00020-1.nii
# │		├── t2_tse_tra_oben_0006
# │		│	└── s250791-113720-00001-00015-1.nii
# │		└── t2_tse_tra_unten_0007
# │		    └── s250791-113952-00001-00015-1.nii
# ...
#
# Sample of the output BIDS dataset:
# ├── code
# │		 └── curate_dcm-zurich.py
# ├── dataset_description.json
# ├── README.md
# ├── participants.json
# ├── participants.tsv
# ├── raw
# │		 ├── sub-250791
# │		 │	 └── anat
# │		 │	     ├── sub-250791_acq-axialBottom_T2w.json
# │		 │	     ├── sub-250791_acq-axialBottom_T2w.nii.gz
# │		 │	     ├── sub-250791_acq-axialTop_T2w.json
# │		 │	     └── sub-250791_acq-axialTop_T2w.nii.gz
# ...
# ├── sub-250791
# │		 └── anat
# │		     ├── sub-250791_acq-axial_T2w.json
# │		     ├── sub-250791_acq-axial_T2w.nii.gz
# │		     ├── sub-250791_acq-sagittal_T2w.json
# │		     └── sub-250791_acq-sagittal_T2w.nii.gz
# ...
#
# USAGE:
#       python3 <PATH_TO_THIS_SCRIPT>/curate_dcm-zurich.py -i <INPUT_DATASET_PATH> -o <OUTPUT_DATASET_PATH>
#
# Authors: Jan Valosek
#

import os
import sys
import glob
import shutil
import json
import argparse
import logging
import datetime
import csv

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # default: logging.DEBUG, logging.INFO
hdlr = logging.StreamHandler(sys.stdout)
logging.root.addHandler(hdlr)


IMAGES = {
    "t2_tse_sag_384_25mm": "acq-sagittal_T2w.nii",
    "t2_tse_tra_oben": "acq-axialTop_T2w.nii",      # axial T2w (upper (top) FOV) --> will be used for stitching
    "t2_tse_tra_unten": "acq-axialBottom_T2w.nii",  # axial T2w (lower (bottom) FOV) --> will be used for stitching
    "t1_tse_sag_fit": "T1w.nii",
}
# Note: sub 323721 has t2_tse_sag_384_25mm, t2_tse_tra_oben, t2_tse_tra_unten acquired twice --> we keep the first ones (using sorted(glob.glob(...)))
# Note: sub 842197 has also t2_tse_tra_oben_wdh --> we ignore it
# Note: sub 876921 has two t2_tse_tra_unten (t2_tse_tra_unten_0007 and t2_tse_tra_unten_0010) --> we keep t2_tse_tra_unten_0007 (using sorted(glob.glob(...)))

# Note: sub 798435 has different naming convention
IMAGES_798435 = {
    "t2_tse_sag_384_25mmT2_TSE_SAG_384_25MM_0009": "acq-sagittal_T2w.nii",
    "t2_tse_tra_p2T2_TSE_TRA_P2_0011": "acq-axialTop_T2w.nii",
    "t2_tse_tra_p2T2_TSE_TRA_P2_0012": "acq-axialBottom_T2w.nii",
    "t1_tse_sag_p2T1_TSE_SAG_P2_0010": "T1w.nii",
}


def get_parser():
    parser = argparse.ArgumentParser(description='Convert dataset to BIDS format.')
    parser.add_argument("-i", "--path-input",
                        help="Path to the folder containing non-BIDS dataset.",
                        required=True)
    parser.add_argument("-o", "--path-output",
                        help="Path to the output folder where the BIDS dataset will be stored.",
                        required=True)
    return parser


def create_subject_folder_if_not_exists(path_subject_folder_out):
    """
    Check if subject's folder exists in the output dataset, if not, create it
    :param path_subject_folder_out: path to subject's folder in the output dataset
    """
    if not os.path.isdir(path_subject_folder_out):
        os.makedirs(path_subject_folder_out)
        logger.info(f'Creating directory: {path_subject_folder_out}')


def copy_nii(path_file_in, path_file_out):
    """
    Copy nii file from the input dataset to the output dataset
    :param path_file_in: path to nii file in the input dataset
    :param path_file_out: path to nii file in the output dataset
    """
    shutil.copy(path_file_in, path_file_out)
    logger.info(f'Copying: {path_file_in} --> {path_file_out}')
    gzip_nii(path_file_out)


def gzip_nii(path_nii):
    """
    Gzip nii file
    :param path_nii: path to the nii file
    :return:
    """
    # Check if file is gzipped
    if not path_nii.endswith('.gz'):
        path_gz = path_nii + '.gz'
        logger.info(f'Gzipping {path_nii} to {path_gz}')
        os.system(f'gzip -f {path_nii}')


def create_empty_json_file(path_file_out):
    """
    Create an empty json sidecar file
    :param path_file_out: path to the output file
    """
    path_json_out = path_file_out.replace('.nii', '.json')
    with open(path_json_out, 'w') as f:
        json.dump({}, f)
        logger.info(f'Created: {path_json_out}')


def write_json(path_output, json_filename, data_json):
    """
    :param path_output: path to the output BIDS folder
    :param json_filename: json filename, for example: participants.json
    :param data_json: JSON formatted content
    :return:
    """
    with open(os.path.join(path_output, json_filename), 'w') as json_file:
        json.dump(data_json, json_file, indent=4)
        # Add last newline
        json_file.write("\n")
        logger.info(f'{json_filename} created in {path_output}')


def create_participants_tsv(participants_tsv_list, path_output):
    """
    Write participants.tsv file
    :param participants_tsv_list: list containing [subject_out, pathology_out, subject_in, centre_in, centre_out],
    example:[sub-torontoDCM001, DCM, 001, 01, toronto]
    :param path_output: path to the output BIDS folder
    :return:
    """
    with open(os.path.join(path_output, 'participants.tsv'), 'w') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
        tsv_writer.writerow(['participant_id', 'pathology'])
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
        "pathology": {
            "Description": "The diagnosis of pathology of the participant",
            "LongName": "Pathology name",
            "Levels": {
                "DCM": "Degenerative Cervical Myelopathy"
            }
        }
    }
    write_json(path_output, 'participants.json', data_json)


def create_dataset_description(path_output):
    """
    Create dataset_description.json file
    :param path_output: path to the output BIDS folder
    :return:
    """
    data_json = {
        "BIDSVersion": "BIDS 1.8.0",
        "Name": "dcm-zurich",
        "DatasetType": "raw"
    }
    write_json(path_output, 'dataset_description.json', data_json)


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


def main():
    # Parse the command line arguments
    parser = get_parser()
    args = parser.parse_args()

    # Make sure that input args are absolute paths
    path_input = os.path.abspath(args.path_input)
    path_output = os.path.abspath(args.path_output)

    # Check if input path is valid
    if not os.path.isdir(path_input):
        print(f'ERROR - {path_input} does not exist.')
        sys.exit()
    # Create output folder if it does not exist
    if not os.path.isdir(path_output):
        os.makedirs(path_output, exist_ok=True)

    FNAME_LOG = os.path.join(path_output, 'bids_conversion.log')
    # Dump log file there
    if os.path.exists(FNAME_LOG):
        os.remove(FNAME_LOG)
    fh = logging.FileHandler(os.path.join(os.path.abspath(os.curdir), FNAME_LOG))
    logging.root.addHandler(fh)
    logger.info("INFO: log file will be saved to {}".format(FNAME_LOG))

    # Print current time and date to log file
    logger.info('\nAnalysis started at {}'.format(datetime.datetime.now()))

    # Initialize list for participants.tsv
    participants_tsv_list = list()

    # Get all directories names in the input path
    subjects = [os.path.basename(x) for x in glob.glob(os.path.join(path_input, '*'))]
    # Loop across subjects in input dataset
    for subject in subjects:
        # Deal with axial T2w images
        # Stitch 'acq-axialTop_T2w.nii.gz' and 'acq-axialBottom_T2w.nii.gz' into 'acq-axial_T2w.nii.gz'
        if subject == '798435':
            # This subject has a different naming convention
            path_file_top_list = sorted(glob.glob(os.path.join(path_input, subject, 't2_tse_tra_p2T2_TSE_TRA_P2_0011', '*nii')))
            path_file_bottom_list = sorted(glob.glob(os.path.join(path_input, subject, 't2_tse_tra_p2T2_TSE_TRA_P2_0012', '*nii')))
        else:
            path_file_top_list = sorted(glob.glob(os.path.join(path_input, subject, 't2_tse_tra_oben*', '*nii')))
            path_file_bottom_list = sorted(glob.glob(os.path.join(path_input, subject, 't2_tse_tra_unten*', '*nii')))
        # Check if path_file_top and path_file_bottom are not empty. If so, we cannot create the stitched file.
        if path_file_top_list and path_file_bottom_list:
            path_file_top = path_file_top_list[0]
            path_file_bottom = path_file_bottom_list[0]
            # Construct path for the output file
            path_subject_folder_out = os.path.join(path_output, 'sub-' + subject, 'anat')
            create_subject_folder_if_not_exists(path_subject_folder_out)
            path_file_stitched = os.path.join(path_subject_folder_out, 'sub-' + subject + '_acq-axial_T2w.nii')
            path_qc = os.path.join(path_output, 'qc')
            os.system('sct_image -i ' + path_file_top + ' ' + path_file_bottom + ' -stitch -o ' + path_file_stitched +
                      ' -qc ' + path_qc + ' -qc-subject sub-' + subject)
            gzip_nii(path_file_stitched)
            create_empty_json_file(path_file_stitched)
        # Some subjects have only a single axial T2w image --> no stitching needed, just copy the file
        else:
            logger.warning(f'Could not find t2_tse_tra_oben* and t2_tse_tra_unten* for subject {subject}')
            logger.warning(f'Checking if a single t2_tse_tra file exists for subject {subject}')
            path_file_in_list = sorted(glob.glob(os.path.join(path_input, subject, 't2_tse_tra*', '*nii')))
            if path_file_in_list:
                # Construct path for the output file
                path_file_in = path_file_in_list[0]
                path_subject_folder_out = os.path.join(path_output, 'sub-' + subject, 'anat')
                create_subject_folder_if_not_exists(path_subject_folder_out)
                path_file_out = os.path.join(path_subject_folder_out, 'sub-' + subject + '_acq-axial_T2w.nii')
                # Copy nii file to the output dataset
                copy_nii(path_file_in, path_file_out)
                # Create an empty json sidecar file
                create_empty_json_file(path_file_out)
                with open(os.path.join(path_output, 'no_stitching.log'), 'a') as txt_file:
                    txt_file.write(f'sub-{subject}: has only a single t2_tse_tra file --> no stitching done\n')
            else:
                with open(os.path.join(path_output, 'missing_files.log'), 'a') as txt_file:
                    txt_file.write(f'sub-{subject}: no t2_tse_tra file found\n')

        # Deal with other sequences ('acq-sagittal_T2w.nii.gz' and 'T1w.nii.gz') and save the original non-stitched
        # images to 'raw' folder as 'acq-axialTop_T2w.nii.gz' and 'acq-axialBottom_T2w.nii.gz'
        # Get all sequences for this subject
        sequences = [os.path.basename(x) for x in sorted(glob.glob(os.path.join(path_input, subject, '*')))]
        for sequence in sequences:
            # glob.glob returns a list of files --> get the first item
            path_file_in = glob.glob(os.path.join(path_input, subject, sequence, '*nii'))[0]
            # Deal with different filenames for subject 798435
            if subject == '798435':
                images = IMAGES_798435
            else:
                images = IMAGES
            for image_in, image_out in images.items():
                if image_in in path_file_in:
                    # Save the original non-stitched images to 'raw' folder as 'acq-axialTop_T2w.nii.gz' and
                    # 'acq-axialBottom_T2w.nii.gz'
                    if "Top" in image_out or "Bottom" in image_out:
                        path_subject_folder_out = os.path.join(path_output, 'raw', 'sub-' + subject, 'anat')
                    # Save 'acq-sagittal_T2w.nii.gz' and 'T1w.nii.gz' to root folder
                    else:
                        path_subject_folder_out = os.path.join(path_output, 'sub-' + subject, 'anat')
                    create_subject_folder_if_not_exists(path_subject_folder_out)
                    # Construct path for the output file
                    path_file_out = os.path.join(path_subject_folder_out, 'sub-' + subject + '_' + image_out)
                    # Copy nii file to the output dataset
                    copy_nii(path_file_in, path_file_out)
                    # Create an empty json sidecar file
                    create_empty_json_file(path_file_out)
        # Aggregate subjects for participants.tsv
        participants_tsv_list.append(['sub-' + subject, 'DCM'])

    create_participants_tsv(participants_tsv_list, path_output)
    create_participants_json(path_output)
    create_dataset_description(path_output)
    copy_script(path_output)


if __name__ == "__main__":
    main()
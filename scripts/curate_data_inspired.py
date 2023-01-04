# Convert the input non-BIDS INSPIRED dataset to the BIDS compliant dataset
# The INSPIRED dataset contains data from two centers (Toronto, Zurich) across three pathologies (DCM, SCI, HC)
# Spinal cord MRI data:
#       - DWI (A-P and P-A phase encoding)
#       - T1w sag
#       - T2w sag
#       - T2w tra
#       - T2star tra
# Brain MRI data:
#       - DWI (A-P and P-A phase encoding)
#       - MPM (multi-parameter mapping)
#
# USAGE:
#       python3 <PATH_TO_THIS_SCRIPT>/curate_data_inspired.py -i <INPUT_DATASET_PATH>/INSPIRED -o <OUTPUT_DATASET_PATH>/INSPIRED_bids
#
# Authors: Jan Valosek

import os
import re
import sys
import csv
import shutil
import json
import glob
import argparse
import logging
import datetime

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # default: logging.DEBUG, logging.INFO
hdlr = logging.StreamHandler(sys.stdout)
logging.root.addHandler(hdlr)

prefix = 'sub-'

# There are two input datasets: `01` and `02`. `01` represents Toronto, `02` represents Zurich
# Details: https://github.com/neuropoly/data-management/issues/184#issuecomment-1329250514
centres_conv_dict = {
    '01': 'toronto',
    '02': 'zurich'
    }

pathologies_conv_dict = {
    'csm': 'DCM',
    'hc': 'HC',
    'sci': 'SCI'
    }

# Dictionary for image filename conversion
# Note: we use label `acq-cspine` to differentiate spine imaging from brain
# Note: we use label `acq-cspine` over `bp-cspine` since BIDS BEP025 is not merged yet (and thus does not pass bids-validator)
# BIDS BEP025 Proposal: https://docs.google.com/document/d/1chZv7vAPE-ebPDxMktfI9i1OkLNR2FELIfpVYsaZPr4
# Discussion `acq-cspine` vs `bp-cspine`: https://github.com/neuropoly/data-management/pull/185#issuecomment-1347421696
images_spine_conv_dict = {
    'dwi.nii.gz': 'dir-AP_acq-cspine_dwi.nii.gz',
    'dwi.bval': 'dir-AP_acq-cspine_dwi.bval',
    'dwi.bvec': 'dir-AP_acq-cspine_dwi.bvec',
    'dwi_reversed_blip.nii.gz': 'dir-PA_acq-cspine_dwi.nii.gz',
    't1_sag.nii.gz': 'acq-cspine_T1w.nii.gz',
    't2_sag.nii.gz': 'acq-cspineSagittal_T2w.nii.gz',
    't2_tra.nii.gz': 'acq-cspineAxial_T2w.nii.gz',
    'pd_medic.nii.gz': 'acq-cspine_T2star.nii.gz'
    }

# TODO - include also DWI derivatives
derivatives_spine_conv_dict = {
    't2_seg.nii.gz': 'acq-cspineAxial_T2w_label-SC_mask.nii.gz',
    'gm_seg.nii.gz': 'acq-cspine_T2star_label-GM_mask.nii.gz',
    'wm_seg.nii.gz': 'acq-cspine_T2star_label-WM_mask.nii.gz'
}

# Dictionary for brain image filename conversion
images_brain_conv_dict = {
    'dwi.nii.gz': 'dir-AP_dwi.nii.gz',
    'dwi.bval': 'dir-AP_dwi.bval',
    'dwi.bvec': 'dir-AP_dwi.bvec',
    'dwi_reversed_blip.nii.gz': 'dir-PA_dwi.nii.gz',
    }


def copy_file(path_file_in, path_dir_out, file_out):
    """
    Copy file from input non-BIDS dataset to BIDS compliant dataset
    :param path_file_in: path of the input non-BIDS file which will be copied
    :param path_dir_out: path of the output BIDS directory; for example sub-torontoDCM001/dwi
    :param file_out: filename of the output BIDS file; for example 'sub-torontoDCM001_dir-AP_acq-cspine_dwi.nii.gz'
    :return:
    """
    # Make sure that the input file exists, if so, copy it
    if os.path.isfile(path_file_in):
        # Create dwi or anat folder if does not exist
        if not os.path.isdir(path_dir_out):
            os.makedirs(path_dir_out, exist_ok=True)
        # Construct path to the output file
        path_file_out = os.path.join(path_dir_out, file_out)
        logger.info(f'Copying {path_file_in} to {path_file_out}')
        shutil.copyfile(path_file_in, path_file_out)
        # Create a dummy json sidecar for all files except of MPM (for MPM we copy original .json sidecars)
        if 'MPM' not in file_out:
            create_dummy_json_sidecar_if_does_not_exist(path_file_out)


# TODO - do we want to create just a empty json sidecar? Or do we want to include some params there?
def create_dummy_json_sidecar_if_does_not_exist(path_file_out):
    # Work only with .nii.gz (i.e., ignore .bval and .bvec files)
    if path_file_out.endswith('.nii.gz'):
        path_json_sidecar = path_file_out.replace('.nii.gz', '.json')
        if not os.path.exists(path_json_sidecar):
            os.system('touch ' + path_json_sidecar)


def read_json_file(path_to_file):
    """
    Read json file and fetch relevant parameters (SeriesDescription, SeriesDescription, EchoTime) for MPM images
    :param path_to_file: path to input json file
    :return:
    """
    # Note: open command returned error for the `02/hc/008/bl/brain/mpm_raw/s837313-0004-00001-000880-05.json` file:
    #   UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe4 in position 1340: invalid continuation byte
    # Thus, `encoding="ISO-8859-1"` has to be used. Source: https://stackoverflow.com/a/19706723
    with open(path_to_file, encoding="ISO-8859-1") as p:
        loaded_json = json.load(p)
        series_description = loaded_json['acqpar'][0]['SeriesDescription']
        flip_angle = loaded_json['acqpar'][0]['FlipAngle']
        echo_time = loaded_json['acqpar'][0]['EchoTime']
        return series_description, flip_angle, echo_time


def construct_mpm_bids_filename(mpm_files_dict, path_output, subject_out):
    """
    Construct BIDS compliant filename for MPM images, e.g. 'acq-T1w_echo-1_flip-1_mt-off_MPM'
    Then, call function to copy the input non-BIDS MPM file to BIDS compliant MPM file
    :param mpm_files_dict: dict with SeriesDescription, FlipAngle, and EchoTime across all MPM files
    :param path_output: path to the output BIDS folder
    :param subject_out: output BIDS subjectID containing centre name and pathology, e.g., 'sub-torontoDCM001'
    :return:
    """
    mpm_to_bids = dict()
    # Get unique values
    unique_SeriesDescription = set([key[0] for key in mpm_files_dict.keys()])
    unique_FlipAngle = set([key[1] for key in mpm_files_dict.keys()])
    unique_EchoTime = set([key[2] for key in mpm_files_dict.keys()])
    # Construct BIDS compliant filename, e.g. 'acq-T1w_echo-1_flip-1_mt-off_MPM'
    for echo_idx, echo_time in enumerate(unique_EchoTime, start=1):
        for flip_idx, flip_angle in enumerate(unique_FlipAngle, start=1):
            for series_description in unique_SeriesDescription:
                if '_mt_' in series_description or '_MT_' in series_description:
                    BIDS_label = 'acq-MTw' + '_echo-' + str(echo_idx) + '_flip-' + str(flip_idx) + '_mt-on_MPM'
                elif '_pd_' in series_description or '_PD_' in series_description:
                    BIDS_label = 'acq-PDw' + '_echo-' + str(echo_idx) + '_flip-' + str(flip_idx) + '_mt-off_MPM'
                elif '_t1_' in series_description or '_T1_' in series_description:
                    BIDS_label = 'acq-T1w' + '_echo-' + str(echo_idx) + '_flip-' + str(flip_idx) + '_mt-off_MPM'
                # Find original MPM filename
                if (series_description, flip_angle, echo_time) in mpm_files_dict.keys():
                    mpm_file = mpm_files_dict[(series_description, flip_angle, echo_time)]
                    mpm_to_bids[mpm_file] = BIDS_label

    # Construct path to the output BIDS compliant directory
    path_dir_out = os.path.join(path_output, subject_out, 'anat')
    # Copy individual mpm raw files to the output BIDS directory
    for sequence_params, path_file_in in mpm_files_dict.items():
        label_out = mpm_to_bids[path_file_in]               # e.g., 'acq-MTw_echo-1_flip-1_mt-on_MPM'
        # Construct output filename, e.g., 'sub-torontoDCM001_acq-MTw_echo-1_flip-1_mt-on_MPM.nii.gz'
        file_out = subject_out + '_' + label_out + '.nii.gz'
        # Copy MPM nii file
        copy_file(path_file_in, path_dir_out, file_out)
        # Copy MPM json sidecar
        # Note: re.sub has to be used instead of .replace to match both '.nii' and '.nii.gz'
        copy_file(re.sub('.nii(.gz)*', '.json', path_file_in), path_dir_out, file_out.replace('.nii.gz', '.json'))


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
        tsv_writer.writerow(['participant_id', 'pathology', 'data_id', 'institution_id', 'institution'])
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
            "Description": "Pathology",
            "LongName": "Pathology name"
        },
        "data_id": {
            "Description": "Subject ID as under duke/mri/",
            "LongName": "Subject ID"
        },
        "institution_id": {
            "Description": "Institution ID as under duke/mri/",
            "LongName": "Institution ID"
        },
        "institution": {
            "Description": "Institution ID after conversion to BIDS",
            "LongName": "BIDS Institution ID"
        }
    }
    with open(os.path.join(path_output, 'participants.json'), 'w') as json_participants:
        json.dump(data_json, json_participants, indent=4)
        logger.info(f'participants.json created in {path_output}')


def create_dataset_description(path_output):
    """
    Create dataset_description.json file
    :param path_output: path to the output BIDS folder
    :return:
    """
    dataset_description = {"BIDSVersion": "BIDS 1.8.0",
                           "Name": "inspired"
                           }
    with open(os.path.join(path_output, 'dataset_description.json'), 'w') as json_dataset_description:
        json.dump(dataset_description, json_dataset_description, indent=4)
        logger.info(f'dataset_description.json created in {path_output}')


def create_bidsignore_file(path_output):
    """
    Create .bidsignore file defining files that should be ignored by the bids-validator.
    We want to exclude files with `acq-cspine` tag since BEP025
    (https://docs.google.com/document/d/1chZv7vAPE-ebPDxMktfI9i1OkLNR2FELIfpVYsaZPr4/edit#heading=h.4k1noo90gelw)
    is not merged to  BIDS yet
    :param path_output:
    :return:
    """
    bidsignore = "*/*/*_bp-cspine*"
    with open(os.path.join(path_output, '.bidsignore'), 'w') as bidsignore_file:
        bidsignore_file.write(f'{bidsignore}\n')
        logger.info(f'.bidsignore created in {path_output}')


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


def get_parameters():
    parser = argparse.ArgumentParser(description='Convert dataset to BIDS format.')
    parser.add_argument("-i", "--path-input",
                        help="Path to folder containing the dataset to convert to BIDS",
                        required=True)
    parser.add_argument("-o", "--path-output",
                        help="Path to the output BIDS folder",
                        required=True,
                        )
    arguments = parser.parse_args()
    return arguments


def main(path_input, path_output):
    # Make sure that input args are absolute paths
    if os.path.isdir(path_input):
        path_input = os.path.abspath(path_input)
    if os.path.isdir(path_output):
        path_output = os.path.abspath(path_output)

    # Check if input path is valid
    if not os.path.isdir(path_input):
        print(f'ERROR - {path_input} does not exist.')
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

    # Loop across centers (01, 02)
    for centre_in, centre_out in centres_conv_dict.items():
        # Loop across pathologies (hc, csm, sci)
        for pathology_in, pathology_out in pathologies_conv_dict.items():
            # Loop across subjects (001, ...)
            for subject_in in sorted(glob.glob(os.path.join(path_input, centre_in, pathology_in, '*'))):
                # If the input subject folder is .tar.gz, extract it
                if subject_in.endswith('.tar.gz'):
                    logger.info(f'Unpacking tar archive {subject_in}...')
                    os.system("tar -xf " + subject_in + " --directory " + os.path.join(path_input, centre_in, pathology_in))
                    # Remove '.tar.gz' from the subject_in variable
                    subject_in = subject_in.replace('.tar.gz', '')
                # Get subjectID (e.g., 001)
                subject_id = subject_in.split(sep='/')[-1]
                # Loop across regions (brain or cord)
                for region in ['brain', 'cord']:
                    # Construct output subjectID containing centre name and pathology, e.g., 'sub-torontoDCM001'
                    subject_out = prefix + centre_out + pathology_out + subject_id
                    if region == 'cord':
                        # Process spinal cord anatomical and DWI data
                        # Loop across files
                        for image_in, image_out in images_spine_conv_dict.items():
                            # Construct path to the input file
                            path_file_in = os.path.join(path_input, centre_in, pathology_in, subject_in, 'bl', region, image_in)
                            # Construct output filename, e.g., 'sub-torontoDCM001_dir-AP_acq-cspine_dwi.nii.gz'
                            file_out = subject_out + '_' + image_out
                            # Construct path to the output BIDS compliant directory
                            if 'dwi' in image_in:
                                path_dir_out = os.path.join(path_output, subject_out, 'dwi')
                            else:
                                path_dir_out = os.path.join(path_output, subject_out, 'anat')

                            # Copy file and create a dummy json sidecar if does not exist
                            copy_file(path_file_in, path_dir_out, file_out)
                        # Deal with derivatives (i.e., spinal cord segmentation) located in `sct_processing` folder
                        path_sct_processing = os.path.join(path_input, centre_in, pathology_in, subject_in, 'bl',
                                                           region, 'sct_processing')
                        if os.path.isdir(path_sct_processing):
                            for image_in, image_out in derivatives_spine_conv_dict.items():
                                if 't2' in image_in:
                                    contrast = 't2'
                                else:
                                    contrast = 't2s'
                                # Construct path to the input file
                                path_file_in = os.path.join(path_sct_processing, contrast, image_in)
                                # Construct output filename, e.g., 'sub-torontoDCM001_acq-cspineAxial_T2w_label-SC_mask.nii.gz'
                                file_out = subject_out + '_' + image_out
                                # Construct path to the output BIDS compliant derivatives directory
                                path_dir_out = os.path.join(path_derivatives, subject_out, 'anat')
                                copy_file(path_file_in, path_dir_out, file_out)
                    elif region == 'brain':
                        # Process DWI brain files
                        # Loop across files
                        for image_in, image_out in images_brain_conv_dict.items():
                            # Construct path to the input file
                            path_file_in = os.path.join(path_input, centre_in, pathology_in, subject_in, 'bl', region, image_in)
                            # Construct output filename, e.g., 'sub-torontoDCM001_dir-AP_dwi.nii.gz'
                            file_out = subject_out + '_' + image_out
                            # Construct path to the output BIDS compliant directory
                            if 'dwi' in image_in:
                                path_dir_out = os.path.join(path_output, subject_out, 'dwi')

                            # Copy file and create a dummy json sidecar if does not exist
                            copy_file(path_file_in, path_dir_out, file_out)

                        # Process raw MPM images (located in brain/mpm_raw folder)
                        mpm_raw_folder_path = os.path.join(path_input, centre_in, pathology_in, subject_in, 'bl',
                                                           region, 'mpm_raw')
                        if os.path.isdir(mpm_raw_folder_path):
                            mpm_files_dict = dict()
                            # Loop across individual MPM files
                            for mpm_file in glob.glob(os.path.join(mpm_raw_folder_path, '*.nii*')):
                                # Get SeriesDescription, FlipAngle, and EchoTime for each MPM file
                                # Note: re.sub has to be used instead of .replace to match both '.nii' and '.nii.gz'
                                json_file = re.sub('.nii(.gz)*', '.json', mpm_file)
                                # Make sure json sidecar exist
                                if os.path.isfile(json_file):
                                    series_description, flip_angle, echo_time = read_json_file(json_file)
                                    # Collect SeriesDescription, FlipAngle, and EchoTime across all MPM files
                                    mpm_files_dict[series_description, flip_angle, echo_time] = mpm_file

                            # Construct BIDS compliant filename for MPM images
                            if bool(mpm_files_dict):
                                construct_mpm_bids_filename(mpm_files_dict, path_output, subject_out)
                            # In some cases, there are no json sidecars for MPM images, thus mpm_files_dict is empty
                            else:
                                logger.warning(f'WARNING: There are no json sidecars in {mpm_raw_folder_path}. '
                                               f'Skipping this subject.')

                participants_tsv_list.append([subject_out, pathology_out, subject_id, centre_in, centre_out])
                # Remove uncompressed subject dir (i.e., keep only .tar.gz).
                # (but first, make sure that .tar.gz subject exists)
                if os.path.isfile(subject_in + '.tar.gz'):
                    shutil.rmtree(subject_in)

    create_participants_tsv(participants_tsv_list, path_output)
    create_participants_json(path_output)
    create_dataset_description(path_output)
    #create_bidsignore_file(path_output)
    copy_script(path_output)


if __name__ == "__main__":
    args = get_parameters()
    main(args.path_input, args.path_output)

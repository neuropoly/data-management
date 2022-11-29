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
# Authors: Jan Valosek

import os
import sys
import shutil
import json
import glob
import argparse

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
# Note: we use label `bp-cspine` to differentiate spine imaging from brain
# Details: BIDS BEP025 Proposal (https://docs.google.com/document/d/1chZv7vAPE-ebPDxMktfI9i1OkLNR2FELIfpVYsaZPr4)
images_spine_conv_dict = {
    'dwi.nii.gz': 'dir-AP_bp-cspine_dwi.nii.gz',
    'dwi.bval': 'dir-AP_bp-cspine_dwi.bval',
    'dwi.bvec': 'dir-AP_bp-cspine_dwi.bvec',
    'dwi_reversed_blip.nii.gz': 'dir-PA_bp-cspine_dwi.nii.gz',
    't1_sag.nii.gz': 'bp-cspine_T1w.nii.gz',
    't2_sag.nii.gz': 'acq-coronal_bp-cspine_T2w.nii.gz',
    't2_tra.nii.gz': 'acq-axial_bp-cspine_T2w.nii.gz',
    'pd_medic.nii.gz': 'bp-cspine_T2star.nii.gz'
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
    :param file_out: filename of the output BIDS file; for example 'sub-torontoDCM001_bp-cspine_dir-AP_dwi.nii.gz'
    :return:
    """
    # Make sure that the input file exists, if so, copy it
    if os.path.isfile(path_file_in):
        # Create dwi or anat folder if does not exist
        if not os.path.isdir(path_dir_out):
            os.makedirs(path_dir_out, exist_ok=True)
        # Construct path to the output file
        path_file_out = os.path.join(path_dir_out, file_out)
        print(f'Copying {path_file_in} to {path_file_out}')
        shutil.copyfile(path_file_in, path_file_out)
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
    with open(path_to_file) as p:
        loaded_json = json.load(p)
        series_description = loaded_json['acqpar'][0]['SeriesDescription']
        flip_angle = loaded_json['acqpar'][0]['SeriesDescription']
        echo_time = loaded_json['acqpar'][0]['EchoTime']
        return series_description, flip_angle, echo_time


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
    # Check if input path is valid
    if not os.path.isdir(path_input):
        print(f'ERROR - {path_input} does not exist.')
        sys.exit()
    # Remove output folder if already exists and create an empty one again
    if os.path.isdir(path_output):
        shutil.rmtree(path_output)
    os.makedirs(path_output, exist_ok=True)

    # Loop across centers (01, 02)
    for centre_in, centre_out in centres_conv_dict.items():
        # Loop across pathologies (hc, csm, sci)
        for pathology_in, pathology_out in pathologies_conv_dict.items():
            # Loop across subjects (001, ...)
            for sub_index, subject_in in enumerate(glob.glob(os.path.join(path_input, centre_in, pathology_in, '*')),
                                                   start=1):
                # If the input subject folder is .tar.gz, extract it
                if subject_in.endswith('.tar.gz'):
                    os.system("tar -xf " + subject_in + " --directory " + os.path.join(path_input, centre_in, pathology_in))
                    # TODO - consider what to do with extracted folders once the BIDS conversion is done.
                    #  Delete them and keep only original .tar.gz files?
                    # Remove '.tar.gz' from the subject_in variable
                    subject_in = subject_in.replace('.tar.gz', '')
                # Loop across regions (brain or cord)
                for region in ['brain', 'cord']:
                    if region == 'cord':
                        # Loop across files
                        for image_in, image_out in images_spine_conv_dict.items():
                            # Construct path to the input file
                            path_file_in = os.path.join(path_input, centre_in, pathology_in, subject_in, 'bl', region, image_in)
                            # Construct output subjectID containing centre name and pathology, e.g., 'sub-torontoDCM001'
                            subject_out = prefix + centre_out + pathology_out + f"{sub_index:03d}"
                            # Construct output filename, e.g., 'sub-torontoDCM001_bp-cspine_dir-AP_dwi.nii.gz'
                            file_out = subject_out + '_' + image_out
                            # Construct path to the output BIDS compliant directory
                            if 'dwi' in image_in:
                                path_dir_out = os.path.join(path_output, subject_out, 'dwi')
                            else:
                                path_dir_out = os.path.join(path_output, subject_out, 'anat')

                            # Copy file and create a dummy json sidecar if does not exist
                            copy_file(path_file_in, path_dir_out, file_out)
                    elif region == 'brain':
                        # Loop across files
                        for image_in, image_out in images_brain_conv_dict.items():
                            # Construct path to the input file
                            path_file_in = os.path.join(path_input, centre_in, pathology_in, subject_in, 'bl', region, image_in)
                            # Construct output subjectID containing centre name and pathology, e.g., 'sub-torontoDCM001'
                            subject_out = prefix + centre_out + pathology_out + f"{sub_index:03d}"
                            # Construct output filename, e.g., 'sub-torontoDCM001_dir-AP_dwi.nii.gz'
                            file_out = subject_out + '_' + image_out
                            # Construct path to the output BIDS compliant directory
                            if 'dwi' in image_in:
                                path_dir_out = os.path.join(path_output, subject_out, 'dwi')

                            # Copy file and create a dummy json sidecar if does not exist
                            copy_file(path_file_in, path_dir_out, file_out)

                        # Convert raw MPM images
                        mpm_raw_folder_path = os.path.join(path_input, centre_in, pathology_in, subject_in, 'bl',
                                                           region, 'mpm_raw')
                        if os.path.isdir(mpm_raw_folder_path):
                            # Loop across individual MPM files
                            for mpm_file in glob.glob(os.path.join(mpm_raw_folder_path, '*.nii*')):
                                series_description, flip_angle, echo_time = read_json_file(mpm_file.replace('.nii', '.json'))
                                # TODO - finish MPM files conversion


if __name__ == "__main__":
    args = get_parameters()
    main(args.path_input, args.path_output)

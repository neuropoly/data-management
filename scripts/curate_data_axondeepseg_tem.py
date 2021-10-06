import glob
import os
import shutil
import json
import argparse
import subprocess
import csv

images = {
    "image.png": "_TEM.png"
}

der = {
    "mask.png": "_TEM_seg-axonmyelin-manual.png",
    "mask_seg-axon-manual.png": "_TEM_seg-axon-manual.png",
    "mask_seg-myelin-manual.png": "_TEM_seg-myelin-manual.png"
}


def get_parameters():
    parser = argparse.ArgumentParser(description='This script is curating dataset data_axondeepseg_tem to BIDS')
    parser.add_argument("-d", "--data",
                        help="Path to folder containing the dataset to be curated",
                        required=True)
    parser.add_argument("-o", "--outputdata",
                        help="Path to output folder",
                        required=True,
                        )
    arguments = parser.parse_args()
    return arguments


def create_json_sidecar(path_folder_sub_id_bids, item_out):
    data_json = {"PixelSize": [0.00236, 0.00236],
                 "FieldOfView": [8.88, 5.39],
                 "BodyPart": "BRAIN",
                 "BodyPartDetails": "splenium",
                 "SampleFixation": "2% paraformaldehyde, 2.5% glutaraldehyde",
                 "Environment": "exvivo"
                 }
    item_out = item_out.replace('_TEM.png', '_TEM.json')
    with open(os.path.join(path_folder_sub_id_bids, item_out), 'w') as json_file:
        json.dump(data_json, json_file, indent=4)


def main(root_data, output_data):

    contents_ds = [subdir for subdir in os.listdir(root_data) if os.path.isdir(os.path.join(root_data, subdir))]
    contents_ds.sort()

    # Loop across contents of each subdirectory
    for subdir in contents_ds:
        sub_id = "sub-nyuMouse" + subdir.split('_')[3]
        sample_id = subdir.split('_')[4]
        path_subdir = os.path.join(root_data, subdir)
        contents_subdir = os.listdir(path_subdir)
        sub_bids_full = sub_id + "_sample-" + sample_id
        for file in contents_subdir:
            path_file_in = os.path.join(path_subdir, file)
            if file in images:
                path_sub_id_dir_out = os.path.join(output_data, sub_id, 'microscopy')
                path_file_out = os.path.join(path_sub_id_dir_out, sub_bids_full + images[file])
                os.makedirs(path_sub_id_dir_out, exist_ok=True)
                create_json_sidecar(path_sub_id_dir_out, sub_id + '_TEM.png')
            elif file in der:
                path_sub_id_dir_out = os.path.join(output_data, 'derivatives', 'labels', sub_id, 'microscopy')
                path_file_out = os.path.join(path_sub_id_dir_out, sub_bids_full + der[file])
                os.makedirs(path_sub_id_dir_out, exist_ok=True)
            else:
                # not a file we recognize
                continue
            shutil.copyfile(path_file_in, path_file_out)

    sub_list = sorted(d for d in os.listdir(output_data) if d.startswith("sub-"))

    # Create participants.tsv and samples.tsv
    with open(output_data + '/samples.tsv', 'w') as samples, \
            open(output_data + '/participants.tsv', 'w') as participants:
        tsv_writer_samples = csv.writer(samples, delimiter='\t', lineterminator='\n')
        tsv_writer_samples.writerow(["sample_id", "participant_id", "sample_type"])
        tsv_writer_participants = csv.writer(participants, delimiter='\t', lineterminator='\n')
        tsv_writer_participants.writerow(["participant_id", "species"])
        for subject in sub_list:
            row_sub = []
            row_sub.append(subject)
            row_sub.append('mus musculus')
            tsv_writer_participants.writerow(row_sub)
            subject_samples = sorted(glob.glob(os.path.join(output_data, subject, 'microscopy', '*.png')))
            for file_sample in subject_samples:
                row_sub_samples = []
                row_sub_samples.append(os.path.basename(file_sample).split('_')[1])
                row_sub_samples.append(subject)
                row_sub_samples.append('tissue')
                tsv_writer_samples.writerow(row_sub_samples)

    # Create dataset_description.json
    dataset_description = {"Name": "data_axondeepseg_tem",
                           "BIDSVersion": "1.6.0 - BEP031 v0.0.4",
                           "License": "MIT"
                           }

    with open(output_data + '/dataset_description.json', 'w') as json_file:
        json.dump(dataset_description, json_file, indent=4)

    # Create dataset_description.json for derivatives/labels
    dataset_description_derivatives = {"Name": "data_axondeepseg_tem labels",
                                       "BIDSVersion": "1.6.0 - BEP031 v0.0.4",
                                       "PipelineDescription": {
                                           "Name": "Axon and myelin manual segmentation labels"
                                       }}

    with open(output_data + '/derivatives/labels/dataset_description.json', 'w') as json_file:
        json.dump(dataset_description_derivatives, json_file, indent=4)

    # Create participants.json
    data_json = {
        "participant_id": {
            "Description": "Unique participant ID"
        },
        "species": {
            "Description": "Binomial species name from the NCBI Taxonomy (https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi)"
        }
    }

    with open(output_data + '/participants.json', 'w') as json_file:
        json.dump(data_json, json_file, indent=4)

    # Create samples.json
    data_json = {
        "sample_id": {
            "Description": "Sample ID"
        },
        "participant_id": {
            "Description": "Participant ID from whom tissue samples have been acquired"
        },
        "sample_type": {
            "Description": "Type of sample from ENCODE Biosample Type (https://www.encodeproject.org/profiles/biosample_type)"
        }
    }

    with open(output_data + '/samples.json', 'w') as json_file:
        json.dump(data_json, json_file, indent=4)

        # Create README
        with open(output_data + '/README', 'w') as readme_file:
            print("""
    - TEM dataset for AxonDeepSeg (https://axondeepseg.readthedocs.io/) 
    - 158 brain (splenium) samples from 20 mice with axon and myelin manual segmentation labels. 
    - 20160718_nyu_mouse_25_0002 was omitted because it contained incomplete data in the folder smb://duke.neuro.polymtl.ca/projects/axondeepseg/raw_data/data_TEM/3_done/ 
    - Original source files are located in smb://duke.neuro.polymtl.ca/histology/mouse/20160718_nyu_mouse 
    - Our original paper (Zaimi et al. 2018), the FOV was reported to be 6x9 um^2. This is because 1) these original values were reported in the original data reference (below), and 2) our images here are slightly cropped at the bottom relative to the original data in order to remove the scale bar. 
    - Our original paper (Zaimi et al. 2018) reported the resolution as being 0.002 micrometer, which was (for an unknown reason) rounded in the paper from the true value of 0.00236 micrometer, as reported in the original data reference (below). 
    - Reference for the origin of the dataset: Jelescu, I. O. et al. In vivo quantification of demyelination and recovery using compartment-specific diffusion MRI metrics validated by electron microscopy. Neuroimage 132, 104–114 (2016). 
    - BIDS version 1.6.0 - Microscopy BEP031 version 0.0.4 (2021-07-13T15:14:00) 
    """, file=readme_file)


if __name__ == "__main__":
    args = get_parameters()
    main(args.data, args.outputdata)

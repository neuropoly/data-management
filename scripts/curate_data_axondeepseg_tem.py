import os
import shutil
import json
import argparse

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


def create_path_sub_id_dir_out(path_sub_id_dir_out):
    if not os.path.isdir(path_sub_id_dir_out):
        os.makedirs(path_sub_id_dir_out)


def main(root_data, output_data):

    # Remove macOS .DS_Store
    os.system("find " + root_data + " -name '.DS_Store' -type f -delete")

    # Remove output_data if exists to start clean
    if os.path.isdir(output_data):
        shutil.rmtree(output_data)
    os.makedirs(output_data, exist_ok=True)

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
                create_path_sub_id_dir_out(path_sub_id_dir_out)
                create_json_sidecar(path_sub_id_dir_out, sub_id + '_TEM.png')
            if file in der:
                path_sub_id_dir_out = os.path.join(output_data, 'derivatives', 'labels', sub_id, 'microscopy')
                path_file_out = os.path.join(path_sub_id_dir_out, sub_bids_full + der[file])
                create_path_sub_id_dir_out(path_sub_id_dir_out)
            shutil.copy(path_file_in, path_file_out)

    sub_list = os.listdir(output_data)
    sub_list.remove('derivatives')
    sub_list.sort()

    # Write additional files
    import csv
    participants = []
    samples = []
    for subject in sub_list:
        row_sub = []
        row_sub.append(subject)
        participants.append(row_sub)
        list_samples = []
        for sample in os.listdir(os.path.join(output_data, subject, 'microscopy')):
            if sample.endswith('.png'):
                list_samples.append(sample)
        list_samples.sort()
        for file_sample in list_samples:
            row_sub_samples = []
            row_sub_samples.append(subject)
            row_sub_samples.append(file_sample.split('_')[1])
            row_sub_samples.append('tissue')
            samples.append(row_sub_samples)

    # Create participants.tsv
    with open(output_data + '/participants.tsv', 'w') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
        tsv_writer.writerow(["participant_id"])
        for item in participants:
            tsv_writer.writerow(item)

    # Create samples.tsv
    with open(output_data + '/samples.tsv', 'w') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
        tsv_writer.writerow(["participant_id", "sample_id", "sample_type"])
        for item in samples:
            tsv_writer.writerow(item)

    # Create dataset_description.json
    dataset_description = {"Name": "data_axondeepseg_tem",
                           "BIDSVersion": "1.6.0 - BEP031 v0.0.4",
                           "License": "MIT"
                           }

    with open(output_data + '/dataset_description.json', 'w') as json_file:
        json.dump(dataset_description, json_file, indent=4)

    # Create participants.json
    data_json = {"participant_id": {
        "Description": "Unique Participant ID",
        "LongName": "Participant ID"
    }}

    with open(output_data + '/participants.json', 'w') as json_file:
        json.dump(data_json, json_file, indent=4)

    # Create samples.json
    data_json = {"participant_id": {
        "Description": "Unique Participant ID",
        "LongName": "Participant ID"
         },
        "sample_id": {
            "Description": "Sample ID",
            "LongName": "Sample ID"
        },
        "sample_type": {
            "Description": "Sample type",
            "LongName": "Sample type"
        }
    }

    with open(output_data + '/samples.json', 'w') as json_file:
        json.dump(data_json, json_file, indent=4)

    # Create README
    with open(output_data + '/README', 'w') as readme_file:
        readme_file.write('Dataset for data_axondeepseg_tem.')


if __name__ == "__main__":
    args = get_parameters()
    main(args.data, args.outputdata)

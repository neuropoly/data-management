import os
import shutil
import json
import argparse

root_data = '/Users/alex/data/basel-mp2rage_raw'
output_data = '/Users/alex/data/basel-mp2rage_raw_curated'


def get_parameters():
    parser = argparse.ArgumentParser(description='This script is curating dataset Delbono Wakehealth to BIDS')
    parser.add_argument("-d", "--data",
                        help="Path to folder containing the dataset to be curated",
                        required=True)
    parser.add_argument("-o", "--outputdata",
                        help="Path to output folder",
                        required=True,
                        )
    arguments = parser.parse_args()
    return arguments


def main(root_data, output_data):
    if os.path.isdir(output_data):
        shutil.rmtree(output_data)
    os.makedirs(output_data, exist_ok=True)

    dict_images = {
        "MP2RAGE_UNI_Images.nii.gz": "_UNIT1.nii.gz"
    }

    dict_der = {
        "lesion_mask_sc.nii.gz": "_UNIT1_lesion-manual.nii.gz"
    }

    for dirs, subdirs, files in os.walk(root_data):
        for file in files:
            if file.endswith('.nii.gz') and file in dict_images or file in dict_der:
                path_file_in = os.path.join(dirs, file)
                path = os.path.normpath(path_file_in)
                subid_bids = 'sub-' + (path.split(os.sep))[5]
                flag_der = False
                if file.endswith('lesion_mask_sc.nii.gz'):
                    path_subid_bids_dir_out = os.path.join(output_data, 'derivatives', 'labels', subid_bids, 'anat')
                    flag_der = True
                else:
                    path_subid_bids_dir_out = os.path.join(output_data, subid_bids, 'anat')
                if not os.path.isdir(path_subid_bids_dir_out):
                    os.makedirs(path_subid_bids_dir_out)
                if not flag_der:
                    path_file_out = os.path.join(path_subid_bids_dir_out, subid_bids + dict_images[file])
                else:
                    path_file_out = os.path.join(path_subid_bids_dir_out, subid_bids + dict_der[file])
                shutil.copy(path_file_in, path_file_out)

        for dirName, subdirList, fileList in os.walk(output_data):
            for file in fileList:
                if file.endswith('.nii.gz'):
                    originalFilePath = os.path.join(dirName, file)
                    jsonSidecarPath = os.path.join(dirName, file.split(".")[0] + '.json')
                    if not os.path.exists(jsonSidecarPath):
                        print("Missing: " + jsonSidecarPath)
                        if file.endswith('lesion-manual.nii.gz'):
                            data_json_label = {}
                            data_json_label[u'Author'] = "USB"
                            data_json_label[u'Label'] = "lesion-manual"
                            with open(jsonSidecarPath, 'w') as outfile:
                                outfile.write(json.dumps(data_json_label, indent=2, sort_keys=True))
                            outfile.close()
                        else:
                            os.system('touch ' + jsonSidecarPath)

    sub_list = os.listdir(output_data)
    sub_list.remove('derivatives')

    sub_list.sort()

    import csv

    participants = []
    for subject in sub_list:
        row_sub = []
        row_sub.append(subject)
        row_sub.append('n/a')
        row_sub.append('n/a')
        participants.append(row_sub)

    print(participants)
    with open(output_data + '/participants.tsv', 'w') as tsv_file:
        tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
        tsv_writer.writerow(["participant_id", "sex", "age"])
        for item in participants:
            tsv_writer.writerow(item)

    # Create participants.json
    data_json = {"participant_id": {
        "Description": "Unique Participant ID",
        "LongName": "Participant ID"
        },
        "sex": {
            "Description": "M or F",
            "LongName": "Participant sex"
        },
        "age": {
            "Description": "yy",
            "LongName": "Participant age"}
    }

    with open(output_data + '/participants.json', 'w') as json_file:
        json.dump(data_json, json_file, indent=4)

    # Create dataset_description.json
    dataset_description = {"BIDSVersion": "BIDS 1.6.0",
                           "Name": "basel-mp2rage"
                           }

    with open(output_data + '/dataset_description.json', 'w') as json_file:
        json.dump(dataset_description, json_file, indent=4)

    # Create README
    with open(output_data + '/README', 'w') as readme_file:
        readme_file.write('Dataset for basel-mp2rage.')


if __name__ == "__main__":
    args = get_parameters()
    main(args.data, args.outputdata)

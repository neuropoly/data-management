import os
import shutil
import json
import argparse


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
    os.makedirs(path_output, exist_ok=True)
    input_files = sorted(os.listdir(path_input))
    for file in input_files:
        sub_no = file.split('.')[0].split('_')[2]
        path_file_in = os.path.join(path_input,file)
        subid_bids = 'sub-P' + sub_no
        path_subid_bids_dir_out = os.path.join(path_output, 'derivatives', 'labels', subid_bids, 'anat')
        path_file_out = os.path.join(path_output,'derivatives')
        path_file_out = os.path.join(path_subid_bids_dir_out, subid_bids + '_UNIT1_lesion-manual2.nii.gz')
        os.makedirs(path_subid_bids_dir_out, exist_ok=True)

        shutil.copy(path_file_in,path_file_out)

    for dirName, subdirList, fileList in os.walk(path_output):
        for file in fileList:
            if file.endswith('.nii.gz'):
                originalFilePath = os.path.join(dirName, file)
                jsonSidecarPath = os.path.join(dirName, file.split('.')[0] + '.json')
                if not os.path.exists(jsonSidecarPath):
                    print("Missing: " + jsonSidecarPath)
                    if file.endswith('lesion-manual2.nii.gz'):
                        data_json_label = {}
                        data_json_label['Author'] = "Katrin"
                        data_json_label['Label'] = "lesion-manual2"
                        with open(jsonSidecarPath, 'w') as outfile:
                            outfile.write(json.dumps(data_json_label, indent=2, sort_keys=True))
                        outfile.close()


if __name__ == "__main__":
    args = get_parameters()
    main(args.path_input, args.path_output)

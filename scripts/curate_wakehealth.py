import os
import shutil
import json
import argparse


def get_parameters():
    parser = argparse.ArgumentParser(description='This script is curating dataset Delbono Wakehealth to BIDS')
    parser.add_argument("-d", "--data",
                        help="Path to folder containing the dataset to be curated",
                        required=True)
    args = parser.parse_args()
    return args


def create_json_sidecar(path_folder_sub_id_bids, item_out):
    data_json = {"BodyPartDetails": "Tibialis nerves",
                 "SampleStaining": "Toluidine Blue",
                 "PixelSize": [0.226, 0.22753],
                 "Environment": "exvivo",
                 "Manufacturer": "Hamamatsu",
                 "ManufacturersModelName": "NanoZoomer Slide Scanner",
                 }
    item_out = item_out.replace('_photo.tif', '_BF.json')
    with open(os.path.join(path_folder_sub_id_bids, item_out), 'w') as json_file:
        json.dump(data_json, json_file, indent=4)


def main(root_data):
    output_data = os.path.join(root_data + '_curated')

    # Remove macOS .DS_Store
    os.system("find " + root_data + " -name '.DS_Store' -type f -delete")

    if os.path.isdir(output_data):
        shutil.rmtree(output_data)
    os.makedirs(output_data)

    subdatasets = os.listdir(root_data)
    counter_move = 0
    counter_file_in = 0

    # Loop across subdirectories
    for ds in subdatasets:
        path_dataset = os.path.join(root_data, ds)
        contents_ds = os.listdir(path_dataset)
        contents_ds.sort()
        roi_no = 1
        previous_sub_id_bids = ''

        # Loop across contents of each subdirectory
        for item in contents_ds:
            sub_id_initial = item.split(' - ')[0]
            if sub_id_initial.find('_'):
                sub_id_initial = sub_id_initial.split('_')[0]
            sub_id_initial = sub_id_initial.replace(' ', '')
            sub_id_initial = sub_id_initial.replace('-', '')
            path_item_in = os.path.join(path_dataset, item)
            counter_file_in = counter_file_in + 1
            sub_id_bids = 'sub-' + sub_id_initial
            sample_id_bids = 'sample- ' + sub_id_initial
            path_folder_sub_id_bids = os.path.join(output_data, sub_id_bids, 'microscopy')
            if not os.path.isdir(path_folder_sub_id_bids):
                os.makedirs(path_folder_sub_id_bids)

            # Curate ROI
            if sub_id_bids == previous_sub_id_bids:
                if (len(item.split('_z0_')) > 1):
                    item_out = sub_id_bids + '_' + sample_id_bids + '_chunk-' + str(roi_no) + '_BF.tif'
                    roi_no = roi_no + 1
            else:
                roi_no = 1
            previous_sub_id_bids = sub_id_bids

            # Curate preview
            if item.endswith('_x0.625_z0.tif'):
                item_out = sub_id_bids + '_' + sample_id_bids + '_photo.tif'
                create_json_sidecar(path_folder_sub_id_bids, item_out)

            path_item_out = os.path.join(path_folder_sub_id_bids, item_out)
            shutil.copy(path_item_in, path_item_out)
            counter_move = counter_move + 1

        print("Counter files before move: " + str(counter_file_in))
        print("Counter moved files: " + str(counter_move))

    sub_list = os.listdir(output_data)
    sub_list.sort()

    # Write additional files
    import csv
    participants = []
    samples = []
    for subject in sub_list:
        row_sub = []
        row_sub_samples = []
        row_sub.append(subject)
        participants.append(row_sub)
        row_sub_samples.append(subject)
        row_sub_samples.append(subject.replace('sub', 'sample'))
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
    dataset_description = {"BIDSVersion": "BIDS 1.6.0 and BEP031 version 0.0.3",
                           "Name": "Delbono Wakehealth"
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
        "Description": "Unique ID",
        "LongName": "Participant ID"
         },
        "sample_id": {
            "Description": "Unique ID",
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
        readme_file.write('Dataset for Delbono Wakehealth.')

if __name__ == "__main__":
    args = get_parameters()
    main(args.data)

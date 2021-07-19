import argparse
import pandas as pd
from csv import reader


def get_parameters():
    parser = argparse.ArgumentParser(description='Curate duplicates duke.')
    parser.add_argument("-i", "--path-input",
                        help="Path to folder containing the log csv",
                        required=True)
    parser.add_argument("-o", "--path-output",
                        help="Path to the output BIDS folder",
                        required=False,
                        )
    arguments = parser.parse_args()
    return arguments


def main(path_input, path_output):
    # content_initial_csv = pd.read_csv(path_input, error_bad_lines=False)
    # print(content_initial_csv)

    # open file in read mode
    match = ['Duplicate Group']
    with open(path_input, 'r') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        # Iterate over each row in the csv using reader object
        match_group = []
        for row in csv_reader:
            # row variable is a list that represents a row in csv
            # print(row)
            if row == match:
                print(match_group[4:])
                # input("push to continue")
                match_group = []
            match_group.append(row)


            # if row == []:
            #     print("empty")
            #     input("push to continue")

if __name__ == "__main__":
    args = get_parameters()
    main(args.path_input, args.path_output)

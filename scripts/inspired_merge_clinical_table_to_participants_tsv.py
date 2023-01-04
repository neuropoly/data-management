#
# Merge table with clinical data for DCM patients (provided Patrick Freund, Balgrist) with INSPIRED participants.tsv
#
# Note - pandas.read_excel requires openpyxl library (pip install openpyxl or conda install openpyxl)
#
# Authors: Jan Valosek
#

import os
import argparse
import shutil

import pandas as pd

# For zurich site, subjectIDs match between clinical table and participants.tsv (i.e., ID 1 in clinical table
# corresponds to sub-zurichDCM001 in participants.tsv, ID 2 corresponds to sub-zurichDCM002, etc.)
# But for toronto site, subjectIDs do not match (i.e., ID 25 in clinical table corresponds to sub-torontoDCM001 in
# participants.tsv, ID 26 corresponds to sub-torontoDCM005, etc.)
# This dict thus allows the merge of both tables.
#   - keys are subject ID from clinical table
#   - values are subject ID for DCM patients from participants.tsv
subject_ID_dict = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 7,
    8: 8,
    9: 9,
    10: 10,
    11: 11,
    12: 12,
    13: 13,
    14: 14,
    15: 15,
    16: 16,
    17: 17,
    18: 18,
    19: 19,
    20: 20,
    21: 21,
    22: 22,
    23: 23,
    24: 24,
    25: 1,
    26: 5,
    27: 6,
    28: 7,
    29: 8,
    30: 9,
    31: 10,
    32: 15,
    33: 17,
    34: 18,
    35: 19,
    36: 21,
    37: 22,
    38: 23,
    }


def get_parser():
    parser = argparse.ArgumentParser(description='Convert dataset to BIDS format.')
    parser.add_argument("-participants-file",
                        help="INSPIRED participants.tsv file",
                        required=True)
    parser.add_argument("-clinical-file",
                        help="Excel table (.xlsx) with clinical data for DCM patients.",
                        required=True,
                        )
    return parser


def main():
    # Parse the command line arguments
    parser = get_parser()
    args = parser.parse_args()

    # Read input .tsv and .xlsx tables as Pandas DataFrames
    if os.path.isfile(args.participants_file):
        print('Reading: {}'.format(args.participants_file))
        participants_df = pd.read_csv(args.participants_file, sep='\t', header=0)
    else:
        raise FileNotFoundError(f'{args.participants_file} not found')
    if os.path.isfile(args.clinical_file):
        print('Reading: {}'.format(args.clinical_file))
        # skip first two rows because they contain legend
        clinical_df = pd.read_excel(args.clinical_file, skiprows=[0, 1])
    else:
        raise FileNotFoundError(f'{args.clinical_file} not found')

    # Insert list of DCM subjectIDs from participants.tsv into clinical table to allow merge
    # Note: 'source_id' is used to match with column in participants.tsv
    clinical_df.insert(1, 'source_id', list(subject_ID_dict.values()))
    # Insert a new column with institutions in lower case (toronto, zurich) into clinical table to allow merge
    # Note: 'institution' is used to match with column in participants.tsv
    clinical_df['institution'] = [x.lower() for x in clinical_df['Site']]

    # First, merge clinical table to participants.tsv
    # Note: we work here only with DCM since there is overlap in 'source_id' with other pathologies
    temp_df = pd.merge(participants_df[participants_df['pathology'] == 'DCM'], clinical_df,
                       on=['institution', 'source_id'])
    # Drop columns from 'temp_df' (they are already included in the participants.tsv)
    temp_df = temp_df.drop(['pathology', 'source_id', 'institution_id', 'institution', 'ID', 'Site'], axis=1)
    # Now, merge 'temp_df' back to the participants.tsv
    final_df = pd.merge(participants_df, temp_df, on='participant_id', how='outer')

    # Convert pd column names to lowercase
    final_df = final_df.rename(columns=str.lower)
    # Replace spaces in pd column names by '_'
    final_df.columns = final_df.columns.str.replace(' ', '_')

    # Rename female to F and male to M
    final_df = final_df.replace({"sex": {'female': 'F', 'male': 'M'}})

    # Backup original participants.tsv
    shutil.move(args.participants_file, args.participants_file.replace('.tsv', '_backup.tsv'))

    # Save merged pd as .tsv
    print('Saving: {}'.format(args.participants_file))
    final_df.to_csv(args.participants_file, sep='\t', na_rep='n/a')


if __name__ == "__main__":
    main()

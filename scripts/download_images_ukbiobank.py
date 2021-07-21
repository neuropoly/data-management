# Info on ukbiobank download data: https://docs.google.com/document/d/1fqAxMm46GhxeW3O6ELlkl7CXztbQawJFoXHWFkQuet8/edit?usp=sharing
# https://biobank.ctsu.ox.ac.uk/~bbdatan/Accessing_UKB_data_v2.3.pdf

# Clone repo on ~/code

# Checkout to af/download_ukbiobank

# Copy ukbfetch, selected_subjects.csv, k54531r40796.key to beluga ~/code

# module avail python
# module load python/3.9.6
# virtualenv --no-download ENV
# pip install --no-index --upgrade pip
# pip install pandas
# chmod +x ukbfetch
# source ENV/bin/activate

import os
import pandas as pd
import shutil
import datetime
from os.path import expanduser

def check_authkey(output_subject_folder,path_key,new_authkey_path):
    flag_authkey = False
    if not os.path.exists(new_authkey_path):
        shutil.copy (path_key, new_authkey_path)
        flag_authkey = True
    return flag_authkey

PATH_DUKE = expanduser("~")

path_scripts = PATH_DUKE + '/projects/def-jcohen/ukbiobank/data-in/ukbfetch'
path_main_csv_data = PATH_DUKE+ '/projects/def-jcohen/ukbiobank/data-in/selected_subjects.csv'
path_key = PATH_DUKE + '/projects/def-jcohen/ukbiobank/data-in/k54531r40796.key'
path_output_folder = PATH_DUKE + '/projects/def-jcohen/ukbiobank'

# Generate list of subjects that have T1, T2 and dwi images

content_main_csv = pd.read_csv(path_main_csv_data)

list_good_subjects = content_main_csv['eid'].tolist()

desired_no_of_subjects = 5572
list_good_subjects=list_good_subjects[0:desired_no_of_subjects-1]

# Loop across subjects and check what has been downloaded on duke/mri
# If the subject/images are not there it will download the images

for subject in list_good_subjects:
    print('\nChecking subject: '+str(subject))
    output_subject_folder = os.path.join(path_output_folder, str(subject), 'zip')
    new_authkey_path = os.path.join(output_subject_folder, 'authkey.key')
    if not os.path.exists(output_subject_folder):
        os.makedirs(output_subject_folder)
    os.chdir(output_subject_folder)

    path_T1w = os.path.join(output_subject_folder, str(subject)+ '_20252_2_0.zip')
    if not os.path.exists(path_T1w):
        print('\nDownload T1w:')
        flag_authkey = check_authkey(output_subject_folder,path_key,new_authkey_path)
        command = path_scripts + ' -e'+ str(subject) + ' -d20252_2_0 -aauthkey.key'
        os.system(command)
    else:
        print('\nFound T1w, skipping download.')
        
    path_T2w = os.path.join(output_subject_folder, str(subject)+ '_20253_2_0.zip')
    if not os.path.exists(path_T2w):
        print('\nDownload T2w')
        flag_authkey = check_authkey(output_subject_folder,path_key,new_authkey_path)
        command = path_scripts + ' -e'+ str(subject) + ' -d20253_2_0 -aauthkey.key'
        os.system(command)
    else:
        print('\nFound T2w, skipping download.')

    path_dwi = os.path.join(output_subject_folder, str(subject)+ '_20218_2_0.zip')
    if not os.path.exists(path_dwi):
        print('\nDownload dwi')
        flag_authkey = check_authkey(output_subject_folder,path_key,new_authkey_path)
        command = path_scripts + ' -e'+ str(subject) + ' -d20218_2_0 -aauthkey.key'
        os.system(command)
    else:
        print('\nFound dwi, skipping download.')
    
    if os.path.exists(new_authkey_path):
        os.remove (new_authkey_path)

    if os.path.exists(os.path.join(output_subject_folder, 'fetched.lis')):
        os.remove (os.path.join(output_subject_folder, 'fetched.lis'))
    print('\n#####################################')

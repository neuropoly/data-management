This repository deals with datalad usage and maintenance for managing the internal database at NeuroPoly Lab.

- [Installing datalad](#installing-datalad)
- [Adding a new dataset](#adding-a-new-dataset)
- [Regular usage (for users)](#regular-usage-for-users)
- [Maintenance (for IT staff)](#maintenance-for-it-staff)
- [Documentation](#documentation)
---------------------------------------------

# Installing datalad

## Requirements

Datalad equires Python, Git, git-annex, and potentially Pythons package manager pip.
If you are deploying datalad for a dataset on a shared drive mounted via cifs, make sure the mount has the *nobrl* option activated.

## Installing on Ubuntu 18.04

1. Add neurodebian to package source list.
```
wget -O- http://neuro.debian.net/lists/bionic.us-ca.libre | sudo tee /etc/apt/sources.list.d/neurodebian.sources.list
sudo apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9

sudo apt-get update

sudo apt-get install datalad
```
2. Check version of datalad. It should be >=0.12. 
```
apt-cache policy datalad
```

## Installing on OSX

- Install [miniconda 3](https://docs.conda.io/en/latest/miniconda.html#macosx-installers)
- Run installer:
  ```
  bash Miniconda3-latest-MacOSX-x86_64.sh -b -p
  ```
- Create venv and activate it:
  ```
  source miniconda3/etc/profile.d/conda.sh
  yes | conda create -n datalad python=3.6
  conda activate datalad  # to run each time you'd like to use datalad
  ```
- Install datalad
  ```
  pip install datalad
  ```
  
# Adding a new dataset

```
datalad create -c text2git --description "YOURDESCRIPTION" datalad-YOURDATASETNAME
```

## Ignore changes in .DS_Store files

Add .gitignore in the dataset root with the following contents (for OSX):

```
.DS_Store
```

# Regular usage (for users)

## Get the list of available versions of a dataset
```
git tag -l
```

## Checkout to specific tag version of a dataset
```
git checkout TAG
```

## How to come back to previous state of repository

You can use `git checkout HASH` to come back to a previous version of the dataset. More details [here](http://handbook.datalad.org/en/latest/basics/101-137-history.html#viewing-previous-versions-of-files-and-datasets).

# Maintenance (for IT staff)
All maintenance operations should be done via a Linux station inside NeuroPoly's VLAN (e.g. joplin, abbey).
## Migrate a dataset to DataLad

```bash
# Go to directory that you would like to transform into datalad folder
cd sct_testing/large
# Remove ugly Apple-related files
find . -name '.DS_Store' -type f -delete
# Rename folder of interest to temp
cd ..
mv sct_testing/large sct_testing/large_tmp
# Create datalad folder
datalad create -c text2git large
# Copy the contents from temp folder
cp -a large_tmp/. large
# Save DataLad dataset
cd large
datalad save -m "initial save"
```

## Nightly backup to duke
This will be added in the cron job of the system admin since it requires grmes credentials for the mount.
The sync has to be done before 9pm (time when nightly backup is made of duke on grappelli).

```bash
0 18 * * * rsync -av --progress /mnt/nvme/datalad/large/ ~/duke/sct_testing/large/
```

## Check dataset status

In order to check for untracked changes, use the command: 

```
datalad status
```

## Save changes to dataset

To save all changes, use the command:

```
datalad save -m "DETAILS_ABOUT_CHANGES"
```

To save changes for specific file, use the command:

```
datalad save -m "DETAILS_ABOUT_CHANGES" FILEPATH
```

# Nicer looking output (add this as an alias 'glg' to your .bashrc)
```
git log --pretty=oneline --decorate --all --graph
```


## Check log of all changes
```
git log

```

## Add/remove tag to datalad dataset
```
datalad save -m "MESSAGE" --version-tag "X.Y.Z" 
```

If you want to add a tag to an existing commit:
```
git tag -a X.Y.Z COMMIT_HASH -m "MESSAGE"
```

If you want to remove the tag:
```
git tag -d TAG
```

## Datalad systemic checkup for changes

One can add the checkup in the cron job of the system:
1. Copy `datalad_check_notification.py` in `/etc/cron.d`.
2. Add entry to crontab (in root user) by running:
```
crontab -e
```
3. Add the following line:
```
0 * * * * python /etc/cron.d/datalad_check_notification.py -d PATH_TO_DATALAD_DATASET
```

## Check the contents of 2 folders
```
find ~/duke/sct_testing/large/ -type f -exec md5sum {} + | sort -k 2 > dir1.txt
find ~/duke/sct_testing/DataLad-large/ -type f -exec md5sum {} + | sort -k 2 > dir2.txt

diff -u dir1.txt dir2.txt > diff_dir_1_2.txt

du -sh ~/duke/sct_testing/large/
du -sh ~/duke/sct_testing/DataLad-large/
```

## Testing procedure

See [wiki page](https://github.com/neuropoly/datalad/wiki/testing-datalad).

# Documentation

Here is a list of useful links:
- http://www.repronim.org/ohbm2018-training/03-01-reproin/
- https://neurostars.org/t/how-to-crawl-with-datalad/2754
- http://git-annex.branchable.com/special_remotes/
- https://github.com/khanlab/datalad/wiki
- https://neurostars.org/t/datalad-setting-up-a-special-remote-with-google-cloud-platform-storage-bucket/1929
- https://neurostars.org/t/upload-to-openneuro/2112/3
- http://handbook.datalad.org/en/latest/

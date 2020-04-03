# Datalad
Repo that deals with datalad aspects for internal use

- [Requirements][#requirements]
- [Install on ubuntu 18.04][#how-to-install-datalad-on-ubuntu-1804]
## Requirements

Datalad equires Python, Git, git-annex, and potentially Pythons package manager pip.
If you are deploying datalad for a dataset on a shared drive mounted via cifs, make sure the mount has the *nobrl* option activated.

## How to install Datalad on Ubuntu 18.04?

1. Add neurodebian to pacakge source list.
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

## Create Datalad dataset

```
datalad create -c text2git --description "YOURDESCRIPTION" DataLad-YOURDATASETNAME
```

### Ignore changes in .DS_Store files

Add .gitignore in the dataset root with the following contents:

```
.DS_Store
```

### Check dataset status

In order to check for untracked changes, use the command: 

```
datalad status
```

### Save changes to dataset

To save all changes, use the command:

```
datalad save -m "DETAILS_ABOUT_CHANGES"
```

To save changes for specific file, use the command:

```
datalad save -m "DETAILS_ABOUT_CHANGES" FILEPATH
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
## Testing
- how does it work
- who can connect to it
- how to fetch data from another station
- how to add data
- who can add data
- what is the versioning strategy/convention
- how is duke windows file system dealing with data fetching (we’ve seen errors in the past)
- how is duke/grappelli backuping dealing with git-annex




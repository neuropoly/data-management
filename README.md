# Neuropoly Data Management

This repository deals with dataset usage and maintenance at [NeuroPoly Lab](https://www.neuro.polymtl.ca).

We run an [internal server](./internal-server.md) so private datasets can be kept off the public internet.

We have have general experience [tracking neuroimaging data with git-annex](./git-annex.md).

The data curation scripts should be placed inside the BIDS datasets, under the `code/` folder. See [BIDS specification](https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html#code). For more convenience, you can create a PR with a curation script that you are working on, so that others can give feedback; once the script is validated, you can simply close the PR and delete the branch without merging.

Every dataset should have a README inside it. Example:
~~~
# <NAME OF DATASET>

<PLEASE MODIFY>This is an MRI dataset acquired in the context of the XX project. It also contains manual segmentation of MS lesions from expert raters.

Dataset shared by: <NAME AND EMAIL>
<IF THERE WAS EMAIL COMM>Email communication: <DATE OF EMAIL AND SUBJECT>
<REPOSITORY OF PROJECT/MODEL, etc>Repository: https://github.com/ivadomed/model_seg_ms_mp2rage

<IF THERE ARE UPDATES IN THE DATASET:>2022-10-30: Added new data from INsIDER_SCT_Segmentations_COR

## dataset structure

participants.tsv: Include the following columns:
- 'pathology': can take values listed in https://docs.google.com/spreadsheets/d/1yjcA8Z0COn4OZxusIDHjStH2DpeXvscsj-aWE2X-_sg/edit#gid=0
- 'data_id' is the name center_study_subject used to locate the unprocessed data as under duke/mri/.
- 'institution_id' is used to identify CenterStudy.
- others? XXX (Jan pls continue)


XXX Jan contnue -- asju julien to check afterward



CONVENTION FOR JSON METADATA
----------------------------

UNDER SUBJECTS:
{
"Metadata": 
  {
  "added_by": "Name of the person who added this data in the database",
  "added_on": "YYYY-MM-DD",
  "contact": "URL to forum/issue AND/OR name AND/OR anything relevant to trace back the image",
  }
}

UNDER DERIVATIVES:
{
  "Author": [ "Firstname Lastname", "Firstname Lastname" ]
}


Spinal cord MRI data:
- DWI (A-P and P-A phase encoding)
- T1w sag
- T1w sag
- T1w sag
- T2star tra
Brain MRI data:
- DWI (A-P and P-A phase encoding)
- MPM (multi-parameter mapping)

## naming convention

sub-<site><pathology>XXX

example:
sub-zurichDCM001

Note: the label `bp-cspine` is used to differentiate spine images from brain.root@joplin:/mnt/extras
~~~

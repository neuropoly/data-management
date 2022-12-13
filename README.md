# Neuropoly Data Management

This repository deals with dataset usage and maintenance at [NeuroPoly Lab](https://www.neuro.polymtl.ca).

We run an [internal server](./internal-server.md) so private datasets can be kept off the public internet.

We have have general experience [tracking neuroimaging data with git-annex](./git-annex.md).

# ⚠️ Every dataset should have the following files 

```
├── README.md
├── participants.json
├── participants.tsv
├── dataset_description.json
└── code
    └── <script_you_used_for_dataset_curation>.py
```

For details, see [BIDS specification](https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html#code).

## `README.md`

The `README.md` is a [markdown](https://markdown-guide.readthedocs.io/en/latest/index.html) file describing the dataset in more detail.

<details><summary>README.md template:</summary>

```
# <NAME OF DATASET>

This is an MRI dataset acquired in the context of the <XYZ> project. 
It also contains manual segmentation of <MS lesions/tumors/etc> from <one/two/or more> expert raters. 
Segmentation are located under the derivatives folder.

## contact person

Dataset shared by: <NAME AND EMAIL>
<IF THERE WAS EMAIL COMM>Email communication: <DATE OF EMAIL AND SUBJECT>
<REPOSITORY OF PROJECT/MODEL, etc>Repository: https://github.com/<organization>/<repository_name>

<IF THERE ARE UPDATES IN THE DATASET:><YYYY>-<MM>-<DD>: Added new data from <centre ABC>

## dataset structure

Jan TODO

Spinal cord MRI data:
- DWI (A-P and P-A phase encoding)
- T1w sag
- T1w sag
- T1w sag
- T2star tra
Brain MRI data:
- DWI (A-P and P-A phase encoding)
- T1w

## naming convention

sub-<site><pathology>XXX

example:
sub-montrealDCM001

<ADDITIONAL NOTES IF AVAILABLE>Note: the label `bp-cspine` is used to differentiate spine images from brain.

## derivatives

The derivatives will be organized according to the following:

https://github.com/ivadomed/ivadomed/wiki/repositories#derivatives

Convention for derivatives JSON metadata:

{
  "Author": "Firstname Lastname",
  "Date": "YYYY-MM-DD HH:MM:SS"
}

<NOTE: "Date" is optional. We usually include it when running the manual correction via python scripts.>

## <IF DATA ARE MISSING FOR SOME SUBJECT(S)>missing data

```

</details>

## `dataset_description.json`

The `dataset_description.json` is a JSON file describing the dataset.

❗One `dataset_description.json` file (with `"DatasetType": "raw"`) must be included within the dataset itself, the second `dataset_description.json` file (with `"DatasetType": "derivative"`) must be included within the `derivatives`.

<details><summary>dataset_description.json template:</summary>

```json
{
    "BIDSVersion": "BIDS X.Y.Z",
    "Name": "<dataset_name>",
    "DatasetType": "raw/derivative"
}
```

</details>

## `participants.tsv`

The `participants.tsv` is a TSV file and should include the following columns:

| participant_id | pathology | data_id | institution_id | institution |
| ----------- | ----------- | ----------- | ----------- | ----------- |
| sub-001 | HC | 001 | 01 | montreal |

- `participant_id` - unique participant ID
- `pathology` - pathology name; can take values listed in the [pathology column](https://docs.google.com/spreadsheets/d/1yjcA8Z0COn4OZxusIDHjStH2DpeXvscsj-aWE2X-_sg/edit?usp=sharing)
- `data_id` -  subject ID used to locate the unprocessed data as under `duke/mri/`
- `institution_id` - institution ID used to locate the unprocessed data as under `duke/mri/`
- `institution` - human-friendly institution name
- others - if available, include also demographic characteristics such as `age`, `sex`, `height`, `weight`, `researcher`, and [additional columns](https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html#participants-file).

❗️Indicate missing values with `n/a` (for "not available"), not by empty cells!

## `participants.json`

The `participants.json` is a JSON file describing the column names in the `participants.tsv` and properties of their values.

<details><summary>participants.json template:</summary>

```json
{
    "participant_id": {
        "Description": "Unique Participant ID",
        "LongName": "Participant ID"
    },
    "pathology": {
        "Description": "Pathology",
        "LongName": "Pathology name"
    },
    "data_id": {
        "Description": "Subject ID as under duke/mri/",
        "LongName": "Subject ID"
    },
    "institution_id": {
        "Description": "Institution ID as under duke/mri/",
        "LongName": "Institution ID"
    },
    "institution": {
        "Description": "Institution ID after conversion to BIDS",
        "LongName": "BIDS Institution ID"
    }
}
```

</details>

## `code/`

The data curation script(s) should be placed inside the BIDS datasets, under the `code/` folder. For more convenience, you can create a PR with a curation script that you are working on, so that others can give feedback; once the script is validated, you can simply close the PR and delete the branch without merging.

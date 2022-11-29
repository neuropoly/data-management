# Neuropoly Data Management

This repository deals with dataset usage and maintenance at [NeuroPoly Lab](https://www.neuro.polymtl.ca).

We run an [internal server](./internal-server.md) so private datasets can be kept off the public internet.

We have have general experience [tracking neuroimaging data with git-annex](./git-annex.md).

The data curation scripts should be placed inside the BIDS datasets, under the `code/` folder. See [BIDS specification](https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html#code). For more convenience, you can create a PR with a curation script that you are working on, so that others can give feedback; once the script is validated, you can simply close the PR and delete the branch without merging.

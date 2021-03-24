# Using git-annex

[`git annex`](git-annex.branchable.com/) is an extension to git that lets it handle large repos spread in pieces across multiple servers/disks/accounts.

We are using it because

1. We have datasets we need to trace but they are too large for plain git to handle them well
1. It is compatible with [`datalad`](https://datalad.org) which gaining popularity in the neuroimaging community

## Installation



Everyone should do:

```
git config --global annex.thin true
git config --global
```



## Troubleshooting


### Resetting


`git-annex init` writes to a lot of places: the `git-annex` branch,
`.git/annex` (including several sqlite databases?), `.git`/config, 
and, sometimes, `.git/info/attributes`.

To get rid of it without getting rid of the 
complete repo, you can use

```
git annex uninit
```

To reset just the ID of the current copy, to make it appear like a fresh repo to `git annex whereis`:

```
git config --unset annex.uuid
#  then git annex init again? or what?
```


### `rm: cannot remove`

When trying to get rid of a git-annex dataset, you will run into, for example:

```
$ rm -rf data-single-subject/
[...]
rm: cannot remove 'data-single-subject/.git/annex/objects/mF/GV/SHA256E-s1082687--290a43b80da6f608e3d47107f3b6c05e98eebe56ed4eea633748c08bd1a7837a.nii.gz/SHA256E-s1082687--290a43b80da6f608e3d47107f3b6c05e98eebe56ed4eea633748c08bd1a7837a.nii.gz': Permission denied
rm: cannot remove 'data-single-subject/.git/annex/objects/Vq/vF/SHA256E-s15564390--7d3e45f0d4c67f31883b76eafc6cfdca1c1591590e2243dc8d443b07616b3609.nii.gz/SHA256E-s15564390--7d3e45f0d4c67f31883b76eafc6cfdca1c1591590e2243dc8d443b07616b3609.nii.gz': Permission denied
rm: cannot remove 'data-single-subject/.git/annex/objects/79/G6/SHA256E-s7183853--3262ac5d6c5f573720c5e508da47608bd9fa49d6cd4dd547f75046c1a2f0d5b6.nii.gz/SHA256E-s7183853--3262ac5d6c5f573720c5e508da47608bd9fa49d6cd4dd547f75046c1a2f0d5b6.nii.gz': Permission denied
```

This is because git-annex tries extra hard to make it hard to lose data, by marking its contents read-only. If you really intend to erase the dataset the invocation is:

```
$ chmod -R +w data-single-subject/.git/annex/
$ rm -rf data-single-subject/
```


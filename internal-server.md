
# Private datasets (git://data.neuro.polymtl.ca)

Much of our data is under medical ethics protections, and needs to be kept off the general internet. We have a custom server, locked down behind a VPN, with 1 terabyte of storage available. `git-annex` (and therefore `datalad`) can store and retrieve data from it.

URL: [git+ssh://data.neuro.polymtl.ca](git+ssh://data.neuro.polymtl.ca)

Table of Contents
-----------------

<!--ts-->
* [Initial setup](#initial-setup)
  * [Prerequisites](#prerequisites)
  * [Inscription](#inscription)
  * [Connection](#connection)
* [Usage](#usage)
  * [List](#list)
  * [Download](#download)
  * [Upload](#upload)
  * [Reviewing Pull Requests](#reviewing-pull-requests)
    * [Commit Rights](#commit-rights)
    * [Committing](#committing) 
  * [New repository](#new-repository)
  * [Permissions](#permissions)
  * [Renaming](#renaming)
  * [Deletion](#deletion)
  * [Add extra devices](#add-extra-devices)
* [Admin Guide](#admin-guide)
  * [Add users](#add-users)
  * [Permissions](#permissions-1)
  * [Renaming](#renaming-1)
  * [Deletion](#deletion-1)
  * [Backups](#backups)
  * [Troubleshooting](#troubleshooting)
  * [References](#references)


<!-- Added by: kousu, at: Tue 23 Mar 2021 11:54:23 PM EDT -->

<!--te-->

Initial setup
-------------

### Prerequisites

0. You must have a \*nix OS with `git-annex>=8` installed. See [`git-annex` installation](./git-annex.md#installation).
2. Make sure you have an ssh key.
    * If not, run `ssh-keygen -t ed25519 -C your.name@polymtl.ca`. Your keys will be in the hidden folder `~/.ssh/`.

### Inscription

Send your ssh public key -- that is, the contents of `~/.ssh/id_rsa.pub` or `~/.ssh/id_ed25519.pub` (the **.pub** file) -- to one of the server admins and ask them to create your account.

A **pubkey** should look like

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDE+b5vj+WvS5l6j56NF/leMpC2xT7JUCMUWDAqvWoVmNZ7UR3dGXQeTPTlmPmxPGD2Hk9/zFzxO2kYOt9o4lHQ0QQSKLUmTyuieyJE26wL1ZiLilmTgvgMxxkxvInF/Vr78V5Ll72zAmXzUxVSvuDGY2GRjnLreYheiqg1F3xTuD68uWInX8ZwA7NDtKpoZ7Aat063vD79WBrtiCfvAMbM8QhC3294zxqAjjy9fxs+TMTqAxtKdaWCA/eCs7sx9uvtFcj2Q9jxCMB3br5HyPLotgJMoIMt+fywj+vQG907LODRcqm9J0+ih+38/3Y6aqECMkHA9WWIfFywwjeA7EGr your.name@polymtl.ca
```

or

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJwsjlem+acuTOZGyNQKjyI7kJe9ULkhZo7N04QfC/tA your.name@polymtl.ca
```

Current **server admins** are:

* jcohen@polymtl.ca
* alexandru.foias@polymtl.ca
* nick.guenther@polymtl.ca

The admins should follow [Admin Guide > Add Users](#add-users) to create your account.

### Connection

Because this server contains private medical data, you need to be on campus, connected to the VPN, or working from a server on campus, like `joplin` or `rosenberg` to access it.

*If connecting from off-campus*, connect to [polyvpn](http://www.polymtl.ca/si/reseaux/acces-securise-rvp-ou-vpn).

> 🏚️ Verify connectivity by `ping data.neuro.polymtl.ca`. If **you cannot ping** then you need to double-check your VPN connection; make sure it is connected, make sure you can reach `joplin`, and if it still isn't working *ask the [Poly network admins](dge.informatique@polymtl.ca)* to unblock your account from this server.
 
Verify you can use the server by `ssh git@data.neuro.polymtl.ca help`. If it hangs, triple-check again your VPN. If it rejects you, your account is not created yet, or you have switched machines. A successful connection looks like:

```
$ ssh git@data.neuro.polymtl.ca help
Enter passphrase for key '/home/kousu/.ssh/id_ed25519.neuropoly': 
hello yourusername, this is git@data running gitolite3 3.6.11-2 (Debian) on git 2.27.0

list of remote commands available:

	D
	create
	desc
	git-annex-shell
	help
	info
	keys
	perms
	readme
	writable
```

Usage
-----

During daily usage, you will need to be [*on the polyvpn network*](#connection).

You should also make sure to [configure git annex](./git-annex.md#global-git-annex-config) for the best performance.

### List

To see what datasets you have available, use `info`, for example:

```
$ ssh git@data.neuro.polymtl.ca info
hello zamboni, this is git@data running gitolite3 3.6.11-2 (Debian) on git 2.27.0
 R W C  CREATOR/..*
 R W C  datasets/..*
 R W    datasets/data-single-subject
 R W    datasets/sct-testing-large
 R W    datasets/uk-biobank
```

You are identified to the server by your ssh keys, butNotice that this tells you the username you are known to 

### Download

To download an existing repository use `git clone`:

```
$ git clone git@data.neuro.polymtl.ca:datasets/data-single-subject
$ cd data-single-subject
$ git annex get .
```

### Upload

Despite not being hosted on Github, we are still using a [pull-request workflow](https://guides.github.com/introduction/flow/).
So, to make changes to a dataset, first ask its owner to [grant you upload rights](#permissions), then make a working branch for your changes:

```
$ git checkout -b working-branch
$ # edit your files, add new ones, etc
$ git add -p
$ git add path/to/new/file
$ git commit # and write a useful commit message
```

The *first* time before uploading, verify you have access with `info`. You need "W" (for "Write") permission, like this:

```
$ ssh git@localhost info datasets/uk-biobank
hello zamboni, this is git@data running gitolite3 3.6.11-2 (Debian) on git 2.27.0

 R W    datasets/uk-biobank
```

Once you have access you can:

```
$ git annex copy --to origin
$ git push
```

Finally, ask one of that dataset's reviewers to [look at your pull request](#Reviewing-Pull-Requests).


### Reviewing Pull Requests

If someone asks you to review their changes on branch `xy/branchname`:

```
git checkout xy/branchname
git annex get .
```

Then look at the branch to see if it looks right to you.

To investigate what changed:

```
git log --stat master..HEAD # to see filenames
git log -p master..HEAD     # to see content, commit-by-commit
git diff master..HEAD       # to see content, overall
```

Also, it's a good idea to run:

```
git annex whereis
```

To check that all the annexed files have been uploaded.


> 🏚️ `git-annex` is not well-suited to a pull-request flow. It is mostly designed for a single person to share data among many computers, not for multiple people to share data between a few computers. We can make it work but it needs some patience. Have a cat to make it better: 🐈🌺


#### Commit Rights


Each repo has its own [`OWNERS` group](#permissions) attached. These are the people allowed to commit to `master`, and usually they should be the [reviewers](#reviewing-pull-requests) as well.

In order to join this group, someone already in it needs to grant you access:

```
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo + OWNERS yourname
```

You can check if you have commit rights to a dataset "my-new-repo" by seeing if you appear in the group:

```
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo -l | grep OWNERS
```

#### Committing

Once a branch is finalized:

```
git checkout master
git merge --ff-only xy/branchname # or use git pull --squash xy/branchname
git push  # no need for git-annex sync here, no annex files have been moved
```

(Optional) Clean up the branch:

```
git branch -d xy/branchname
git branch -d synced/xy/branchname   # redundancy
git push origin :xy/branchname
git push origin :synced/xy/branchname
```


### New repository

To make a new repo, follow this [recipe](./git-annex.md#new-repo).

Then, to upload it, pick a name under `datasets/`, e.g. "my-new-repo", and do

```
$ git remote add origin git@data.neuro.polymtl.ca:datasets/my-new-repo
$ git annex sync --content origin
$ # verify your .nii.gz files were annexed and uploaded
$ git annex whereis
```

Note that you have personal space under "CREATOR", so if your username is "zamboni" then you can:

```
$ git remote add origin git@data.neuro.polymtl.ca:zamboni/project1
$ git push origin
```

### Permissions

You can grant others permissions to your repositories with `perms`.

```
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo + WRITERS someone # grant someone upload rights
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo - WRITERS someone # revoke someone's upload rights
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo + OWNERS researcher2 # grant someone rights to add (and remove) others and to merge to master
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo -l # view users
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo -lr # view access rules
```

Use

```
ssh git@data.neuro.polymtl.ca perms -h
```

and see https://gitolite.com/gitolite/user#setget-additional-permissions-for-repos-you-created for full details.


### Renaming

There is no way for a user to rename a repo directly ([bug report](https://github.com/neuropoly/data-management/issues/83)).
You can [ask an admin to do it](#renaming-1).

### Deletion

If you created or own a repo and decide it is no longer necessary:

```
ssh git@data.neuro.polymtl.ca D trash repo
```

The "trash" is cleaned out after a week. *Except it's not, yet: https://github.com/neuropoly/data-management/issues/54*


### Add extra devices

Like with Github, you can authorize any number of secondary devices.

For example, to authorize yourself from `server2`, log in to `server2` and make an ssh key if one doesn't exist (`ssh-keygen`), copy it (`~/.ssh/id_rsa.pub`) to a device that is already authenticated (e.g. as `~/id_rsa.server2.pub`), then authorize yourself by:

```
cat ~/id_rsa-server2.pub | ssh git@data.neuro.polymtl.ca keys add @server2
```

Test it by running, from `server2`

```
ssh git@data.neuro.polymtl.ca info
```

Admin Guide
-----------

We are using [`Gitolite`](https://gitolite.com/) with [`git-annex`](https://git-annex.branchable.com/) as our dataset server.
It is compatible with [`datalad`](https://www.datalad.org/) but to reduce the fragility we only support the basics.

Datasets are stored as git repositories on the server, with the bulk of their data *also* stored on the server in each repo's "annex" folder. Using `git-annex` enables data on-demand -- in our default configuration, only the data needed for the active branch is actually downloaded by a user, and it is also possible for the user to choose specific folders to focus on. Datasets are `git-annex` [ssh remotes](https://git-annex.branchable.com/walkthrough/#index11h2).

`gitolite` manages users and their permissions. Each user has a namespace to themselves where they can make repos named `data.neuro.polymtl.ca:$user/$repo.git` (like Github), and there is also a shared space `data.neuro.polymtl.ca:datasets/*` intended for lab-wide datasets.

### Add users

To grant access to a lab member, [as above](#add-extra-devices), ask the lab member to generate an ssh key using `ssh-keygen` and have them send you the *public key*. Save it to a file `id_rsa.zamboni.pub` and add them with

```
cat id_rsa.zamboni.pub | ssh git@data.neuro.polymtl.ca keys add zamboni
```

You can also paste the key in, followed by `ctrl-d`; this looks like:

```
$ ssh git@data.neuro.polymtl.ca keys add zamboni
Enter passphrase for key '/home/kousu/.ssh/id_rsa.github': 
please supply the new key on STDIN (e.g. cat you.pub | ssh gitolite@git.example.com keys add @laptop).
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID11N3hQpJP4Okivd5xO3N0CuO24ioMwXYv+l/1PM/+z zamboni@laptop
Added SHA256:hwil2tmaw/prgIBX5odO8vOAj2i38gPrUGjGZnnkVvo : zamboni.pub
```

You **should** use the person's @polymtl.ca email address as their username. However [there is a bug](https://github.com/kousu/gitolite-mods/issues/3), so just use "firstname.lastname". Once someone is inscribed they can add and remove their own keys without having to know their username. We will migrate all the usernames when that bug is fixed; it won't affect much, since these usernames are entirely server-side. The only time users see them is when they run `info` or use `perms`.


### Permissions

As admin, you can add or revoke any permissions to any repo [using `perms`](#permissions).

There is unfortunately no way to view permissions *as another user* so you will need to rely on people sending you screenshots if they are having problems
but you can at least inspect the active sets of permissions on a repo with

```
ssh git@data.neuro.polymtl.ca perms <repo> -l
```

If you need to add new namespaces or finer grained permissions, first, reconsider if the extra complexity and the _risk of locking yourself out_ is worth it. Everything you should need to manage the lab should be doable via `ssh git@data.neuro.polymtl.ca help`. If you are sure, then review [gitolite's permissions model](https://gitolite.com/gitolite/conf.html) and [official docs for this use case](https://gitolite.com/gitolite/fool_proof_setup.html#administration-tasks), then:

```
git clone git@data.neuro.polymtl.ca:gitolite-admin
cd gitolite-admin
vi conf/gitolite.conf  # optional: investigate/change the repo definitions
ls -R keydir/          # optional: investigate/change who has access; this *should* be unnecessary, use `keys` as above instead.
git add -u . && git push
```

### Renaming

As an admin, you can rename a repo by connecting to the server directly:

```
ssh root@data.neuro.polymtl.ca
sudo -u git -i
cd repositories/datasets/
mv $dataset.git $new_name.git
```

### Deletion

You can also delete any repo [using `D`](#deletion).

You can also get rid of a dataset immediately by:

```
ssh git@data.neuro.polymtl.ca D unlock datasets/<dataset>
ssh git@data.neuro.polymtl.ca D rm datasets/<dataset>
```

### Backups

Backups are automatically made to MIC-UNF's servers.

*except they're not, yet: https://github.com/neuropoly/data-management/issues/20*

You can access these if you need to recover by:

```
TODO
```


### Troubleshooting

If the server is doing something strange, contact someone with sysadmin-access to the server (what luck: as of 2021-03 at least, *the admins and the sysadmins are the same set: Julien, Alex and Nick*).

These people can investigate by following the gitolote guide in the [sysadmin docs](https://github.com/neuropoly/management/blob/master/docs/gitolite.md).

### References

* Patel, Hiren - [Wildrepos in Gitolite](https://caesr.uwaterloo.ca/wildrepos-in-gitolite/) -- detailing how a research lab manages their code and publications collaboratively through `gitolite`

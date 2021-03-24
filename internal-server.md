
# Private datasets (git://data.neuro.polymtl.ca)

Much of our data is under medical ethics protections, and needs to be kept off the general internet. We have a custom server, locked down behind a VPN, with 1 terabyte of storage available. `git-annex` (and therefore `datalad`) can store and retrieve data from it.

URL: git+ssh://data.neuro.polymtl.ca

<!--ts-->
* [Initial setup](#initial-setup)
* [Usage](#usage)
  * [List](#list)
  * [Download](#download)
  * [Upload](#upload)
  * [Add secondary devices](#add-secondary-devices)
  * [New repository](#new-repository)
  * [Permissions](#permissions)
  * [Submodules:](#submodules)
  * [Reviewing Pull Requests](#reviewing-pull-requests)
* [Troubleshooting](#troubleshooting)
  * [rm: cannot remove](#rm-cannot-remove)
* [Admin Guide](#admin-guide)
* [Add users](#add-users)
  * [Manage Repos](#manage-repos)
* [Sysadmin Guide](#sysadmin-guide)
  * [Infrastructure](#infrastructure)
  * [Notifications](#notifications)
  * [Monitoring](#monitoring)
  * [Gitolite](#gitolite)
  * [Backups](#backups)
  * [dataset repo configuration](#dataset-repo-configuration)

<!-- Added by: kousu, at: Tue 23 Mar 2021 11:54:23 PM EDT -->

<!--te-->

Initial setup
-------------

**Prerequisites**

0. You must have a unix OS. `git-annex` is simply not compatible with anything else.
    * _Linux_
    * _BSD_
    * _macOS_
    * if *Windows*, either
	* use [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
        * install a Linux virtual machine using e.g. [VirtualBox](https://virtualbox.org/)
1. Make sure you have `git` and `git-annex>=8` installed.
    Make sure `git-annex version` reports version 8 or higher!
    * **Linux**
        * **Arch**: `pacman -Sy git-annex`
        * **Fedora/RedHat/CentOS**: `dnf install git-annex`
        * **Debian/Ubuntu**: `apt-get install git-annex`, but **you must be using Ubuntu 20.04** or **Debian Testing** or higher.
        * if on an older system and can't upgrade, you can try [installing `conda`](https://docs.conda.io/en/latest/miniconda.html) and then `conda install git-annex`.
    * **BSD**:
        * OpenBSD: _untested_
        * FreeBSD: _untested_
        * NetBSD: _untested_
    * **macOS**: `brew install git-annex`

2. Make sure you have an ssh key.
    * If not, run `ssh-keygen`. Your keys will be in the hidden folder `~/.ssh/`.

3. Give your ssh public key -- that is, the contents of `~/.ssh/id_rsa.pub` or `~/.ssh/id_ed25519.pub`, making sure to use the **.pub** file -- to one of the server admins and ask for their consent to granting you access.
    * A pubkey should look like
      ```
      ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDE+b5vj+WvS5l6j56NF/leMpC2xT7JUCMUWDAqvWoVmNZ7UR3dGXQeTPTlmPmxPGD2Hk9/zFzxO2kYOt9o4lHQ0QQSKLUmTyuieyJE26wL1ZiLilmTgvgMxxkxvInF/Vr78V5Ll72zAmXzUxVSvuDGY2GRjnLreYheiqg1F3xTuD68uWInX8ZwA7NDtKpoZ7Aat063vD79WBrtiCfvAMbM8QhC3294zxqAjjy9fxs+TMTqAxtKdaWCA/eCs7sx9uvtFcj2Q9jxCMB3br5HyPLotgJMoIMt+fywj+vQG907LODRcqm9J0+ih+38/3Y6aqECMkHA9WWIfFywwjeA7EGr user@laptop
      ```
      or
      ```
      ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJwsjlem+acuTOZGyNQKjyI7kJe9ULkhZo7N04QfC/tA user@laptop
      ```
    * Current server admins are:
        * jcohen@polymtl.ca
        * alexandru.foias@polymtl.ca
        * nick.guenther@polymtl.ca
	* These people have their personal ssh keys in `~root/.ssh/authorized_keys` (i.e. they can `ssh root@data.neuro.polymtl.ca`); they also have the _shared_ root password in their password managers, which should never be needed but for low-level rescue maintenance on the system.

  The admin will then add the key as follows:
  ```
  ssh git@data.neuro.polymtl.ca keys add @STATION
  ```
  Example: STATION could be "joplin"
  when prompted, enter the entire passkey, exemple:
  ```
  ssh-rsa AAABS663728....XXXSIH p101317@joplin
  ```
  Then, press CTRL+D
  You should see the message:
  ```
  Added SHA256:En0CCSS...DoMzc : USERNAME@joplin.pub
  ```

4. *If connecting from off-campus*, connect to [polyvpn](http://www.polymtl.ca/si/reseaux/acces-securise-rvp-ou-vpn).
    * Verify connectivity by `ping data.neuro.polymtl.ca`. If **you cannot** then you need to double-check your VPN connection; make sure it is connected, and *ask the Poly network admins* if you are firewalled from this server.
5. Verify you have access to the server by `ssh git@data.neuro.polymtl.ca help`. If it hangs, triple-check your VPN. If it rejects you, ask if others are having the same problem. A successful connection looks like:

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
$ # TODO: git config annex.thin=true ?
$ git annex init
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
$ git annex sync --content
```

Finally, ask one of that dataset's reviewers to [look at your pull request](#Reviewing-Pull-Requests).


### Add secondary devices

Like with Github, you can authorize any number of secondary devices.

For example, to authorize yourself from `server2`, log in to `server2` and make an ssh key if one doesn't exist (`ssh-keygen`), copy it (`~/.ssh/id_rsa.pub`) to a device that is already authenticated (e.g. as `~/id_rsa.server2.pub`), then authorize yourself by:

```
cat ~/id_rsa-server2.pub | ssh git@data.neuro.polymtl.ca keys add @server2
```

Test it by running, from `server2`

```
ssh git@data.neuro.polymtl.ca info
```


### New repository

To make a new repo:

```
$ mkdir my-new-repo
$ cd my-new-repo
$ git init
$ touch README # and hopefully write something useful in this too
$ git add README; git commit -m "Initial commit"
$ (echo "*   annex.largefiles=anything"; echo "*.nii.gz   filter=annex"; echo "*.nii   filter=annex") > .gitattributes
$ git add .gitattributes; git commit -m "Configure git-annex"
$ git annex init
$ git annex dead here # make sure *this* copy isn't shared to others; the repo should be shared via the server
$ # copy in or create initial files
$ git add .
$ # verify your .nii.gz files were annexed
$ git annex whereis
$ git commit
```

To upload a new repository, pick a name that follows one of the patterns you have "C" (for "Create") permission on and do:

```
$ git remote add origin git@data.neuro.polymtl.ca:datasets/my-new-repo
$ git push origin # ??
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
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo + OWNERS researcher2 # grant someone rights to add (and remove) others
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo -l # view users
ssh git@data.neuro.polymtl.ca perms datasets/my-new-repo -lr # view access rules
```

Use

```
ssh git@data.neuro.polymtl.ca perms -h
```

and see https://gitolite.com/gitolite/user#setget-additional-permissions-for-repos-you-created for full details.


### Submodules:
(Ref: the datalad handbook)

### Reviewing Pull Requests

If someone asks you to review their changes on branch `xy/branchname`:

```
git annex sync --content
git checkout xy/branchname
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


**NB** `git-annex` is not well-suited to a pull-request flow. It is mostly designed for a single person to share data among many computers, not for multiple people to share data between a few computers. We can make it work but it needs some care.


If you approve and want to commit:

```
git checkout master
git merge --ff-only xy/branchname # or use git pull --squash xy/branchname
git push
```

(Optional) Clean up the branch:

```
git branch -d xy/branchname
git branch -d synced/xy/branchname   # redundancy
git push origin :xy/branchname
git push origin :synced/xy/branchname
```

## Troubleshooting

### `rm: cannot remove`

When trying to get rid of a git-annex dataset, you will run into, for example:

```
$ rm -rf data-single-subject/
[...]
rm: cannot remove 'data-single-subject/.git/annex/objects/mF/GV/SHA256E-s1082687--290a43b80da6f608e3d47107f3b6c05e98eebe56ed4eea633748c08bd1a7837a.nii.gz/SHA256E-s1082687--290a43b80da6f608e3d47107f3b6c05e98eebe56ed4eea633748c08bd1a7837a.nii.gz': Permission denied
rm: cannot remove 'data-single-subject/.git/annex/objects/Vq/vF/SHA256E-s15564390--7d3e45f0d4c67f31883b76eafc6cfdca1c1591590e2243dc8d443b07616b3609.nii.gz/SHA256E-s15564390--7d3e45f0d4c67f31883b76eafc6cfdca1c1591590e2243dc8d443b07616b3609.nii.gz': Permission denied
rm: cannot remove 'data-single-subject/.git/annex/objects/79/G6/SHA256E-s7183853--3262ac5d6c5f573720c5e508da47608bd9fa49d6cd4dd547f75046c1a2f0d5b6.nii.gz/SHA256E-s7183853--3262ac5d6c5f573720c5e508da47608bd9fa49d6cd4dd547f75046c1a2f0d5b6.nii.gz': Permission denied
```

This is because git-annex tries extra hard to make it hard to lose data, by marking its contents read-only. If you really intend to erase a dataset then:

```
$ chmod -R +w data-single-subject/.git/annex/
$ rm -rf data-single-subject/
``````

Admin Guide
-----------

We are using [`Gitolite`](https://gitolite.com/) with [`git-annex`](https://git-annex.branchable.com/) as our dataset server.
It is compatible with [`datalad`](https://www.datalad.org/) but to reduce the fragility we only support the basics.

Datasets are stored as git repositories on the server, with the bulk of their data *also* stored on the server in each repo's "annex" folder. Using `git-annex` enables data on-demand -- in our default configuration, only the data needed for the active branch is actually downloaded by a user, and it is also possible for the user to choose specific folders to focus on. Datasets are `git-annex` [ssh remotes](https://git-annex.branchable.com/walkthrough/#index11h2).

`gitolite` manages users and their permissions. Each user has a namespace to themselves where they can make repos named `data.neuro.polymtl.ca:$user/$repo.git` (like Github), and there is also a shared space `data.neuro.polymtl.ca:datasets/*` intended for lab-wide datasets.

## Add users

To grant access to a lab member, [as above](#add-secondary-devices), ask the lab member to generate an ssh key using `ssh-keygen` and have them send you the *public key*. Save it to a file `id_rsa.zamboni.pub` and add them with

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

### Manage Repos

As admin, you can also delete user's repos (using `D`), revoke or add permissions to their repos (using `perms`)
[TODO]

If you need to add new namespaces or finer grained permissions, first, reconsider if the extra complexity and the _risk of locking yourself out_ is worth it. Everything you should need to manage the lab should be doable via `ssh git@data.neuro.polymtl.ca help`. If you are sure, then review [gitolite's permissions model](https://gitolite.com/gitolite/conf.html) and [official docs for this use case](https://gitolite.com/gitolite/fool_proof_setup.html#administration-tasks), then:

```
git clone git@data.neuro.polymtl.ca:gitolite-admin
cd gitolite-admin
vi conf/gitolite.conf  # optional: investigate/change the repo definitions
ls -R keydir/          # optional: investigate/change who has access; this *should* be unnecessary, use `keys` as above instead.
git add -u . && git push
```

Further reading:

* Patel, Hiren - [Wildrepos in Gitolite](https://caesr.uwaterloo.ca/wildrepos-in-gitolite/) -- detailing how a research lab manages their code and publications collaboratively through `gitolite`



Sysadmin Guide
--------------

In case something goes wrong, here are some notes about getting underneath gitolite to fix things up.


### Infrastructure

`data.neuro.polymtl.ca` should have IP address `132.207.65.204`. It is a virtual machine running on polymtl.ca's on-premises Xen cluster. dge.informatique@polymtl.ca manages this cluster, including its backups, and can help you out in an emergency.


### Notifications

You should consider adding your email to `~root/.forward` so that you receive OS notifications from the system:

```
sudo sh -c 'echo your.email@example.com >> ~root/.forward'
```



### Monitoring

We're running [netdata](https://netdata.cloud) which provides useful charts and history. Netdata [does not have built in authentication](https://github.com/netdata/netdata/issues/70#issuecomment-220866829), and there are many firewalls at Polytechnique anyway, so the best way to access it is:

1. Log in
```
ssh -L 19999:localhost:19999 data.neuro.polymtl.ca
```
2. Visit https://localhost:19999

Netdata is currently configured to keep 1 week of history.

Netdata will send an email to `root@` if something is amiss; this is why it is a good idea to get yourself in `~root/.forward`.

### Gitolite

gitolite is the main application on this server.

gitolite keeps its configuration in two places: the baseline system in `~git/.gitolite.rc`, and repo definitions and permissions in the repository. Gitolite considers a "gitolite admin" to be anyone with write access to, so to nominate new admins you need to edit.

To edit

If 

To investigate the state of the git server, ssh in (as or sudo'ing to root) and run

```
root@data:~# sudo -u git -i bash
```

Which will let you look around at the underlying state. The actual repositories are in `~git/repositories`; this folder is a 1TB virtual disk. Again, the primary config is `~git/.gitolite.rc`, and the site config is in a git repo in

Normally, gitolite builds its deployment out of its `gitolite-admin` repo on changes, but if working on the same server you need to use `gitolite push` instead of `git push` because, as far as I can tell, the receive hook has a bug. That is, to manage the deployment, what you should do is:

```
cd $(mktemp -d); # optional: keep changes isolated
git clone ~git/repositories/gitolite-admin
cd gitolite-admin
vi conf/gitolite.conf  # optional: investigate/change the repo definitions
ls -R keydir/          # optional: investigate/change who has access; this *should* be unnecessary, use `keys` as above instead.
git add -u && gitolite push  # this is the difference
```

[`keys`](https://github.com/kousu/gitolite-mods/blob/master/keys) is a combination and simplification of [`sskm`](https://gitolite.com/gitolite/contrib/sskm.html) and [`ukm`](https://gitolite.com/gitolite/contrib/ukm.html), written by nick.guenther@polymtl.ca.


References

* [gitolite: help for emergencies](https://gitolite.com/gitolite/emergencies.html)



### Backups

We have no backup plan in place yet. For now, just make sure to take a complete.

Not totally true! We're backing up to `sftp://neuropoly-backup@elm.criugm.qc.ca`. watch this space.






### dataset repo configuration

`git-annex` has a lot of options, many of which are already considered legacy; datalad has even more, which is part of why we are ignoring it. For optimal data management, it is important that these options are configured in each repo:


```
```

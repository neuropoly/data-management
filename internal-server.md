
# Accessing and managing your private datasets on git://data.neuro.polymtl.ca.


Initial setup
-------------

**Prerequisites**

**TEMPORARY PREREQUISITE**: I'm waiting on IT to set up DNS for the server; in the meantime:
```
(echo Host data.neuro.polymtl.ca; echo HostName 132.207.65.204) >> ~/.ssh/config
```

0. You must have a unix OS. `git-annex` is simply not compatible with anything else:
    * _Linux_
    * _BSD_
    * _macOS_
    * if you have Windows you can either
	* use [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
        * install a Linux virtual machine using e.g. [VirtualBox](https://virtualbox.org/)
1. Make sure you have `git` and `git-annex>=8` installed.
    Make sure `git-annex version` reports version 8 or higher!
    * **Linux**
        * **Arch**: `pacman -Sy git-annex`
        * **Fedora/RedHat/CentOS**: `dnf install git-annex`
        * **Debian/Ubuntu**: `apt-get install git-annex`, but **you must be using Ubuntu 20.10** or **Debian Testing**
        * if you are on an older system and can't upgrade, you can try [installing `conda`](https://docs.conda.io/en/latest/miniconda.html) and then `conda install git-annex`.
    * **BSD**:
        * OpenBSD: _untested_
        * FreeBSD: _untested_
        * NetBSD: _untested_
    * **macOS**: `brew install git-annex`
2. Make sure you have an ssh key.
    * If not, run `ssh-keygen`. Your keys will be in the hidden folder `~/.ssh/`.
4. Give your ssh public key -- that is, the contents of `~/.ssh/id_rsa.pub` or `~/.ssh/id_ed25519.pub`, making sure to use the **.pub** file -- to one of the server admins and ask for their consent to granting you access.
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
1. *If connecting from off-campus*, connect to [polyvpn](http://www.polymtl.ca/si/reseaux/acces-securise-rvp-ou-vpn).
    * Verify connectivity by `ping data.neuro.polymtl.ca`. If **you cannot** then you need to double-check your VPN connection; make sure it is connected, and *ask the Poly network admins* if you are firewalled from this server.
3. Verify you have access to the server by `ssh git@data.neuro.polymtl.ca help`. Again, if it hangs, triple-check your VPN. A successful connection looks like:

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

Using data:

TODO

Submodules:
(Ref: the datalad handbook)

Uploading data:

TODO


```
ssh git@data.neuro.polymtl.ca
```

Admin Guide
-----------

We are using [`Gitolite`](https://gitolite.com/) with [`git-annex`](https://git-annex.branchable.com/) as our dataset server.
It is compatible with [`datalad`](https://www.datalad.org/) but to reduce the fragility we only support the basics.

Datasets are stored as git repositories on the server, with the bulk of their data *also* stored on the server in each repo's "annex" folder. Using `git-annex` enables data on-demand -- in our default configuration, only the data needed for the active branch is actually downloaded by a user, and it is also possible for the user to choose specific folders to focus on. Datasets are `git-annex` [ssh remotes](https://git-annex.branchable.com/walkthrough/#index11h2).

`gitolite` manages users and their permissions. Each user has a namespace to themselves where they can make repos named `data.neuro.polymtl.ca:$user/$repo.git` (like Github), and there is also a shared space `data.neuro.polymtl.ca:datasets/*` intended for lab-wide datasets.


To grant access to a lab member:

```
```

As admin, you can also delete user's repos (using `D`), revoke or add permissions to their repos (using `perms`)


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

`data.neuro.polymtl.ca` should have IP address `132.207.65.204`. It is a virtual machine running on polymtl.ca's on-premises Xen cluster. dge.informatique@polymtl.ca manages this cluster, including its backups, and can help you out in an emergency.

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



[`netdata`](https://www.netdata.cloud/) is installed on the server: it provides useful logs of what the system is up to, for tracing crashes and performance problems; it's configured with 1 week of logs. But it is installed with lazy access control: in order to access it, you need to first authenticate via ssh by doing:

```
ssh -L 19999:localhost:19999 data.neuro.polymtl.ca
```

Then visit https://localhost:19999.


References

* [gitolite: help for emergencies](https://gitolite.com/gitolite/emergencies.html)



### Backups

We have no backup plan in place yet. For now, just make sure to take a complete.





### dataset repo configuration

`git-annex` has a lot of options, many of which are already considered legacy; datalad has even more, which is part of why we are ignoring it. For optimal data management, it is important that these options are configured in each repo:


```
```

---
title: "A tiny script to explore package sizes in Anaconda"
date: 2023-04-26T00:00:00+02:00
tags: ["anaconda", "shell"]
categories: ["bash"]
draft: false
---

# A tiny script to explore package sizes in Anaconda

Today at work, I was trying to reduce the size of a container image and I wanted to check what's in
some conda environments, especially what packages are taking up all that sweet storage (looking at
you Tensorflow).

I thought, surely `conda` has a way to show me the packages and their sizes in general and not just
when I install them? But it seems that it doesn't, so I hacked together something silly with the
help of the _coreutils_ and awk.

See below my `conda-size-report.sh`,

```sh
env=$1

# Select the conda environment path matching the name passed as argument
path=$(conda env list | awk -v env="$env" '$1==env {print $2}')

if [[ -d $path ]]
then
    # Do not follow symlinks, indicated by 'l' at the beginning of the line
    pythons=$(ls -ld $path/lib/python* | grep -v ^l | awk '{print $NF}')
    for p in $pythons
    do
	echo $p | awk -F/ '{printf "Python version: %s\n",$NF}'
	# cd to python version and print sizes -> sort by human-readable size -> print size and pkg name and add total size
	(cd $p && du -ch --max-depth=1 $p/site-packages | sort -hk1 --unique | awk -F/ '{print $1, $NF}' | sed -e 's/site-packages/+Total+/')
    done
else
    echo "No conda environment: $env"
fi
```

So right now, with an environment called `my_env` for example, I can simply do:

```sh
sh conda-size-report.sh my_env
```

and have something simple like this:

```text
Python version: python3.8
770K    gunicorn
.
.
34M     numpy
71M     pandas
535M    tensorflow
1203M   +Total+
```

And that's it, you can enjoy your time again, one hacky script at a time.

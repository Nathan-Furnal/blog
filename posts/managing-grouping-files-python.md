---
title: "Managing and grouping files with Python"
date: 2022-06-06T00:00:00+02:00
categories: ["python"]
draft: false
---

# Managing and grouping files with Python

## Introduction {#introduction}

We are sometimes faced with systems which generate lots of files that we have to
deal with, be it for triage or later reading; it could be logs, data dumps,
automatically generated reports and so on. In many cases, we don't have a say in
the how and why of the files' organization and might want to deal with them
automatically, later on. Which is what I'd like to tackle here, using Python
standard library. This is very much an "automate the boring stuff" article where
I'll show a handful of functions that make dealing with files easier.

The bread and butter of the following sections will be the [`pathlib`](https://docs.python.org/3/library/pathlib.html) module
which provides a lot of cross-platform functionalities to work with paths and
files. I'll also use the [`itertools`](https://docs.python.org/3/library/itertools.html) module which is worth getting familiar
with.

To goal of this post is to provide functionalities that will allow turning a
directory such as this one (sub-directories management possible as well):

```text
AREA44_LOG1.txt
AREA51_LOG2.txt
info.md
AREZ51_LOG3.txt -> mistake here!
AREA23_LOG1.txt
AREA51_LOG1.txt
junk.json
AREA00_LOG1.txt
Makefile.mk
AREA23_LOG2.txt
```

Into the result here:

```text
output-dir/
├── AREA00
│   └── AREA00_LOG1.txt
├── AREA23
│   ├── AREA23_LOG1.txt
│   └── AREA23_LOG2.txt
├── AREA44
│   └── AREA44_LOG1.txt
└── AREA51
    ├── AREA51_LOG1.txt
    └── AREA51_LOG2.txt
```


## Filtering files on extensions {#filtering-files-on-extensions}

A simple, useful operation is filtering on file extensions, such as extracting
all the text files from a directory or all the images files from a directory and
its sub-directories.

Python's `Path` objects allow [globbing](https://en.wikipedia.org/wiki/Glob_(programming)) at 3 different levels: inside the
directory, inside the directory and its direct children, inside the directory
and all its recursive children.

See for example, the following structure:

```text
test-dir/
├── other-subdir
│   ├── deeper-dir
│   │   └── deeper-file.txt
│   ├── subfile.py
│   └── subfile.txt
├── random.txt
├── stuff.py
└── subdir
    ├── subdir.log
    ├── subdir.mk
    └── subdir.txt
```

We can grab its files like this:

```python
from pathlib import Path

directory = Path("test-dir")

# First level, inside the dir only
level_1 = list(directory.glob("*.txt"))

# Second level, the dir and the direct children
level_2 = list(directory.glob("*/*.txt"))

# Recursive level, the dir and all its children
level_recur = list(directory.glob("**/*.txt"))

print(level_1, "\n")
print(level_2, "\n")
print(level_recur, "\n")
```

```text
[PosixPath('test-dir/random.txt')]

[PosixPath('test-dir/other-subdir/subfile.txt'),
 PosixPath('test-dir/subdir/subdir.txt')]

[PosixPath('test-dir/random.txt'), PosixPath('test-dir/other-subdir/subfile.txt'),
 PosixPath('test-dir/other-subdir/deeper-dir/deeper-file.txt'),
 PosixPath('test-dir/subdir/subdir.txt')]
```

There are a couple of things of note here. Firstly, I'm running this file inside
the top directory and using a relative path (namely, `test-dir`). I could also
use an absolute path, `pathlib` lets us pick how paths are declared and can also
extract the absolute path from a relative one using the `absolute()`
method. Secondly, I had to wrap the glob results in a `list` because the output is
a [generator](https://docs.python.org/3/glossary.html#term-generator) object. Thirdly, the output is a list of _PosixPath_ because I'm on
a Linux machine, on other operating systems, you might see something different.

Now this is all well and good but somewhat limited, because we can only glob a
single file extension at a time. We can easily fix this by creating a list of
valid extensions.

Let's try to get all the Python files and text files inside a directory and its
sub-directories, we'll use a [generator comprehension](https://peps.python.org/pep-0289/) and [f-strings](https://docs.python.org/3/tutorial/inputoutput.html).

The following won't have the desired output because it creates a list of
generators instead of a list of files. I could iterate over the list and create
a list of list but I'd like a flat output instead. This is where `itertools`
comes to the rescue.

```python
from pathlib import Path
from itertools import chain
directory = Path("test-dir")
extensions = ["py", "txt"]

# List of generators, bad output
py_and_text_files = list(directory.glob(f"**/*.{ext}") for ext in extensions)

# List of files from flattened generators, good output
# Per the docs: chain.from_iterable(['ABC', 'DEF']) --> A B C D E F
py_and_text_files = list(
    chain.from_iterable(directory.glob(f"**/*.{ext}") for ext in extensions)
)

print(py_and_text_files)
```

```text
[PosixPath('test-dir/stuff.py'),
 PosixPath('test-dir/other-subdir/subfile.py'),
 PosixPath('test-dir/random.txt'),
 PosixPath('test-dir/other-subdir/subfile.txt'),
 PosixPath('test-dir/other-subdir/deeper-dir/deeper-file.txt'),
 PosixPath('test-dir/subdir/subdir.txt')]
```

Armed with enough knowledge, let's write a helper function that will filter a
directory given some extensions and a recursion level. I've added a couple
checks that I thought were useful. That is, converting string paths to `Path`
objects, handling one extension vs. a list of extensions and finally, handling
how deep the globbing goes.

```python
from pathlib import Path
from itertools import chain

def filter_extensions(directory, extensions, level = 0):
    lvl_map = {0: ".", 1: "*", 2: "**"}
    if isinstance(directory, str):
        directory = Path(directory)
    if isinstance(extensions, str):
        return directory.glob(f"{lvl_map[level]}/*.{extensions}")

    return chain.from_iterable(
        directory.glob(f"{lvl_map[level]}/*.{e}") for e in extensions
    )

# Getting all Python and text files from all levels
list(filter_extensions(Path("test-dir"), ["py", "txt"], 2))
```

```text
[PosixPath('test-dir/stuff.py'),
 PosixPath('test-dir/other-subdir/subfile.py'),
 PosixPath('test-dir/random.txt'),
 PosixPath('test-dir/other-subdir/subfile.txt'),
 PosixPath('test-dir/other-subdir/deeper-dir/deeper-file.txt'),
 PosixPath('test-dir/subdir/subdir.txt')]
```

We've got the first step down! Now we can work onto the next, which is grouping
files.


## Grouping files {#grouping-files}

After filtering the files to get only the relevant extensions, we'll manipulate
them a bit more. I'll show you how to group files by arbitrary conditions using
a function.

A common solution to capture patterns in (file) names is to use [regular
expressions](https://en.wikipedia.org/wiki/Regular_expression), they have their place when you know in advance what you're
matching but it's not always the case. For example, log files for some actions
starting with `LOG_X_...` where `X` is a number. The range of numbers might not
be known beforehand but we still want to group logs with the same numbers
together or more likely, with the same code, ID, timestamp, etc. We can
accomplish this with [`itertools.groupby`](https://docs.python.org/3/library/itertools.html#itertools.groupby).

A `groupby` requires a function that will indicate how to group as well as
generally sort the data to pack group components together. Then, it can separate
the keys and the groups. Here is an example with tuples where the first element
of the tuple is the key.

```python
from itertools import groupby

unique_keys = []
groups = []
l = [("a", 1, 2), ("b", 3, 4), ("b", 2), ("c", 11, 12), ("a", 0, 2, 6)]
key_func = lambda x : x[0]
data = sorted(l, key=key_func)
for key, group in groupby(data, key_func):
    unique_keys.append(key)
    # returns an iterator so wrapping in list is necessary
    groups.append(list(group))

print(unique_keys)
print(groups)
```

```text
['a', 'b', 'c']
[[('a', 1, 2), ('a', 0, 2, 6)], [('b', 3, 4), ('b', 2)], [('c', 11, 12)]]
```

In the output, you can see that the data is sorted by the keys (first element)
and put into a list, for each key. This is exactly what we are going to do with
the file names but using a key-value pair (a dictionary) instead of plain lists.

Let's try it with the following files under the same directory:

```text
AREA44_LOG1.txt
AREA51_LOG2.txt
info.md
AREZ51_LOG3.txt -> mistake here!
AREA23_LOG1.txt
AREA51_LOG1.txt
junk.json
AREA00_LOG1.txt
Makefile.mk
AREA23_LOG2.txt
```

We would like to filter only the text files and group the area paths together
but there's a small mistake in one of the file name, which would lead to it
having its own group. We don't want groups to be created willy-nilly so let's
add a filter to remove anything that doesn't start with `AREA`. This will
require a bit of knowledge of [regex](https://docs.python.org/3/library/re.html).

```python
import re

# Filters paths by file name (ignores the rest of the path)
def filter_keyword(path_generator, regex):
    pat = re.compile(rf'{regex}')
    return filter(lambda x: re.match(pat, x.name), path_generator)
```

Next, let's call this function with a simple regex after filtering by extension:

```python
p = Path("test-groups")

list(filter_keyword(filter_extensions(p, "txt", 0), r'^AREA'))
```

```text
[PosixPath('test-groups/AREA44_LOG1.txt'),
 PosixPath('test-groups/AREA51_LOG2.txt'),
 PosixPath('test-groups/AREA23_LOG1.txt'),
 PosixPath('test-groups/AREA51_LOG1.txt'),
 PosixPath('test-groups/AREA00_LOG1.txt'),
 PosixPath('test-groups/AREA23_LOG2.txt')]
```

Finally, let's set the keys as well as grouping rule as having the same
characters before the underscore (`_`). Each area name will be stored as a
dictionary key while the paths will be the values. A [`defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict) is used to
store the elements.

```python
from collections import defaultdict

keyfunc = lambda x : x.name.split("_")[0] # first element of split on `_`

def group_files(filepaths, key_function):
    grp_files = defaultdict(list)
    data = sorted(filepaths, key=key_function)
    for key, group in groupby(data, key_function):
        grp_files[key] = list(group)

    return grp_files
```

When everything is put together, we can just do this:

```python
p = Path("test-groups")
keyfunc = lambda x : x.name.split("_")[0]

group_files(filter_keyword(filter_extensions(p, "txt", 0), r'^AREA'), keyfunc)
```

```text
defaultdict(<class 'list'>,
{
'AREA00': [PosixPath('test-groups/AREA00_LOG1.txt')],
'AREA23': [PosixPath('test-groups/AREA23_LOG1.txt'), PosixPath('test-groups/AREA23_LOG2.txt')],
'AREA44': [PosixPath('test-groups/AREA44_LOG1.txt')],
'AREA51': [PosixPath('test-groups/AREA51_LOG2.txt'), PosixPath('test-groups/AREA51_LOG1.txt')]
})
```

Which closes the grouping section, the next step is to move each group of files
into a dedicated folder.


## Moving &amp; copying files {#moving-and-copying-files}

Up until now, we've only manipulated file paths which is quite safe and if you
played around with the code above, nothing big happened. This section though
will move actual files around, if you want to try the code out, do so with
useless files or non-critical directories at first.

The goal here is to use the keys of the grouped file paths as new directories to
store the files.

This will require a destination directory but no source directory as this
information is already contained in the (absolute) path of the files. Note that
the `/` operator is overloaded such that `path1 / path2` becomes
`path1/path2`. Also, the `parents` and `exist_ok` parameters are needed to
mirror those in [`Path.mkdir`](https://docs.python.org/3/library/pathlib.html#pathlib.Path.mkdir).

```python
def mv_files_into_dir(paths_dict, dest_dir, parents=False, exist_ok=False):
    for dir, files in paths_dict.items():
        curr_dir = dest_dir / dir
        Path.mkdir(curr_dir, parents=parents, exist_ok=exist_ok)
        for f in files:
            f.rename(curr_dir / f.name)
```

If we put all the calls together, we get:

```python
from pathlib import Path
from itertools import chain, groupby
from collections import defaultdict
import re

# functions definition here ... #

p = Path("test-groups")
out = Path("output-dir")

key_func = lambda x: x.name.split("_")[0]
paths_dict = group_files(
    filter_keyword(filter_extensions(p, "txt", 0), r'^AREA'), key_func
)

mv_files_into_dir(paths_dict, out)
```

With the output directory looking something like this:

```text
output-dir/
├── AREA00
│   └── AREA00_LOG1.txt
├── AREA23
│   ├── AREA23_LOG1.txt
│   └── AREA23_LOG2.txt
├── AREA44
│   └── AREA44_LOG1.txt
└── AREA51
    ├── AREA51_LOG1.txt
    └── AREA51_LOG2.txt
```

This **moved** the files, they are not in the `test-groups` directory anymore. As
such, you should have a strategy for reversal in case something wrong
happens. The [command pattern](https://en.wikipedia.org/wiki/Command_pattern) is aimed at encapsulating operations and allows for
reversal. I won't go into it because it's beyond the scope of the article but if
you're planning on making tools that move files around, an _undo_ command will
most likely come handy.

An alternative is the copy the files instead of moving them, using the [`shutil`](https://docs.python.org/3/library/shutil.html)
module, with the caveat that it won't copy the metadata (file creation time,
modification time) of the file unless you're willing to sacrifice some speed and
use `shutil.copy2`.

```python
import shutil

def copy_files_into_dir(paths_dict, dest_dir, parents=False, exist_ok=False):
    for dir, files in paths_dict.items():
        curr_dir = dest_dir / dir
        Path.mkdir(curr_dir, parents=parents, exist_ok=exist_ok)
        for f in files:
            shutil.copy(f, curr_dir) # use copy2 to try to keep metadata
```


## Conclusion {#conclusion}

In the post, I attempted to show how the powerful Python built-ins let us
manipulate paths and files, with cross-platform support. There are ways to
improve what's been shown; some of the functions would benefit from being
wrapped into a class and there are more powerful operations possible as
well. Probably the best path (😉) to improve the functionalities here would be
to use more complex functions during the `groupby` such as grouping per file
size until some threshold is reached or grouping per last file modification to
archive stale files.
---
title: "Python adventures: Finding unused dependencies"
date: 2023-05-27T00:00:00+02:00
tags: ["dependencies"]
categories: ["python"]
draft: false
---

# Python adventures: Finding unused dependencies

## Introduction {#introduction}

This article is about an issue I got a couple of times when working on medium to largish Python
projects and having to deploy them. It happens quite often that the dependencies are messy and
whoever is, or was working on the project happened to install a bunch of libraries because they
needed to add a new feature _now_. But when deployment comes, we want the environments or containers
to be lean for multiple reasons, build time and pipelines latency being some of them. After some
months working on the project, we are often left with many dependencies, not sure if they are needed
or not.

For that reason, I tried to build a small python tool that would let me go inside a project and
basically print out all the unused dependencies, which then become candidates for removal unless
advised otherwise.

If that sounds interesting to you and you'd like a look at the code, you [check it out on Github](https://github.com/Nathan-Furnal/depslorer). In
short, it allows you to use a small CLI tool and do:

```sh
# -f -> --filenames
# -r -> --recursive
# -d -> --depfiles
python cli.py -f . -r true -d examples/example.toml
```

inside a project, to go through the whole project recursively and check which of your dependencies
are actually used or not. Then, you'll get messages printed in the console:

```text
'pandas' is probably unused.
'scipy' is probably unused.
```

In the next parts of the post, I'll break down the functions and functionalities to make that
possible, we'll talk about naming things, Abstract Syntax Trees (AST's) and regular expressions.


## What's in a name {#what-s-in-a-name}

First, I think it's important to know a bit about the packaging system in Python. Regardless of your
package management strategies (conda, pip, poetry...), when you're in a virtual environment,
installed packages will be (almost every time) in the `lib/python<version>/site-packages/`
directory. So anytime you do `conda install`, `pip install` or `poetry add` from within a virtual
environment; this is the place where you'll find the package's files and metadata. There are some
other ways to install packages, notably by cloning a repository, but we'll focus on what most people
do when they're working with Python, which is using the tools I just mentioned.

This is where the naming part comes in, you might think that when you install a package named
`some-package`, it becomes accessible as `some-package` as an import in your Python code. This is
trivially wrong because Python does not allow hyphens in identifiers, so you should expect it to be
`some_package`. Not as obvious, it is also possible that the package provides an entirely different
name for imports, which can't be found from the package name only. Notable examples are
`scikit-learn` being available as `sklearn`, `beautifulsoup4` being available as `bs4` or `pyyaml`
being `yaml`. If you check out the source code for all those projects, you'll find that the name of
the package which contains the code is the name used in imports but the name of the project is the
one used for installs. In short, the name used for imports is the actual name of the directory
containing the package's code and the name of the package that is retrieved with package managers,
is whatever it is called and published as. This is all well and good, but when we are interacting
with dependencies, the project name is used, not the import name. So we need to find a strategy to
link the two together.

When you install packages in the ways we mentioned, you get the package's code but also its
metadata, a package called `stuff` will also provide a `stuff-<version>.egg-info` or
`stuff-<version>.dist-info` directory. Those directories sometimes contain a file called
`top_level.txt` that gives the import names (yes, there are multiple sometimes!) for a package. A
simple heuristic got me quite far: if the metadata provides a `top_level.txt` use it, and if that
file does not exist then the package name and import name are the same.

Armed with this knowledge, we can build the first part of the tool which reads that information in a
Python datastructure: a mapping of package name and its import names.  Python's standard library
does a lot of the heavy lifting since it provides tools to find where packages are installed as well
as manipulate paths and files. In the function below, I walk through the directories where
dependencies are installed, grab the ones ending with `-info` and look for the
`top_level.txt`. Depending on its presence, I apply the heuristic and then we have a neat mapping of
dependencies and import names.

```python
from collections import defaultdict
from pathlib import Path
import site

def get_installed_deps() -> dict[str, set[str]]:
    name_imports_mapping = defaultdict(set)
    for d in site.getsitepackages():
        info_dirs = Path(d).glob('*-info')
        for info_dir in info_dirs:
            # pkgs are named like pkg-<version>
            pkg_name = info_dir.stem.split("-")[0]
            if (fn := (info_dir / 'top_level.txt')).exists():
                import_names = fn.read_text().strip().splitlines()
                name_imports_mapping[pkg_name].update(import_names)
            else:
                name_imports_mapping[pkg_name].add(pkg_name)
    return name_imports_mapping
```

The datastructure above will look like this:

```text
{
'PyYAML': {'yaml', '_yaml'},
'numpy': {'numpy'},
'Pillow': {'PIL'}
}
```

Now that we have a better handle on the dependencies and their names, we still need to find which
are actually used in our own code, which is detailed in the next part.


## Playing in the trees {#playing-in-the-trees}

I think there are a couple ways to go about finding imports, they will all involve reading the
Python files in our project of course. We could:

-   Iterate over lines in a file and try to find all the ones using `import`.
-   Use regular expressions.
-   Use a method aware of the code's structure.

I think the first and second methods have their merits but since they don't 'understand' code
structure, they are also quick to breakdown. Think about what happens when you don't have top-level
imports rather ones in functions or when there are multi-line imports. Dealing with strings and
regular expressions quickly becomes a nightmare.

With that in mind, we can use Python's own parser which has an intimate knowledge of the language's
grammar. The grammar of the language and the whole of a program structure are described by a
datastructure called an abstract syntax tree (AST), for which Python also has a module, called
[`ast`](https://docs.python.org/3/library/ast.html). There are specific nodes of interest in a tree, namely `Import` and `ImportFrom`; they
contain all the information we need, so we'll use just that to collect the names of the imports in a
single set for the whole project.

In the function below, we go through each file's AST and walk down the tree to find the nodes
related to imports.

```python
from pathlib import Path
import ast

def get_used_imports(filepaths: str | Path | Iterable[str | Path]) -> set[str]:
    if isinstance(filepaths, (str, Path)):
        filepaths = [filepaths]
    imports: set[str] = set()
    for fp in filepaths:
        with open(fp, 'r') as f:
            tree = ast.parse(f.read(), filename=fp)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
    return imports
```

Now, we have a tool which gives us all the imports for as many files as we want and from the
previous section, we know the dependencies. Our next job is to try to compare the dependencies with
the imports.

There is a somewhat large caveat though. The logic above doesn't have any way to differentiate
between top-level dependencies and those dependencies' dependencies. Any installed package will be
added to the mapping and comparing the imports with the mapping will not yield a very useful report
because none (or few) of the installed packages dependencies are imported in our own code. To remedy
that issue, we can use dependency files in the form of a `requirements.txt`, `env.yml`,
`pyproject.toml`... Since those files document the actual, direct dependencies of a project, we can
use those to filter down the dependencies mapping and get a more realistic output.

As you might have guessed, the next section talks about parsing and using those files.


## Sometimes regular expressions are good enough {#sometimes-regular-expressions-are-good-enough}

Python's ecosystem can go a bit wild about defining dependencies so I'll go with a large hammer,
called regular expressions, to read dependency files. Here's the function that does just that and
gets packages' names from dependency files.

```python
from pathlib import Path
import tomllib
import yaml
import re

def deps_from_depfiles(filepaths: Path | Iterable[Path]):
    if isinstance(filepaths, Path):
        filepaths = [filepaths]
    deps: set[str] = set()
    for fp in filepaths:
        match(fp.suffix):
            case '.toml':
                with open(fp, 'rb') as f:
                    out = tomllib.load(f)
                    deps.update(_dep_from_toml(out))
            case '.txt':
                with open(fp) as f:
                    # Find all lines starting with a character and with zero or
                    # more letters separated by hyphens/underscores Note that
                    # this doesn't enforce any 'correct' naming for the packages
                    # it just makes sure to catch possible packages names
                    deps.update(re.findall(r'^\w+[-_\w+]*', fp.read_text().strip(), re.MULTILINE))
            case '.yml' | '.yaml':
                pat = re.compile(r'[\[=<>]')
                pat_git = re.compile(r'[@#\.]')
                with open(fp) as f:
                    out = yaml.safe_load(f)
                    for dep in out.get('dependencies', []):
                        # Check that the first char is alpha
                        # to avoid commands or invalid names
                        if isinstance(dep, str) and dep[0].isalpha():
                        # split on any of '[=<>' and get only the pkg name
                            deps.add(re.split(pat, dep)[0])
                        if isinstance(dep, dict) and dep.get('pip', None):
                            for el in dep['pip']:
                                # dependency like 'git+<...>'
                                if isinstance(el, str) and el.startswith('git'):
                                    # get the last element of the URL with a '/' split
                                    # and try to remove .git extension as well as @ or # details
                                    deps.add(re.split(pat_git, el.split('/')[-1])[0])
                                elif isinstance(el, str) and el[0].isalpha():
                                    deps.add(re.split(pat, el)[0])
            case _:
                raise ValueError(f"Unknown file extensions: {fp.suffix}")
    return deps
```

There's a lot going on here, since multiple file formats will have to be dealt with differently,
even worse, some tools use the same file format but with a different structure. So even if this
function looks a bit stuffy, it mostly contains file reading and regular expression logic. You'll
notice that the TOML files have their own function to parse them. The text files are parsed roughly,
only getting the names of the packages on the left-hand side of symbols like `[=<>`. The YAML files
are a bit trickier because multiple tools can be called from within the file: it's possible to both
add dependencies and call pip from inside the YAML. For each file type, we can then get the
dependency name and add it to a set of all dependencies. Note that this function does not cover all
possible edge cases, it's merely a starting point.


## Putting it all together {#putting-it-all-together}

We have everything to build a function bringing all the functionalities together.

```python
from pathlib import Path

def gen_unused_pkgs(deps: dict[str, set[str]],
                    used_imports: set[str],
                    depfiles: Path | Iterable[Path] | None = None):
    # Those packages are almost always installed or present and would be needlessly printed
    DEFAULT_PKGS = {'pip', 'setuptools', 'wheel', 'python', 'python_version'}
    has_issue = False
    file_deps = None
    if depfiles:
        file_deps = deps_from_depfiles(depfiles)

    for dep, import_names in deps.items():
        if not any(imp in used_imports for imp in import_names) and dep not in DEFAULT_PKGS:
            if not file_deps:
                has_issue = True
                print(f"'{dep}' is probably unused.")
            else:
                if dep.lower() in file_deps:
                    has_issue = True
                    print(f"'{dep}' is probably unused.")
    if not has_issue:
        print("No unused dependencies were found.")
```

The function iterates over all the dependencies with the names being the keys and the set of
possible import names being the values. If none of the possible import names are found in the actual
imports, then we know that the package is probably unused. The function works without any dependency
file and will flag all installed packages but it is advised to use it with a dependency file that
will narrow down the actual unused packages.


## Making a CLI {#making-a-cli}

Finally, we can build a small CLI that will make using the functionalities of the package a bit
easier. It uses `argparse` and enforces some number of arguments on the more important
parameters.

You might wonder why I decided to use `glob.glob` and not `Path.glob` to get the files; it is
because as of Python 3.11, the globbing interface lets us ignore hidden directories or files which is
handy because all the files in the `.venv` folder of the project shouldn't be accessed.

```python
import argparse
from deps_explorer import (
    get_installed_deps,
    get_used_imports,
    gen_unused_pkgs,
)
from pathlib import Path
import glob

def fnames(string):
    if string == ".":
        return ["**/*.py"]
    else:
        return string

def parse_fnames(inp: list[str], recur: bool):
    if len(inp) > 1:
        return [Path(p) for p in inp]
    else:
        el = inp[0]
        if '*' in el:
            return [Path(p) for p in glob.glob(el, recursive=recur)]
        else: return Path(el)


parser = argparse.ArgumentParser(prog="Dependencies explorer")
parser.add_argument("-f", "--filenames", default=".", type=fnames, nargs='+')
parser.add_argument("-r", "--recursive", choices=["true", "false"], default="true")
parser.add_argument("-d", "--depfiles", nargs="*", default=None)

def main():
    args = parser.parse_args()
    recur = True if args.recursive == "true" else False
    filenames = parse_fnames(args.filenames, recur=recur)
    depfiles = parse_fnames(args.depfiles, recur=False) if args.depfiles else None
    try:
        gen_unused_pkgs(
            get_installed_deps(),
            get_used_imports(filenames),
            depfiles
        )
    except FileNotFoundError as fnfe:
        print(f"No such file: {fnfe.filename}")
        print("CLI was stopped!")

if __name__ == '__main__':
    main()
```

Hopefully, this has been an interesting delve into Python's functionalities.

Thanks for reading 🤖

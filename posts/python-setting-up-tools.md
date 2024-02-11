---
title: "Python adventures: Setting up a robust environment"
date: 2024-02-11
draft: false
tags: 
    - python
---
# Setting up a robust Python development environment

There used to be quite a lot of jokes in Python circles and beyond, that after some time using the
language, you could just reinstall everything from scratch as finicky dependencies would
break your computer. Or, your own Python installation would break the one used by
the system.

I think this is somewhat true if you're starting out and haven't taken the habit
of using virtual environments (a.k.a `venv`) & friends and I'd like to motivate
a list of tools I'm using on my day to day working with Python, which help me
avoid those issues.

What I want to do, is take you through a series of useful tools for managing
different Python versions, different virtual environments and define a good
"recipe" to work with Python.

I've setup those tools on both Linux and MacOS where I can attest that they
work, I make no such promises for Windows but you can [use
WSL](https://learn.microsoft.com/en-us/windows/wsl/) to use Linux on Windows.

If you already know about some of those tools and only want the resulting
workflow, you can [go directly to that section](#workflow).

## Managing different Python versions

A typical issue when working with Python is dealing with multiple Python versions,
because some packages only work in a specific range of versions. It's usually
fine to start with the system-installed Python and create virtual environments
to work in, but it'll only take you so far.

This is where [`pyenv`](https://github.com/pyenv/pyenv) comes in. It lets you
install different Python versions alongside each other and plays nice with your
system install.

You can install it with your package manager or a script. Once it is done, you can simply
use the following command to list the existing Python versions available for installation.
```sh
pyenv install -l
```
There's a **lot** of versions though so you should probably filter them down
with your tool of choice, here's an example filtering for Python 3.12 with
`grep`. 
```sh
pyenv install -l | grep 3.12
```
Once you've made your choice, you can install a specific version.
```sh
pyenv install 3.12.2
```
Then, list the installed versions with:
```sh
pyenv versions
```
I really recommend you to read the short documentation of the project and setup
your shell (it supports `bash`, `zsh` and `fish`) to use it. The docs will show
you how to setup a global Python version and local, potentially per-project,
Python versions.

## Managing virtual environments

The tool we just installed, `pyenv`, also comes with plugins, and one is
particular is especially useful:
[`pyenv-virtualenv`](https://github.com/pyenv/pyenv-virtualenv). It lets you
create virtual environments with existing Python versions already installed with
`pyenv`.

There are three things to do here that I believe will make your life easier: 

- Install `pyenv-virtualenv` and add the line in your shell so that it
  automatically activates virtual environments.
  
- Pick up the habit of using the tool to create and destroy virtual
  environments. You just need to add a
  [`.python-version`](https://github.com/pyenv/pyenv-virtualenv?tab=readme-ov-file#activate-virtualenv)
  file with the name of the virtual environment at the root of the project to
  activate it automatically.
  
- Alias `pip` to `pip --require-virtualenv`.

The last point is about using shell aliases to substitute a command with
another. If you add the following line to your `.bashrc` or `.zshrc` or whatever
shell you're using that supports aliases:
```sh
alias pip='pip --require-virtualenv'
```
It will ensure that the Python package installer bundled with every Python
installation, `pip`, errors out if you're trying to use it outside a virtual
environment. I recommend to do it because `pip` will happily install a package
with all its dependencies when asked to, but to this day still doesn't have a
way to uninstall a package with all its dependencies. If you're working inside a
virtual environment, you can always destroy it and try again from scratch but
if you had forgotten to activate it beforehand, your system would be
littered with system-wide installed Python packages.

## Managing system-wide packages

In the previous section, I pointed that system-wide Python packages are a pain
and something to avoid. But in some cases, you might want to install a package
that is available everywhere, just like one installed from your package manager
or an executable.

The answer to this problem is [`pipx`](https://pipx.pypa.io/stable/) and it lets
you contain Python packages that you want to have accessible everywhere, which
is especially useful when those packages aren't available through the system
package manager.

Examples of such packages are:

- [`poetry`](https://python-poetry.org/)
- [`hatch`](https://hatch.pypa.io/latest/)
- [`toolong`](https://github.com/textualize/toolong)
- [`tox`](https://tox.wiki/en/4.12.1/)
- [`httpie`](https://httpie.io/docs/cli)
- ...

Per the docs, you'll need to install `pipx` with your system package manager or your
system's Python own `pip`.

There's not much to say aside from that, I use it to install `poetry` which will
be useful in the next section.

## Managing packages inside a virtual environment

Now that we have tools to choose which Python version we want to use as well as
create a virtual environment with said version, we need to manage the packages
inside the *virtualenv*. While it is possible to install packages with `pip`
(and hard to remove their dependencies) and it used to be common to have a
`requirements.txt` file to pin those dependencies, I much prefer
[`poetry`](https://python-poetry.org/) nowadays.

[`poetry`](https://python-poetry.org/) has several advantages which make it
attractive:

- It is a package manager that lets you properly install and remove packages
  (dependencies included).
  
- It lets you group dependencies together, typically required dependencies, test
  dependencies and development dependencies.
  
- It uses the new `pyproject.toml` file which lets you setup dependencies, tools
  settings and build workflow in one place. So you don't need a
  `requirements.txt`, `requirements-dev.txt`, `pytest.ini`,
  `mypy.ini`,... Everything fits neatly into that one file.
  
I think the docs are self-explanatory but if you use a setup with
`pyenv-virtualenv` there is a couple of variables to set in your shell
configuration:
```sh
export POETRY_VIRTUALENVS_CREATE=0 # Do not create virtualenv, we have pyenv for that
export POETRY_VIRTUALENVS_IN_PROJECT=1 # If creates a virtualenv, prefer doing it in the project instead
``` 
You can look up what those variables do but this ensures that `poetry` plays
nice with `pyenv` and its plugins, you don't need to set those variables if you
don't use `pyenv-virtualenv` though.

Note that `poetry` should be used inside a virtual environment.

## Workflow

For a typical workflow you can:

- Install `pyenv` and `pyenv-virtualenv`.
- Install `pipx`.
- Install `poetry` through `pipx`.
- Prefer having one *virtualenv* per project.
- Make sure to use those tools to create your virtual environments with the
  relevant Python version and manage the packages within the virtual environment
  with `poetry`.
  
This might seem like a lot of moving parts but a lot of the tools described here
go into the "install once and forget about it" category as you don't need to
update them often. They also do not require a lot of mental load since you only
need to know a couple common commands when using them.

## Not mentioned

Since this article focuses on my own workflow, there will be a ton of tools I
didn't mention but still think are useful. I just don't use them right now but
they might be interesting to you nonetheless.

- The [Hitchhiker's guide to Python](https://docs.python-guide.org/) is always a
  good read and uses `pipenv`.
  
- `mamba` which is a drop-in replacement for `anaconda` and especially useful
  when working with data science libraries which can have more brittle/finicky
  dependencies.
  
- A new all-in-one tool called [rye](https://rye-up.com/).



Thanks for reading 👾

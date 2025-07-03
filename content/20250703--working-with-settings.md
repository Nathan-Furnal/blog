+++
title = "Managing settings in Python projects"
slug = "managing-settings-in-python-projects"
date = 2025-07-04
tags = ["python", "softwareDesign"]
categories = ["guide"]
draft = true
+++

## Motivation

In general, I've not seen any strong prescription in how to deal with settings when
working on Python applications. As the project grows and when you're exposing multiple
kinds of configurations, it makes sense to have a common interface to handle settings.

Otherwise, it can lead to some frustration, as any time you're working on an application
with multiple people, you'll find a mix of `.env` or JSON files, hard-coded global
variables and even some amount of setting and getting global environment variables.

What I've found useful instead of using any mix of the above solutions, is to define
**local**, **immutable** and **dumb** python objects defined in one place, which I can
then pass around the application. Ideally, I do not want to add a new dependency solely
for configuration purposes so the solution I'm looking for should rely on the standard
library. Note that if you already depend on
[pydantic](https://docs.pydantic.dev/latest/), they have a library called
[`pydantic-settings`](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
which fits the bill but I wouldn't introduce it otherwise.

## What makes useful settings

Developing the previous section a bit more in depth, I believe great settings are:

- **local** in the sense that they shouldn't modify or be affected by some global state
  and should be safe to pass around in different parts of the code.
- **immutable** such that there is no question about the configuration, it is setup
  once and there is no potential change of state as you would have with a `dict`.
- **dumb**, meaning that there is no specific behavior of business logic implemented
  by the settings object, it should be plain data.

You might have an inkling to where I'm going with this: using
[`dataclasses`](https://docs.python.org/3/library/dataclasses.html), which were added
back in Python 3.7 and truly blossomed in Python 3.10 when many new features appeared.

I'll also add that you should put your configuration related `dataclasses` in one module,
which I usually call `settings.py` or `config.py`. Moreover, you should have one object
per kind of setting (web server, DB, resource access,…) though having a larger object
that bundles all configurations is fine.

This is what it might look like:

```python
from dataclasses import dataclass
```

### From global to local

### From mutable to immutable

## Tools nudging you in the right (and wrong) direction

I'll stand on the shoulders of giants and show some libraries I think do a good job
showing users how to use settings properly and which are not.

## Conclusion

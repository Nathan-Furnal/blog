+++
title = "Managing settings in Python projects"
slug = "managing-settings-in-python-projects"
date = 2025-07-05
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

Depending on your background and experience, you might never have encountered
those issues but if you work in data science or on machine learning adjacent
projects, they'll probably ring a bell, in part because of choices made in the
most common frameworks and libraries in the field.

N.B: You can [jump to the code](#code) if you prefer.

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

Let's go with an example now, where I'll setup the [connection to a DB with
SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/engines.html#engine-configuration),
with a more legwork with a `Secret` type, which isn't safe by any means but
won't default to printing the value of the secret.

In a `config.py`, there's now:

```python
from dataclasses import dataclass
from typing import final, override

@final
@dataclass(frozen=True, repr=False)
class Secret:
    _value: str

    @property
    def value(self) -> str:
        raise NotImplementedError

    def get_secret_value(self) -> str:
        return self._value

    @override
    def __str__(self) -> str:
        return "Secret(*****)"

    @override
    def __repr__(self) -> str:
        return "Secret(*****)"


@dataclass(frozen=True, kw_only=True)
class DBSettings:
    drivername: str
    username: str
    password: Secret
    host: str
    port: int
    database: str

    def to_dict(self) -> dict[str, str | int]:
        # dataclasses.asdict is also valid
        # as long as the password is handled properly
        return {
            "drivername": self.drivername,
            "username": self.username,
            "password": self.password.get_secret_value(),
            "host": self.host,
            "port": self.port,
            "database": self.database,
        }
```

Which makes it possible to pass the dictionary generated from `DBSettings`, to
the `URL.create` function of SQLAlchemy.

By using `frozen=True`, any attempt at modifying the members of `DBSettings`
will raise a `FrozenInstanceError`.

You can improve the snippet by setting default values with the `field` function
of `dataclasses`.

### Settings from files

Of course, you might want or need to read the configuration from a file, let's
say a `.env` one. Such a file will look like this:

```
DB_DRIVERNAME=postgresql+psycopg
DB_USERNAME=user
...
```

I don't want to install `python-dotenv`, it's yet another dependency that I
think isn't needed. A simple alternative is to create a class method that
receives a file path, and build the settings from there. I'll also create a
couple helper functions to find the root of the project since environment and
configuration files are often at the root.

Still in the `config.py`, I'll add:

```python
from pathlib import Path

PROJ_ROOT = Path(__file__).parents[1]


def get_project_root() -> Path:
    return PROJ_ROOT
```

Now, to get a configuration file from the root, you can do:

```python
from app import config

env_file = config.get_project_root() / ".env"
# ...
```

We'll want to be able to read files and generate a settings object straight from an
`.env` file, I've made some choices about how to read the file: only accepting prefixed
variables and ignoring extraneous variables.

Here's the abridged version of the `DBSettings` object with a new prefix highlighted
as well as a couple tools annotations since they are static analysis tools and I am
relying on dynamic typing by fetching the types of the fields straight from the class
definition.

```python
@dataclass(frozen=True, kw_only=True)
class DBSettings:
    env_prefix: ClassVar[str] = "DB_"
    drivername: str
    username: str
    password: Secret
    host: str
    port: int
    database: str

    @classmethod
    def from_dotenv(cls: type[Self], fp: Path) -> Self:
        cls_fields = fields(cls)
        key_type_map: dict[str, type] = {  # pyright: ignore[reportAssignmentType]
            f.name: f.type for f in cls_fields if not f.name.startswith("_")
        }
        data: dict[str, str | Secret | int] = {}
        lines = [
            line
            for line in fp.read_text().lstrip().splitlines()
            if line.startswith(cls.env_prefix)
        ]
        for line in lines:
            key, val = (s.strip() for s in line.split("="))
            key = key.lower().removeprefix(cls.env_prefix.lower())
            if key in key_type_map:
                dtype = key_type_map[key]
                data[key] = dtype(val)
        return cls(**data)  # pyright: ignore[reportArgumentType]
```

I think this is a decently useful implementation which can be extended or copied
for anyone's needs.

## Tools nudging you in the right (and wrong) direction

I'll stand on the shoulders of giants and show some libraries I think do a good job
showing users how to use settings properly and which are not.

## Code

You can read the [full code and tests] to get a better picture of the final result.

## Conclusion

"""Blog roll generator.

This module generates a blog roll for the files of a given folder, as long as they follow
the pattern given by https://protesilaos.com/emacs/denote#h:4e9c7512-84dc-4dfb-9fa9-e15d51178e5d
which is an efficient file-naming scheme as follows:

DATE==SIGNATURE--TITLE__KEYWORDS.EXTENSION

This way, only file names are necessary to add information to the blog roll and all
operations are safe, since a file is never opened or modified.

`denote.el` documentation defines the time until the second but for the purpose of
blog posts, a daily granularity is fine.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Self, final, override

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

PAT = re.compile(
    # %Y%m%d date     optional signature         title                           keywords
    r"(?P<date>\d{8})(?:==(?P<sig>[a-z0-9]+))?--(?P<title>[a-z0-9][a-z0-9\-]+)__(?P<keywords>[a-z0-9][a-z0-9_]+)\."
)

# Dot separator may appear multiple times for some files like `.tar.gz` or `.txt.zip`
# This is not supported though -> only accept txt based files
SEPARATORS: tuple[str, ...] = ("==", "--", "__", ".")


@dataclass(frozen=True)
class BlogPost:
    date: datetime
    signature: str | None
    title: str
    keywords: tuple[str, ...]
    extension: str

    @classmethod
    def from_fp(cls: type[Self], fp: Path) -> Self:
        """Build a blog post from a file path.

        Parameters
        ----------
        cls : type[Self]
            The BlogPost type or one of its children.
        fp : Path
            The path to build the blog post from.

        Returns
        -------
        Self
            A new instance of the blog post or of a child class.

        Raises
        ------
        ValueError
            When a separator appears multiple times.
            When the path doesn't match the structure.
        """
        for sep in SEPARATORS:
            if str(fp).count(sep) > 1:
                msg = f"Separator '{sep}' can only appear at most once in file path."
                raise ValueError(msg)
        rematch = PAT.match(str(fp))
        if rematch is None:
            msg = f"Invalid file path: {fp!s}"
            raise ValueError(msg)
        date: datetime = datetime.strptime(rematch.group("date"), "%Y%m%d").replace(tzinfo=UTC)
        sig: str | None = rematch.group("sig")
        title: str = rematch.group("title")
        keywords: tuple[str, ...] = tuple(rematch.group("keywords").split("_"))
        extension: str = fp.suffix
        return cls(date=date, signature=sig, title=title, keywords=keywords, extension=extension)


@final
class BlogRollDirective(SphinxDirective):
    # The path of the posts dir
    required_arguments = 1

    @override
    def run(self) -> Sequence[nodes.Node]:
        return super().run()

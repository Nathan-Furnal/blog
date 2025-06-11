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
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import ExtensionMetadata

PAT = re.compile(
    # %Y%m%d date     optional signature         title                           keywords
    r"(?P<date>\d{8})(?:==(?P<sig>[a-z0-9]+))?--(?P<title>[a-z0-9][a-z0-9\-]+)__(?P<keywords>[a-z0-9][a-z0-9_]+)\."
)

# Dot separator may appear multiple times for some files like `.tar.gz` or `.txt.zip`
# This is not supported though -> only accept txt based files
SEPARATORS: tuple[str, ...] = ("==", "--", "__", ".")


@dataclass(frozen=True)
class BlogPost:
    time: datetime
    signature: str | None
    title: str
    keywords: tuple[str, ...]
    extension: str

    @property
    def display_title(self) -> str:
        """Create the display title.

        Returns
        -------
        str
            Titled, space separated string.
        """
        first, *rest = self.title.split("-")
        return f"{first.title()} {' '.join(elem for elem in rest)}"

    @property
    def isoformat_date(self) -> str:
        """Return the ISO formatted string of the date.

        Returns
        -------
        str
            ISO formatted date string.
        """
        return self.time.date().isoformat()

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
        time: datetime = datetime.strptime(rematch.group("date"), "%Y%m%d").replace(tzinfo=UTC)
        sig: str | None = rematch.group("sig")
        title: str = rematch.group("title")
        keywords: tuple[str, ...] = tuple(rematch.group("keywords").split("_"))
        extension: str = fp.suffix
        return cls(time=time, signature=sig, title=title, keywords=keywords, extension=extension)


@final
class BlogRollDirective(SphinxDirective):
    # No content on the body, it's just displaying existing posts
    has_content = False
    # The path of the posts dir
    required_arguments = 1

    @override
    def run(self) -> Sequence[nodes.Node]:
        post_nodes = nodes.paragraph()
        dirpath = self.arguments[0]
        post_dir = Path(self.env.srcdir).resolve() / dirpath
        paths = [p.relative_to(post_dir) for p in post_dir.glob("*.rst")]
        posts = sorted(
            (BlogPost.from_fp(fp) for fp in paths),
            key=lambda bp: bp.time,
            reverse=True,
        )

        for path, post in zip(paths, posts, strict=True):
            para = nodes.paragraph()
            para.append(nodes.Text(f"{post.isoformat_date} - "))
            link = nodes.reference()
            link["refuri"] = f"{dirpath}/{path.with_suffix('.html')}"
            link.append(nodes.Text(post.display_title))

            para.append(link)
            para.append(nodes.Text("\u00a0\u00a0\u00a0\u00a0"))
            para.append(nodes.Text(f"@{' @'.join(post.keywords)}"))
            post_nodes.append(para)

        if not posts:
            post_nodes.append(nodes.Text("No blog posts..."))

        return [post_nodes]


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive("blogroll", BlogRollDirective)

    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

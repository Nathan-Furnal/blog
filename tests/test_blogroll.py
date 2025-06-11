from datetime import UTC, datetime
from pathlib import Path

import pytest

from source._ext.blogroll import BlogPost


@pytest.mark.parametrize(
    ("fp", "blog_post"),
    [
        (
            Path("20250124==testsig--my-test-title__test_file.rst"),
            BlogPost(
                time=datetime(2025, 1, 24, tzinfo=UTC),
                signature="testsig",
                title="my-test-title",
                keywords=("test", "file"),
                extension=".rst",
            ),
        ),
        (
            Path("20250124--my-test-title__test_file.md"),
            BlogPost(
                time=datetime(2025, 1, 24, tzinfo=UTC),
                signature=None,
                title="my-test-title",
                keywords=("test", "file"),
                extension=".md",
            ),
        ),
        (
            Path("19991111==ab--title__testing.txt"),
            BlogPost(
                time=datetime(1999, 11, 11, tzinfo=UTC),
                signature="ab",
                title="title",
                keywords=("testing",),
                extension=".txt",
            ),
        ),
    ],
)
def test_blogpost_can_be_created_from_path(fp: Path, blog_post: BlogPost):
    assert BlogPost.from_fp(fp) == blog_post


@pytest.mark.parametrize(
    "fp",
    [
        # Invalid date format: hyphen seperator
        Path("2025-01-24==testsig--my-test-title__test_file.rst"),
        # Invalid signature: underscore
        Path("20250124==test_sig--my-test-title__test_file.rst"),
        # Invalid title: bad casing
        Path("20250124==testsig--my-Test-Title__test_file.rst"),
        # Invalid title: starts with hyphen
        Path("20250124==testsig---my-test-title__test_file.rst"),
        # Invalid keywords: bad casing
        Path("20250124==testsig--my-test-title__test_File.rst"),
        # Invalid keywords: starts with underscore
        Path("20250124==testsig--my-test-title___test_file.rst"),
    ],
)
def test_invalid_path_pattern_raises_value_error(fp: Path):
    with pytest.raises(ValueError, match="Invalid file path"):
        _ = BlogPost.from_fp(fp)


@pytest.mark.parametrize(
    "fp",
    [
        # Multiple '=='
        Path("20250124==testsig==other--my-test-title__test_file.rst"),
        # Multiple '--'
        Path("20250124==testsig--my-test--title__test_file.rst"),
        # Multiple '__'
        Path("20250124==testsig--my-test-title__test__file.rst"),
        # Multiple extensions
        Path("20250124==testsig--my-test-title__test_file.rst.gz"),
    ],
)
def test_invalid_path_with_multiple_separators_raises_value_error(fp: Path):
    with pytest.raises(ValueError, match="Separator"):
        _ = BlogPost.from_fp(fp)

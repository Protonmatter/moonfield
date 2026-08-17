"""Worked examples in the lessons must be output the code actually produces.

The curriculum's method is: predict, run, compare, explain the difference. That
only works if the numbers printed in a lesson are the numbers the reader gets.
A lesson showing output from an engine that has since moved on teaches the
reader to distrust their own correct result, which is worse than teaching them
nothing.

How to mark a block for checking
--------------------------------
Put an HTML comment directly above the fenced block::

    <!-- moonfield-check: phase --date 2026-08-16T00:00:00Z --explain --no-art -->

    ```
      Phase:        Waxing Crescent
    ```

The test runs ``moonfield`` with those arguments and requires the block to
appear, verbatim, as a run of consecutive lines in the real output. Excerpting
is fine -- most lessons quote a few lines rather than a whole screen -- but
every character of what you do quote has to be real.

Two rules for the arguments you write there:

* Pin the instant, with a zone. ``--date 2026-08-16`` means local midnight, so
  it is a different instant in Sydney than in Chicago and the lesson would only
  be true where its author was sitting.
* Pin the place too, if the command needs one, so the example does not depend
  on whatever the reader has in their config file.
"""

from __future__ import annotations

import re
import shlex
from pathlib import Path

import pytest

from moonfield.cli import main

DOCS = Path(__file__).resolve().parents[1] / "docs"

MARKER = re.compile(
    r"<!--\s*moonfield-check:\s*(?P<args>.+?)\s*-->\s*\n+```[a-zA-Z]*\n(?P<block>.*?)```",
    re.DOTALL,
)


def checked_examples() -> list[tuple[Path, str, str]]:
    """Every (file, args, expected block) triple marked in the lessons."""
    found = []
    for path in sorted(DOCS.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in MARKER.finditer(text):
            found.append((path, match.group("args"), match.group("block")))
    return found


EXAMPLES = checked_examples()


def _normalise(text: str) -> list[str]:
    """Split into lines, ignoring trailing spaces an editor may have eaten."""
    return [line.rstrip() for line in text.rstrip("\n").split("\n")]


def _is_run_of_lines(needle: list[str], haystack: list[str]) -> bool:
    """True when `needle` appears as consecutive lines within `haystack`."""
    if not needle:
        return False
    for start in range(len(haystack) - len(needle) + 1):
        if haystack[start : start + len(needle)] == needle:
            return True
    return False


@pytest.mark.skipif(not EXAMPLES, reason="no lesson examples are marked for checking")
@pytest.mark.parametrize(
    "path,args,block",
    EXAMPLES,
    ids=[f"{p.parent.name}/{p.name}:{i}" for i, (p, _, _) in enumerate(EXAMPLES)],
)
def test_lesson_example_matches_real_output(path, args, block, capsys):
    argv = shlex.split(args)
    code = main(argv)
    produced = capsys.readouterr().out

    assert code == 0, f"`moonfield {args}` failed, in {path.name}"

    expected = _normalise(block)
    actual = _normalise(produced)

    if not _is_run_of_lines(expected, actual):
        raise AssertionError(
            f"{path.relative_to(DOCS.parent)} quotes output that "
            f"`moonfield {args}` does not produce.\n\n"
            "--- the lesson says ---\n" + "\n".join(expected) +
            "\n\n--- the command prints ---\n" + "\n".join(actual) +
            "\n\nUpdate the lesson, or fix whatever moved the numbers."
        )


def test_the_marker_syntax_is_not_silently_broken():
    """A typo'd marker would just stop checking, with nothing to notice.

    So: if a lesson mentions the marker at all, at least one has to parse.
    """
    mentions = [
        p for p in DOCS.rglob("*.md")
        if "moonfield-check" in p.read_text(encoding="utf-8")
    ]
    if mentions:
        assert EXAMPLES, (
            "moonfield-check appears in "
            + ", ".join(p.name for p in mentions)
            + " but no block parsed. Check the marker sits directly above a "
            "fenced block."
        )

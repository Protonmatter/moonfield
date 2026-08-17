"""The README's worked example must be real output.

A README that shows output the code no longer produces is a small lie, and
this project is in no position to tell it. The whole method is: predict, run,
compare, explain the difference. A front page whose numbers drifted away from
the engine years ago teaches the opposite lesson to the one intended.

So the example is not an illustration. It is a fixture. If you change the
phase engine, or the way `phase` lays out its output, this test fails and the
README gets updated in the same commit as the change that moved it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from moonfield.cli import main

README = Path(__file__).resolve().parents[1] / "README.md"

# The instant the README example is computed for, and the flags that produce
# it. Fixed, so the output is the same on every machine and in every year.
EXAMPLE_ARGS = ["phase", "--date", "2026-08-16T21:00:00Z", "--timezone", "Europe/London"]
EXAMPLE_OPENING = "Moon phase for 2026-08-16 22:00 BST"


def readme_example() -> str:
    """Pull the fenced block containing the phase example out of the README."""
    text = README.read_text(encoding="utf-8")
    # The optional language tag matters: without it, ```bash openers are not
    # recognised as openers, and the scan pairs one block's closing fence with
    # the next block's opening fence -- silently returning the prose between
    # two code blocks instead of the code.
    for block in re.findall(r"```[a-zA-Z]*\n(.*?)```", text, re.DOTALL):
        if block.startswith(EXAMPLE_OPENING):
            return block.rstrip("\n")
    pytest.fail(
        f"No fenced block in README.md starts with {EXAMPLE_OPENING!r}. "
        "If you moved or reworded the example, update EXAMPLE_OPENING here."
    )


def _has_london() -> bool:
    """True when this machine can resolve Europe/London.

    Windows ships no IANA database. `tzdata` is a dev dependency so the suite
    normally has one, but someone running the tests from a bare checkout
    should get a skip rather than a confusing diff of timezone abbreviations.
    """
    from zoneinfo import ZoneInfo

    try:
        ZoneInfo("Europe/London")
        return True
    except Exception:
        return False


class TestReadmeExample:
    @pytest.mark.skipif(
        not _has_london(),
        reason="the example is shown in BST, which needs the IANA timezone database",
    )
    def test_readme_still_shows_what_the_code_prints(self, capsys):
        code = main(EXAMPLE_ARGS)
        produced = capsys.readouterr().out.rstrip("\n")

        assert code == 0
        assert produced == readme_example(), (
            "README.md no longer matches `moonfield "
            + " ".join(EXAMPLE_ARGS)
            + "`.\nPaste the current output into the README, or fix the change "
            "that moved it."
        )

    def test_the_example_is_not_empty(self):
        """Guards the extractor itself, not the engine."""
        assert len(readme_example().splitlines()) > 10

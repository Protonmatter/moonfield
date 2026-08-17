"""The published site must contain the curriculum, and its links must work.

The site used to describe thirteen modules and link to none of them, so a
visitor could read about the curriculum but not read it. These tests exist so
that cannot quietly happen again: every lesson gets a page, every internal
link resolves to a file that exists, and no Markdown leaks through unrendered.

The renderer in tools/build_site.py covers only the Markdown the curriculum
actually uses. If you write a lesson using something it does not know about,
`test_no_unrendered_markdown` is what tells you.
"""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT / "tools"))

build_site = pytest.importorskip("build_site", reason="tools/build_site.py not present")


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site")
    build_site.build(out)
    return out


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "link"):
            for name, value in attrs:
                if name == "href" and value:
                    self.hrefs.append(value)


def internal_links(path: Path) -> list[str]:
    parser = LinkCollector()
    parser.feed(path.read_text(encoding="utf-8"))
    return [
        h for h in parser.hrefs
        if not re.match(r"^(https?:|mailto:|#)", h)
    ]


class TestEveryLessonIsPublished:
    def test_each_markdown_file_becomes_a_page(self, site):
        """Every lesson reachable, by name. A count would also pass if two
        lessons collided onto one URL and a third was invented."""
        missing = []
        for source in sorted(DOCS.rglob("*.md")):
            rel = source.relative_to(DOCS).with_suffix(".html")
            expected = site / "learn" / rel
            if source.name == "README.md":
                expected = expected.parent / "index.html"
            if not expected.exists():
                missing.append(str(rel))
        assert not missing, "lessons with no published page:\n" + "\n".join(missing)

    def test_directories_without_a_readme_still_get_an_index(self, site):
        """Otherwise /learn/troubleshooting/ is a 404 the sidebar links to."""
        for module in sorted(p for p in DOCS.iterdir() if p.is_dir()):
            if module.name == "assets" or not list(module.glob("*.md")):
                continue
            assert (site / "learn" / module.name / "index.html").exists(), module.name

    def test_the_landing_page_links_into_the_curriculum(self, site):
        text = (site / "index.html").read_text(encoding="utf-8")
        assert 'href="learn/' in text, "the site must offer a way into the lessons"
        # Every module directory should be reachable from the front page.
        for module in sorted(p.name for p in DOCS.iterdir() if p.is_dir()):
            if module[0].isdigit():
                assert f'href="learn/{module}/"' in text, f"no link to {module}"

    def test_the_interactives_survive_the_build(self, site):
        assert (site / "longitude-game" / "index.html").exists()

    def test_tide_datasets_are_published(self, site):
        """Lessons link to the CSVs, so they have to be served too."""
        assert list(site.glob("learn/04-tides/data/*.csv"))


class TestLinks:
    def test_every_internal_link_resolves(self, site):
        broken: list[str] = []
        for page in sorted(site.rglob("*.html")):
            for href in internal_links(page):
                target, _ = urldefrag(unquote(href))
                if not target:
                    continue
                resolved = (page.parent / target).resolve()
                if resolved.is_dir():
                    resolved = resolved / "index.html"
                if not resolved.exists():
                    broken.append(f"{page.relative_to(site)} -> {href}")
        assert not broken, "broken links:\n" + "\n".join(broken)

    def test_no_links_still_point_at_markdown(self, site):
        offenders = [
            f"{p.relative_to(site)}: {h}"
            for p in site.rglob("*.html")
            for h in internal_links(p)
            if h.endswith(".md") or ".md#" in h
        ]
        assert not offenders, "links to .md survived the build:\n" + "\n".join(offenders)


class TestRendering:
    def test_no_unrendered_markdown(self, site):
        """Markdown syntax visible in the output means a gap in the renderer.

        Only the text outside <pre> blocks is checked. Inside them, a `#` is a
        shell prompt or a Python comment and belongs exactly as written.
        """
        patterns = {
            "link": r"\[[^\]]{1,60}\]\([^)]{1,80}\)",
            "bold": r"\*\*[^*\n]{1,60}\*\*",
            "heading": r"(?m)^#{1,6} \S",
            "table row": r"(?m)^\|.*\|\s*$",
        }
        problems: list[str] = []
        for page in sorted(site.glob("learn/**/*.html")):
            text = page.read_text(encoding="utf-8")
            visible = re.sub(r"<pre.*?</pre>", "", text, flags=re.DOTALL)
            visible = re.sub(r"<[^>]+>", "", visible)
            for name, pattern in patterns.items():
                found = re.search(pattern, visible)
                if found:
                    problems.append(
                        f"{page.relative_to(site)}: unrendered {name}: "
                        f"{found.group()[:60]!r}"
                    )
        assert not problems, "\n".join(problems)

    def test_check_markers_do_not_reach_the_reader(self, site):
        """The moonfield-check comments are for the test suite, not the page."""
        for page in site.rglob("*.html"):
            assert "moonfield-check" not in page.read_text(encoding="utf-8")

    def test_pages_have_a_title_and_a_way_back(self, site):
        for page in sorted(site.glob("learn/**/*.html")):
            text = page.read_text(encoding="utf-8")
            assert "<title>" in text and "- Moonfield</title>" in text
            assert 'class="side"' in text, f"{page.name} has no navigation"

    def test_code_blocks_keep_their_content_literal(self, site):
        """A lesson showing `<details>` in a fence must not open a real one."""
        page = site / "learn" / "00-start-here" / "setup.html"
        text = page.read_text(encoding="utf-8")
        assert "&lt;" in text or "<pre>" in text
        assert text.count("<pre") == text.count("</pre>")

"""Render the curriculum in docs/ into a browsable site.

Why this exists
---------------
The Pages site used to be a landing page and one interactive. It described
thirteen modules and linked to none of them, so a visitor could read about the
curriculum but not read the curriculum. It dead-ended at a `git clone`.

Why it is written by hand
-------------------------
Moonfield installs with nothing but the standard library, and the interactives
load nothing from anyone else's server. Pulling in a Markdown library and a
static site generator to publish a project whose whole pitch is "you can read
every line that produced this" would be an odd trade. So this is a small
Markdown subset renderer covering exactly what the curriculum uses, which was
counted rather than guessed:

    inline code, headings, list items, bold, fenced code, tables, links,
    ordered lists, horizontal rules, task boxes, italics, blockquotes,
    nested lists, HTML comments, <details>

No images, footnotes, autolinks, or reference links appear anywhere in docs/,
so none are implemented. If you add one, add it here too and the test in
tests/test_site_build.py will tell you when you have forgotten.

Usage
-----
    python tools/build_site.py [--out _site]

Writes a complete site: the static pages from site/, plus every lesson under
/learn/, plus the tide datasets so the links to them resolve.
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
STATIC = ROOT / "site"

# Modules in reading order, with the titles the landing page shows. The
# directory names carry the order already; this map only supplies prettier
# titles and the ready/planned state.
MODULE_TITLES = {
    "00-start-here": "Start here",
    "01-time-and-place": "Time and place",
    "02-moon-phases": "Moon phases",
    "03-earth-moon-system": "The Earth-Moon system",
    "04-tides": "Tides",
    "05-local-sky": "Your local sky",
    "06-seasons": "Seasons",
    "07-planets": "Planets",
    "08-constellations": "Constellations",
    "09-physics": "The physics underneath",
    "10-orbital-mechanics": "Orbital mechanics",
    "11-rocketry": "Rocketry",
    "12-visualization": "Visualisation",
    "background": "Background",
    "interactives": "Interactives",
    "troubleshooting": "Troubleshooting",
    "instructor": "For instructors",
}

READY = {
    "00-start-here", "01-time-and-place", "02-moon-phases",
    "03-earth-moon-system", "04-tides", "05-local-sky", "06-seasons",
}


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------


def escape(text: str) -> str:
    return html.escape(text, quote=False)


def slug(text: str) -> str:
    """A heading id you can link to, from the heading's visible text."""
    plain = re.sub(r"[`*_\[\]()]", "", text).strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-") or "section"


REPO_URL = "https://github.com/Protonmatter/moonfield"

# Bare paths the lessons use that only mean something on github.com. Written
# as `../../issues` in Markdown so they work when read in the repository.
GITHUB_SHORTCUTS = {"issues", "discussions", "pulls", "labels", "wiki", "releases"}


def resolve_href(href: str, source_dir: Path) -> str:
    """Point a Markdown link at wherever that thing lives on the built site.

    Links in the curriculum are written to work when read on GitHub, which
    means some of them climb out of docs/ entirely: `../../issues` for the
    tracker, `../../CONTRIBUTING.md` for a file at the repository root. Those
    are fine in the repo and dead on a site, so anything that escapes docs/
    is sent to github.com instead.
    """
    if re.match(r"^[a-z]+:", href) or href.startswith("#"):
        return href

    path, _, fragment = href.partition("#")
    fragment = f"#{fragment}" if fragment else ""
    if not path:
        return href

    target = (source_dir / path).resolve()

    try:
        target.relative_to(DOCS)
    except ValueError:
        # Outside docs/. Either a GitHub shortcut or a file in the repository.
        name = path.rstrip("/").split("/")[-1]
        if name in GITHUB_SHORTCUTS:
            return f"{REPO_URL}/{name}{fragment}"
        try:
            in_repo = target.relative_to(ROOT)
        except ValueError:
            return f"{REPO_URL}{fragment}"
        return f"{REPO_URL}/blob/main/{str(in_repo).replace(chr(92), '/')}{fragment}"

    # Inside docs/: a lesson becomes a page, anything else is copied as-is.
    # A module's README is its index, so links to it must follow the rename.
    path = re.sub(r"(^|/)README\.md$", r"\1index.html", path)
    return re.sub(r"\.md$", ".html", path) + fragment


def inline(text: str, source_dir: Path | None = None) -> str:
    """Inline markup, in an order that keeps code spans literal.

    Code spans come out first and go back in last, because a backtick span may
    contain asterisks, underscores or anything else that would otherwise be
    read as emphasis. `**not bold**` has to survive as visible asterisks.
    """
    spans: list[str] = []

    def stash(match: re.Match) -> str:
        spans.append(match.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = re.sub(r"`([^`]+)`", stash, text)
    text = escape(text)

    def link(match: re.Match) -> str:
        label, href = match.group(1), match.group(2)
        href = resolve_href(href, source_dir or DOCS)
        rel = ' rel="noopener"' if href.startswith("http") else ""
        target = ' target="_blank"' if href.startswith("http") else ""
        return f'<a href="{html.escape(href, quote=True)}"{rel}{target}>{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)

    for i, code in enumerate(spans):
        text = text.replace(f"\x00{i}\x00", f"<code>{escape(code)}</code>")
    return text


def render(markdown: str, source_dir: Path | None = None) -> tuple[str, str, list[tuple[int, str, str]]]:
    """Return (html body, page title, [(level, id, text)] for the outline).

    ``source_dir`` is the directory the Markdown came from, needed to resolve
    relative links: the same `../../issues` means different things depending
    on how deep in docs/ the lesson sits.
    """
    lines = markdown.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    outline: list[tuple[int, str, str]] = []
    title = ""

    i = 0
    list_stack: list[str] = []  # open <ul>/<ol> tags, outermost first

    def close_lists(to_depth: int = 0) -> None:
        while len(list_stack) > to_depth:
            out.append(f"</{list_stack.pop()}>")

    while i < len(lines):
        line = lines[i]

        # Fenced code. Taken verbatim; nothing inside is markup.
        if line.lstrip().startswith("```"):
            close_lists()
            lang = line.strip().strip("`").strip()
            body: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].lstrip().startswith("```"):
                body.append(lines[i])
                i += 1
            i += 1
            cls = f' class="lang-{escape(lang)}"' if lang else ""
            out.append(f"<pre{cls}><code>{escape(chr(10).join(body))}</code></pre>")
            continue

        # HTML comments, including the moonfield-check markers, are for the
        # repository and the test suite, not for the reader.
        if line.strip().startswith("<!--"):
            while i < len(lines) and "-->" not in lines[i]:
                i += 1
            i += 1
            continue

        # <details> and friends pass straight through.
        if re.match(r"^\s*</?(details|summary)", line):
            close_lists()
            out.append(line.strip())
            i += 1
            continue

        if not line.strip():
            close_lists()
            i += 1
            continue

        if re.match(r"^---+\s*$", line):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            close_lists()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            ident = slug(text)
            if level == 1 and not title:
                title = re.sub(r"[`*]", "", text)
            outline.append((level, ident, re.sub(r"[`*]", "", text)))
            out.append(f'<h{level} id="{ident}">{inline(text, source_dir)}</h{level}>')
            i += 1
            continue

        # Tables: a header row, a separator of dashes, then body rows.
        if line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]
        ):
            close_lists()
            def cells(row: str) -> list[str]:
                return [c.strip() for c in row.strip().strip("|").split("|")]

            head = cells(line)
            i += 2
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            thead = "".join(f"<th>{inline(c, source_dir)}</th>" for c in head)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{inline(c, source_dir)}</td>" for c in r) + "</tr>"
                for r in rows
            )
            out.append(
                f"<div class='tablewrap'><table><thead><tr>{thead}</tr></thead>"
                f"<tbody>{tbody}</tbody></table></div>"
            )
            continue

        if line.lstrip().startswith(">"):
            close_lists()
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            inner, _, _ = render("\n".join(quote))
            out.append(f"<blockquote>{inner}</blockquote>")
            continue

        item = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", line)
        if item:
            indent, marker, text = item.group(1), item.group(2), item.group(3)
            depth = len(indent) // 2 + 1
            kind = "ul" if marker in "-*" else "ol"

            while len(list_stack) > depth:
                out.append(f"</{list_stack.pop()}>")
            if len(list_stack) < depth:
                out.append(f"<{kind}>")
                list_stack.append(kind)
            elif list_stack and list_stack[-1] != kind:
                out.append(f"</{list_stack.pop()}>")
                out.append(f"<{kind}>")
                list_stack.append(kind)

            box = re.match(r"^\[([ xX])\]\s+(.*)$", text)
            if box:
                checked = " checked" if box.group(1).lower() == "x" else ""
                out.append(
                    f'<li class="task"><input type="checkbox" disabled{checked}> '
                    f"{inline(box.group(2), source_dir)}</li>"
                )
            else:
                out.append(f"<li>{inline(text, source_dir)}</li>")
            i += 1
            continue

        # Anything else is a paragraph, running until a blank line.
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^\s*(#{1,6}\s|[-*]\s|\d+[.)]\s|>|\||```|---+\s*$|<!--|</?details|</?summary)",
            lines[i],
        ):
            para.append(lines[i].strip())
            i += 1
        if para:
            close_lists()
            out.append(f"<p>{inline(' '.join(para), source_dir)}</p>")
        else:
            i += 1

    close_lists()
    return "\n".join(out), title, outline


# ---------------------------------------------------------------------------
# Site assembly
# ---------------------------------------------------------------------------


@dataclass
class Page:
    source: Path
    url: str          # relative to the site root, e.g. learn/04-tides/index.html
    title: str
    module: str
    body: str = ""
    outline: list = field(default_factory=list)


def page_title(source: Path, rendered_title: str) -> str:
    if rendered_title:
        return rendered_title
    return source.stem.replace("-", " ").capitalize()


def lesson_order(module_dir: Path) -> list[str]:
    """Reading order for a module, taken from the order its README links them.

    Alphabetical would open module 00 with "Editors and IDEs" and bury "What
    is this?" in the middle. Each module README already lists its lessons in
    the order they are meant to be read, so that list is the ordering, and it
    stays correct when someone reorders the module without thinking about
    this script.
    """
    readme = module_dir / "README.md"
    if not readme.exists():
        return []
    text = readme.read_text(encoding="utf-8")
    seen: list[str] = []
    for match in re.finditer(r"\[[^\]]+\]\(([a-z0-9-]+\.md)\)", text):
        name = match.group(1)
        if name != "README.md" and name not in seen:
            seen.append(name)
    return seen


def module_index(directory: Path, module: str) -> Page:
    """A contents page for a directory that has no README of its own."""
    title = MODULE_TITLES.get(module, module)
    items = []
    for lesson in sorted(directory.glob("*.md")):
        _, lesson_title, _ = render(lesson.read_text(encoding="utf-8"), lesson.parent)
        label = page_title(lesson, lesson_title)
        items.append(f'<li><a href="{lesson.stem}.html">{escape(label)}</a></li>')
    body = (
        f'<h1 id="{slug(title)}">{escape(title)}</h1>'
        f"<p>{escape(title)} pages in this collection:</p>"
        f'<ul>{"".join(items)}</ul>'
    )
    return Page(directory, f"learn/{module}/index.html", title, module, body, [])


def collect() -> list[Page]:
    """Every lesson, in reading order: overview, then modules in order."""
    def make(source: Path) -> Page:
        rel = source.relative_to(DOCS)
        module = rel.parts[0] if len(rel.parts) > 1 else ""
        url = "learn/" + str(rel.with_suffix(".html")).replace("\\", "/")
        url = url.replace("/README.html", "/index.html").replace(
            "learn/README.html", "learn/index.html"
        )
        body, rendered_title, outline = render(source.read_text(encoding="utf-8"), source.parent)
        return Page(source, url, page_title(source, rendered_title), module, body, outline)

    pages: list[Page] = []

    top = DOCS / "README.md"
    if top.exists():
        pages.append(make(top))

    for module in MODULE_TITLES:
        directory = DOCS / module
        if not directory.is_dir():
            continue
        readme = directory / "README.md"
        if readme.exists():
            pages.append(make(readme))
        else:
            # background/ and troubleshooting/ are collections rather than
            # taught modules and have no README. Without an index page,
            # /learn/troubleshooting/ is a 404 and the sidebar heading leads
            # nowhere, so build them one from what is in the directory.
            pages.append(module_index(directory, module))
        ordered = lesson_order(directory)
        remaining = sorted(
            p for p in directory.glob("*.md") if p.name != "README.md"
        )
        for name in ordered:
            lesson = directory / name
            if lesson.exists():
                pages.append(make(lesson))
        for lesson in remaining:
            if lesson.name not in ordered:
                pages.append(make(lesson))

    # Anything in docs/ that no module claimed, so nothing goes unpublished.
    published = {p.source for p in pages}
    for source in sorted(DOCS.rglob("*.md")):
        if source not in published:
            pages.append(make(source))
    return pages


def depth_prefix(url: str) -> str:
    """`../` repeated enough times to climb from `url` back to the site root."""
    return "../" * url.count("/")


def sidebar(pages: list[Page], current: Page) -> str:
    by_module: dict[str, list[Page]] = {}
    for page in pages:
        by_module.setdefault(page.module, []).append(page)

    up = depth_prefix(current.url)
    parts = ['<nav class="side"><a class="home" href="' + up + 'index.html">Moonfield</a>']

    for page in by_module.get("", []):
        here = ' class="here"' if page.url == current.url else ""
        parts.append(
            f'<ul class="top"><li{here}><a href="{up}{page.url}">'
            f"{escape(page.title)}</a></li></ul>"
        )

    for module, module_pages in by_module.items():
        if not module:
            continue
        title = MODULE_TITLES.get(module, module)
        state = "ready" if module in READY else "planned"
        number = module.split("-")[0]
        parts.append(
            f'<p class="mod"><span class="n">{escape(number)}</span> {escape(title)}'
            f'<span class="s {state}">{state}</span></p><ul>'
        )
        # module_pages is already in reading order from collect().
        for page in module_pages:
            here = ' class="here"' if page.url == current.url else ""
            label = "Overview" if page.url.endswith("index.html") else page.title
            parts.append(f'<li{here}><a href="{up}{page.url}">{escape(label)}</a></li>')
        parts.append("</ul>")
    parts.append("</nav>")
    return "".join(parts)


PAGE_CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--abyss);color:var(--ink);font-family:var(--body);
  font-size:17px;line-height:1.7;-webkit-font-smoothing:antialiased}
a{color:var(--lamp)}
a:focus-visible{outline:2px solid var(--lamp);outline-offset:3px}
.layout{display:grid;grid-template-columns:17rem minmax(0,1fr);gap:3rem;
  max-width:78rem;margin:0 auto;padding:0 1.5rem}
.side{position:sticky;top:0;align-self:start;max-height:100vh;overflow-y:auto;
  padding:2rem 0 4rem;font-family:var(--display);font-size:.82rem;
  border-right:var(--rule)}
.side .home{display:block;font-size:1rem;letter-spacing:.02em;margin-bottom:1.6rem;
  text-decoration:none;color:#fff}
.side .mod{display:flex;align-items:baseline;gap:.5rem;margin:1.4rem 0 .4rem;
  color:#fff;font-size:.8rem}
.side .mod .n{color:var(--sounding);font-size:.7rem}
.side .mod .s{margin-left:auto;font-size:.58rem;letter-spacing:.14em;text-transform:uppercase}
.side ul{list-style:none;margin:0;padding:0 0 0 .2rem}
.side li{padding:.18rem 0}
.side li a{text-decoration:none;color:var(--ink);opacity:.82}
.side li a:hover{opacity:1}
.side li.here a{color:var(--lamp);opacity:1}
main{padding:2.5rem 0 6rem;min-width:0}
main h1{font-family:var(--display);font-size:clamp(1.8rem,4vw,2.5rem);color:#fff;
  line-height:1.15;margin:0 0 1.5rem}
main h2{font-family:var(--display);font-size:1.35rem;color:#fff;margin:2.8rem 0 .8rem}
main h3{font-family:var(--display);font-size:1.05rem;color:var(--lamp);margin:2rem 0 .6rem}
main p,main li{max-width:38rem}
pre{background:var(--water);border:var(--rule);border-top:2px solid rgba(240,189,99,.5);
  padding:1.1rem 1.3rem;overflow-x:auto;font-size:.88rem;line-height:1.5;
  font-family:var(--display)}
code{font-family:var(--display);font-size:.9em}
:not(pre)>code{background:var(--water);padding:.1em .35em;border-radius:3px;color:var(--lamp)}
blockquote{border-left:3px solid var(--sounding);margin:1.5rem 0;padding:.1rem 0 .1rem 1.2rem}
blockquote p{margin:.6rem 0}
hr{border:0;border-top:var(--rule);margin:2.5rem 0}
.tablewrap{overflow-x:auto;margin:1.5rem 0}
table{border-collapse:collapse;font-size:.92rem;min-width:100%}
th,td{border:var(--rule);padding:.5rem .8rem;text-align:left;vertical-align:top}
th{background:var(--water);font-family:var(--display);font-size:.8rem;
  letter-spacing:.04em;color:#fff}
li.task{list-style:none;margin-left:-1.2rem}
li.task input{margin-right:.5rem}
details{border:var(--rule);padding:.8rem 1.1rem;margin:1.2rem 0;background:rgba(13,40,54,.5)}
summary{cursor:pointer;font-family:var(--display);font-size:.9rem;color:var(--lamp)}
.pager{display:flex;justify-content:space-between;gap:1.5rem;margin-top:4rem;
  padding-top:1.5rem;border-top:var(--rule);font-family:var(--display);font-size:.85rem}
.pager a{text-decoration:none}
.pager .next{margin-left:auto;text-align:right}
.crumb{font-family:var(--display);font-size:.7rem;letter-spacing:.2em;
  text-transform:uppercase;color:var(--sounding);margin:0 0 .8rem}
.menu{display:none}
@media(max-width:900px){
  .layout{grid-template-columns:1fr;gap:0}
  .side{position:static;max-height:none;border-right:0;border-bottom:var(--rule)}
  main{padding-top:1.5rem}
}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<style>
:root{{
  --abyss:#08161e; --water:#0d2836; --sounding:#6fa3ad;
  --ink:#c9dde1; --lamp:#f0bd63; --rocks:#d1495b;
  --display:ui-monospace,"SFMono-Regular",Menlo,Consolas,"DejaVu Sans Mono",monospace;
  --body:Georgia,"Iowan Old Style","Times New Roman",serif;
  --rule:1px solid rgba(111,163,173,.28);
}}
{css}
</style>
</head>
<body>
<div class="layout">
{sidebar}
<main>
<p class="crumb">{crumb}</p>
{body}
{pager}
</main>
</div>
</body>
</html>
"""


def build(out_dir: Path) -> list[Page]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # Static pages and interactives first.
    for item in STATIC.iterdir():
        target = out_dir / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

    pages = collect()

    # Datasets the lessons link to, so those links resolve on the site too.
    for data in DOCS.rglob("*.csv"):
        target = out_dir / "learn" / data.relative_to(DOCS)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(data, target)

    for index, page in enumerate(pages):
        previous = pages[index - 1] if index else None
        following = pages[index + 1] if index + 1 < len(pages) else None
        up = depth_prefix(page.url)

        links = []
        if previous:
            links.append(
                f'<a class="prev" href="{up}{previous.url}">&larr; {escape(previous.title)}</a>'
            )
        if following:
            links.append(
                f'<a class="next" href="{up}{following.url}">{escape(following.title)} &rarr;</a>'
            )
        pager = f'<div class="pager">{"".join(links)}</div>' if links else ""

        crumb = MODULE_TITLES.get(page.module, "Curriculum")
        description = (
            f"{page.title}. Part of Moonfield, an open, AI-free curriculum in "
            "astronomy, maths and physics."
        )
        document = TEMPLATE.format(
            title=escape(f"{page.title} - Moonfield"),
            description=html.escape(description, quote=True),
            css=PAGE_CSS,
            sidebar=sidebar(pages, page),
            crumb=escape(crumb),
            body=page.body,
            pager=pager,
        )
        target = out_dir / page.url
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document, encoding="utf-8", newline="\n")

    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(ROOT / "_site"), help="output directory")
    args = parser.parse_args()

    out_dir = Path(args.out)
    pages = build(out_dir)
    print(f"Built {len(pages)} lesson pages into {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

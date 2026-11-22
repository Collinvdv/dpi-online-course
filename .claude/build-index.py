#!/usr/bin/env python3
"""
Build index.html at the repo root: an overview of every course, its modules
and languages, with links to every page. For this repo only; the TMS never
serves it (only files inside a course folder are served).

Mirrors how the TMS reads a course (app/Services/ELearningCourses.php):
- course    = top-level folder matching [a-z0-9-]+ (dot-folders never count)
- overview  = <course>/<lang>/index.html            (lang = nl, fr, en)
- module    = <course>/<module>/<lang>/index.html   (selectable as a page block)
- skipped   = <course>/media and the nl / fr / en folders themselves
- title     = <title> within the first 4096 bytes of the page

Run:  python3 .claude/build-index.py
"""

import html
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = ["nl", "fr", "en"]
NAME = re.compile(r"^[a-z0-9-]+$")
MEDIA_EXT = {".mp3", ".mp4", ".m4a", ".ogg", ".wav", ".webm"}
ROOT_FILES_OK = {"README.md", "CLAUDE.md", "index.html", ".gitignore", ".gitmodules", ".DS_Store"}


def title_of(page: Path) -> str | None:
    try:
        head = page.read_bytes()[:4096].decode("utf-8", "replace")
    except OSError:
        return None
    m = re.search(r"<title>([^<]{1,200})</title>", head, re.I)
    return html.unescape(m.group(1)).strip() if m else None


def size_of(folder: Path) -> tuple[int, int, int]:
    total = media = count = 0
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for f in filenames:
            if f.startswith("."):
                continue
            p = Path(dirpath) / f
            n = p.stat().st_size
            total += n
            if p.suffix.lower() in MEDIA_EXT:
                media += n
                count += 1
    return total, media, count


def mb(n: int) -> str:
    return f"{n / 1024 / 1024:,.0f} MB" if n >= 1024 * 1024 else f"{n / 1024:,.0f} KB"


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def scan(course: Path) -> dict:
    warnings = []
    overview = {l: course / l / "index.html" for l in LANGUAGES if (course / l / "index.html").is_file()}
    if not overview:
        warnings.append("No overview page (nl/index.html, fr/index.html or en/index.html): the portal has nothing to open.")

    modules, covered = [], set(overview.values())
    for entry in sorted(course.iterdir()):
        if entry.name.startswith("."):
            continue
        if not entry.is_dir():
            if entry.name != "robots.txt":
                warnings.append(f"Loose file <code>{html.escape(entry.name)}</code> in the course folder: pages belong in a module or language folder.")
            continue
        if entry.name in (*LANGUAGES, "media"):
            continue
        if not NAME.match(entry.name):
            warnings.append(f"Folder <code>{html.escape(entry.name)}</code>: use lowercase letters, numbers and - only, or the TMS ignores it.")
            continue
        pages = {l: entry / l / "index.html" for l in LANGUAGES if (entry / l / "index.html").is_file()}
        covered.update(pages.values())
        # Pages that exist but sit deeper than <module>/<lang>/index.html.
        odd = sorted(
            rel(p.parent) + "/" for p in entry.rglob("index.html")
            if not any(part.startswith(".") for part in p.relative_to(entry).parts)
        )[:4]
        first = next(iter(pages.values()), None)
        modules.append({"key": entry.name, "pages": pages, "title": title_of(first) if first else None, "odd": odd})

    other = sorted(
        p for p in course.rglob("index.html")
        if p not in covered and not any(part.startswith(".") for part in p.relative_to(course).parts)
    )
    return {"overview": overview, "modules": modules, "other": other, "warnings": warnings, "size": size_of(course)}


def root_warnings() -> list[str]:
    out = []
    for e in sorted(ROOT.iterdir()):
        if e.name.startswith(".") or e.name in ROOT_FILES_OK:
            continue
        if e.is_dir() and not NAME.match(e.name):
            out.append(f"Folder <code>{html.escape(e.name)}</code> in the main folder: course folders use lowercase letters, numbers and - only.")
        elif not e.is_dir():
            out.append(f"Loose file <code>{html.escape(e.name)}</code> in the main folder: files belong inside a course folder.")
    return out


def lang_cell(pages: dict, lang: str) -> str:
    if lang not in pages:
        return '<td class="muted">—</td>'
    p = pages[lang]
    return f'<td><a class="pill" href="{html.escape(rel(p))}" title="{html.escape(title_of(p) or "")}">{lang.upper()}</a></td>'


def render(courses: dict, top_warnings: list[str]) -> str:
    sections = []
    for name, c in courses.items():
        total, media, count = c["size"]
        warns = list(c["warnings"])
        rows = []
        for m in c["modules"]:
            if m["pages"]:
                status = '<td class="ok">yes</td>'
            elif m["odd"]:
                status = '<td class="warn">no — pages are one level too deep</td>'
                warns.append(
                    f"Module <code>{html.escape(m['key'])}</code> has no <code>nl/index.html</code> (or fr / en) directly inside, "
                    f"so it can't be picked on a training page. Found: {', '.join(f'<code>{html.escape(o)}</code>' for o in m['odd'])}."
                )
            else:
                status = '<td class="warn">no — no pages</td>'
                warns.append(f"Module folder <code>{html.escape(m['key'])}</code> has no pages (no index.html anywhere inside).")
            rows.append(
                f'<tr><td><code>{html.escape(m["key"])}</code></td><td>{html.escape(m["title"] or "")}</td>'
                + "".join(lang_cell(m["pages"], l) for l in LANGUAGES) + status + "</tr>"
            )

        overview = " ".join(
            f'<a class="pill" href="{html.escape(rel(p))}">{l.upper()}</a>' for l, p in c["overview"].items()
        ) or '<span class="warn">missing</span>'
        other = "".join(
            f'<li><a href="{html.escape(rel(p))}">{html.escape(rel(p.parent))}/</a> '
            f'<span class="muted">{html.escape(title_of(p) or "")}</span></li>'
            for p in c["other"]
        )
        warn_html = (
            '<div class="warnbox"><strong>Needs attention</strong><ul>'
            + "".join(f"<li>{w}</li>" for w in warns) + "</ul></div>"
        ) if warns else ""
        sections.append(f"""
<section class="course" id="{html.escape(name)}">
  <header>
    <h2>{html.escape(name)}</h2>
    <p class="muted">{len(c['modules'])} modules · {mb(total)} · {count} audio/video files ({mb(media)})</p>
  </header>
  {warn_html}
  <p><strong>Course overview:</strong> {overview}</p>
  <table>
    <thead><tr><th>Module folder</th><th>Title (as shown in the TMS)</th><th>NL</th><th>FR</th><th>EN</th><th>Can be picked on a training page</th></tr></thead>
    <tbody>{''.join(rows) or '<tr><td colspan="6" class="muted">No modules yet.</td></tr>'}</tbody>
  </table>
  {f'<details><summary>Other pages inside modules ({len(c["other"])})</summary><ul>{other}</ul></details>' if other else ''}
</section>""")

    toc = " ".join(f'<a class="pill" href="#{html.escape(n)}">{html.escape(n)}</a>' for n in courses)
    top = (
        '<div class="warnbox"><strong>Main folder</strong><ul>'
        + "".join(f"<li>{w}</li>" for w in top_warnings) + "</ul></div>"
    ) if top_warnings else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>E-learning courses</title>
<style>
:root{{--bg:#f3f4f6;--card:#fff;--text:#111827;--muted:#6b7280;--line:#e5e7eb;--accent:#4f46e5;--ok:#047857;--warn:#b45309;--warnbg:#fffbeb;--warnline:#fcd34d}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111827;--card:#1f2937;--text:#f9fafb;--muted:#9ca3af;--line:#374151;--accent:#a5b4fc;--ok:#6ee7b7;--warn:#fcd34d;--warnbg:#2a2412;--warnline:#92400e}}}}
*{{box-sizing:border-box}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--text);font:15px/1.5 ui-sans-serif,system-ui,sans-serif}}
main{{max-width:1100px;margin:0 auto}}
h1{{margin:0 0 4px}} h2{{margin:0;font-size:20px}}
a{{color:var(--accent)}} .muted{{color:var(--muted)}} .ok{{color:var(--ok);font-weight:600}} .warn{{color:var(--warn);font-weight:600}}
.course{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:20px;margin-top:20px;overflow-x:auto}}
.course header{{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:8px}}
.pill{{display:inline-block;padding:1px 10px;border:1px solid var(--accent);border-radius:999px;text-decoration:none;font-weight:600;font-size:13px;margin:2px 0}}
.warnbox{{background:var(--warnbg);border:1px solid var(--warnline);border-radius:8px;padding:10px 14px;margin:12px 0}}
.warnbox ul{{margin:6px 0 0}}
table{{width:100%;border-collapse:collapse;margin-top:8px;font-size:14px}}
th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}}
details{{margin-top:12px}} summary{{cursor:pointer;font-weight:600}} ul{{padding-left:20px}}
</style>
</head>
<body>
<main>
<h1>E-learning courses</h1>
<p class="muted">Overview of this repository: every course, its modules and languages, with a link to each page.
Built automatically by <code>.claude/build-index.py</code> — don't edit by hand. See <code>README.md</code> for where things go.</p>
<p>{toc}</p>
{top}
{''.join(sections) or '<p>No courses yet.</p>'}
</main>
</body>
</html>
"""


def main() -> None:
    courses = {
        d.name: scan(d)
        for d in sorted(ROOT.iterdir())
        if d.is_dir() and not d.is_symlink() and NAME.match(d.name)
    }
    top = root_warnings()
    (ROOT / "index.html").write_text(render(courses, top), encoding="utf-8")
    n_warn = len(top) + sum(
        len(c["warnings"]) + sum(1 for m in c["modules"] if not m["pages"]) for c in courses.values()
    )
    print(f"index.html: {len(courses)} course(s) ({', '.join(courses) or '-'}), {n_warn} warning(s)")


if __name__ == "__main__":
    main()

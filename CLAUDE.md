# CLAUDE.md — dpi-online-course

E-learning courses for the DPI Training Management System (TMS). This repo is a
git submodule of the TMS (at `e-learning/`); the TMS serves these files to
participants on the student portal (`app/Services/ELearningCourses.php`,
`app/Http/Controllers/Portal/ELearningController.php` in the TMS repo).

## Who you are working with

The person editing this repo is usually **not a developer**. Talk in plain
language, no jargon ("module folder", "page", "language" — not "path",
"slug", "submodule"). Do the technical parts for them, and **keep the
structure below intact**: if they ask for something that breaks it (a file
in the wrong place, a new folder at the root, a renamed module), explain why
in one sentence and do it the right way instead. `README.md` is their guide —
keep it correct when conventions change.

## Structure (what the TMS expects — don't deviate)

Order is always **course → module → language** (never language → module):
the TMS resolves `<module>/<lang>/index.html` with language fallback, and
`portal-select.js` matches overview links `../<module>/<lang>/`. Call it
"module" towards the user (that's what the pages say).

```
<course>/                              one e-learning per top-level folder
  nl/index.html  fr/index.html  en/index.html     course overview per language
  <module>/<lang>/index.html                      one module, one language
  <module>/<lang>/<sub>/index.html                deeper pages (parts, challenges)
  media/                                          audio / video (+ media/manifests/*.json)
  robots.txt                                      "User-agent: *  Disallow: /"
```

- **Course** = every top-level folder matching `^[a-z0-9-]+$`. Each one shows
  up as a course in the TMS — **never create other folders at the root**
  (no `scripts/`, `docs/`, `old/`, `tmp/`). Helpers go in `.claude/`.
- Dot-files / dot-folders and root-level files are never served and never a course.
- **Languages:** `nl`, `fr`, `en` only (TMS falls back nl → fr → en).
- **Overview** = `<course>/<lang>/index.html`. The portal opens this; a course
  without one is broken.
- **Module** = `<course>/<module>/<lang>/index.html` directly. Only these are
  selectable as an e-learning block on a TMS training page. Pages nested deeper
  (`handhaving/nl/deel1/`) are reachable but not selectable — when adding a
  module, always give it a `<lang>/index.html`.
- `media` and the language folders are never modules.
- **Module title** = `<title>` within the first 4 KB of the page; it is the
  name in the TMS block picker. Format: `Module N · <name>`.
- **Don't rename or move existing module / course folders** without telling
  the user: TMS training pages and blocks reference them by name (a renamed
  module shows as "missing" in the TMS).

## Pages

- New pages: copy an existing page of the same kind (overview or module) from
  `dpo/` and change the content — never write a page from scratch.
- Links relative only (`../nl/`, `../beginselen/nl/`, `../../media/…`). No
  absolute `/…` URLs, no `%`-encoding, no `..` beyond the course folder: the
  TMS serves a course under a signed prefix and refuses those.
- Every page keeps `<meta name="robots" content="noindex, nofollow">`.
- Keep the template the TMS theme hooks into (it injects
  `resources/e-learning/portal-theme.css` + `portal-select.js`):
  - colours / fonts only via the CSS custom properties (`--font`, `--page-bg`,
    `--card-bg`, `--text`, `--title`, `--muted`, `--accent`, `--line`,
    `--header-*`, `--title-*`, `--btn-*`, `--radius`, `--shadow`, …);
  - `header.top` with `.logo`, `.modlabel`, `nav.main` buttons (`#nav-overview`, …);
  - overview: modules in `<details class="grp">` groups with
    `<li><a href="../<module>/<lang>/">` links (used to open a module from a TMS block);
  - `.card`, `.btn`, `.hero`.
- After adding a module, link it from that course's overview page in every
  language it exists in.
- No secrets or personal data anywhere — every participant with access can
  read every file in the course.

## Media

- `<course>/media/<set>/…` (mp3 / mp4). Replacing a file: same name, same place.
- The repo is ~1.2 GB and the TMS downloads it on every deploy: keep media
  compressed, don't commit unused renders. Served types: html, css, js, mjs,
  json, txt, vtt, png, jpg, gif, webp, avif, svg, ico, mp3, m4a, ogg, wav,
  mp4, webm, pdf, woff, woff2, ttf, otf (anything else downloads).

## After every change

1. Run `python3 .claude/build-index.py` — rebuilds `index.html` (the overview
   the user opens in the browser). Never edit `index.html` by hand.
2. Check its output for warnings (orange in `index.html`) and fix them or tell
   the user.
3. Commit + push only when the user asks. Branch: `master`. Remind them that
   the website changes only after the TMS administrator updates the TMS.

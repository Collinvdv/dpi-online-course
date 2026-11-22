# DPI e-learning courses

This repository holds the **e-learning courses** that participants open in the
DPI student portal. Everything you change here ends up on the website for
participants — so the folder structure below matters: if a file is in the
wrong place, the website can't find it.

> **Easiest way to work:** open this folder in Claude Code and describe what
> you want ("add a French version of module 4", "replace the audio of slide 3").
> Claude knows the rules in this file and puts everything in the right place.

---

## 1. See what's there: open `index.html`

Double-click **`index.html`** (in this folder) to open it in your browser. It
shows every course, every module, in which languages it exists, and a link to
each page. Use it to check your work.

- A **green "yes"** in the *Page block* column = the module can be added to a
  training page in the TMS.
- An **orange warning** = something is in the wrong place. Fix it (or ask
  Claude) before publishing.

`index.html` is rebuilt automatically when Claude makes a change. Never edit it
by hand.

---

## 2. The structure

**One folder per e-learning.** Each e-learning (course) has its own folder
here, e.g. `dpo` or `ai-security`. Never put two e-learnings in one folder.

**The order is always: course → module → language.**
So `dpo/beginselen/nl/index.html` = course *dpo*, module *beginselen*, Dutch.
Why not language first? Because then all translations of a module stay
together in one folder: adding, renaming or removing a module is done in one
place, and you can't forget a language.

Inside a course folder:

```
dpo/                          ← the course (one e-learning)
│
├── nl/index.html             ← course overview page, Dutch
├── fr/index.html             ← course overview page, French
├── en/index.html             ← course overview page, English
│
├── beginselen/               ← a module (one folder per module)
│   ├── nl/index.html         ←   the module in Dutch
│   ├── fr/index.html         ←   the module in French
│   └── en/index.html         ←   the module in English
│
├── rollen/                   ← another module, same structure
│   ├── nl/index.html
│   └── ...
│
└── media/                    ← audio and video used by the pages
    ├── les8-nl/slide-01.mp4
    └── ...
```

### The rules

| Rule | Example ✅ | Wrong ❌ |
|---|---|---|
| Folder names: lowercase letters, numbers and `-` only | `ai-security` | `AI Security`, `ai_security`, `Module4` |
| Languages are always `nl`, `fr` or `en` | `beginselen/fr/index.html` | `beginselen/FR/…`, `beginselen/frans/…` |
| Each page is called `index.html` inside its language folder | `rollen/en/index.html` | `rollen/rollen-en.html` |
| A module page sits **directly** in its language folder | `rollen/nl/index.html` | `rollen/nl/part1/index.html` only |
| Audio and video go in the course's `media` folder | `dpo/media/…` | next to the page, or in the main folder |
| Nothing extra in the main folder | – | a `docs/` or `old/` folder next to `dpo/` |

**Why the last rule?** Every folder in the main folder appears in the website
as a separate e-learning. A stray `old/` folder becomes a broken course.

### The page title

The text between `<title>` and `</title>` at the top of a page is the name
staff see when they pick the module in the TMS. Keep it short and consistent:
`Module 4 · De basisprincipes van de verwerking`.

---

## 3. Common tasks

**Change text on a page** — open the page's `index.html` and change the text.
Do this in every language that needs it.

**Add a language to a module** — copy the module's `nl` folder, rename the copy
to `fr` or `en`, translate the text and the `<title>`.

**Add a new module** — make a new folder in the course (e.g. `dpo/nieuwe-module/`),
with an `nl/index.html` (and `fr` / `en` if needed). Copy an existing module
as a starting point, so it keeps the same look. Then add a link to it on the
course overview pages (`dpo/nl/index.html`, …).

**Add a new e-learning** — make a new folder in the main folder (e.g. `nis2`),
with `nl/index.html` as the overview and modules inside it, same structure as
`dpo`. Copy from `dpo` so it gets the portal look. Then ask the TMS
administrator to link it to the right training.

**Replace audio or video** — put the new file in the course's `media` folder
with **the same file name** as the old one. Keep files small (compressed mp3 /
mp4): everything here is downloaded on every website update.

---

## 4. Don'ts

- Don't change the look (colours, fonts, the header with buttons). The website
  applies the portal look automatically, and that only works when pages keep
  the same building blocks as the existing ones.
- Don't rename or move existing module folders: training pages in the TMS
  point to them by name. Ask the TMS administrator first.
- Don't put passwords, personal data or internal notes in any file — every
  participant can read everything in a course.
- Don't use other languages than `nl`, `fr`, `en`.

---

## 5. Publishing

1. Check your work in `index.html` (no orange warnings).
2. Save your changes to GitHub (commit + push — Claude can do this for you).
3. Tell the TMS administrator. Changes go live on the website only after they
   update the TMS — your push alone doesn't change the website yet.

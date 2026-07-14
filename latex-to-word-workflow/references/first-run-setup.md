# First-run setup

Use only when the environment has not been verified. Do not use a full manuscript as the first test.

## 1. Output modes

- **Zotero live:** citations stay as Zotero fields (refresh, restyle, bibliography in Word). Prefer when authors keep editing Word.
- **Static CSL:** plain formatted text. Prefer for previews, fixed deliverables, or no Zotero/BBT.

Ask which mode is needed only if unclear. Live mode needs more first-time setup.

## 2. Detect environment

Check before proposing installs:

| Component | How to think about it |
|---|---|
| Pandoc 3+ | `pandoc -v` |
| Python + deps | `pip install -r requirements.txt` (`python-docx`, `lxml`) |
| LaTeX/BibTeX | Prefer `latexmk` available |
| Microsoft Word | Installed and usable by the **user** (agent does not drive Word UI) |
| Live only | Zotero desktop, Word add-in (**user** confirms Zotero tab), Better BibTeX, current official `zotero.lua` |

Report installed / missing / needs user confirmation. Do not claim the Word add-in works only because files exist—ask the user whether the **Zotero** tab appears. Install software only after user confirmation.

Official filter only:

`https://retorque.re/zotero-better-bibtex/exporting/zotero.lua`

## 3. Zotero + Better BibTeX (live mode)

1. Start Zotero; ensure Better BibTeX is enabled.
2. Confirm Word shows the Zotero tab (reinstall add-in from Zotero Cite settings if missing; restart Word).
3. If localhost API calls fail under a system proxy, set `NO_PROXY=*` / `no_proxy=*` for that shell only.
4. Smoke the API with a **real** library item (never invent keys):

```text
python scripts/test_better_bibtex.py "realCitationKeyOrTitle"
```

A response from `http://127.0.0.1:23119/better-bibtex/json-rpc` means BBT is reachable. HTTP 404 usually means BBT missing/disabled.

## 4. Word reference template

If the project has no approved template, **copy** `assets/reference.docx` to a project path. Do not treat the bundled file as the working template.

Ask the user to open the copy and accept (or edit) at least: page size/margins; Title/Subtitle/Heading 1–3; Normal/Body Text; Figure (no first-line indent); Caption; Table Body; Bibliography hanging indent.

Defaults are **A4 + Times New Roman**. US Letter or CJK body fonts need a project-specific template.

Zotero CSL controls citation punctuation and reference **content**; the Word template controls page layout and paragraph look. Continue only after the user accepts the template or explicitly accepts bundled defaults.

## 5. One-citation smoke test

Use `examples/minimal/` or equivalent. For live mode, replace `exampleCitation2025` with a real BBT key and matching `.bib` entry.

Build the requested mode with the approved template. Live: `zotero.lua` without `--citeproc`. Keep test outputs separate from manuscript outputs.

Example (paths relative to the skill root; adjust as needed):

```text
# Static — provide any journal CSL (e.g. from https://github.com/citation-style-language/styles)
pandoc examples/minimal/main.tex -f latex -t docx --wrap=none --citeproc --bibliography=examples/minimal/references.bib --csl=path/to/journal.csl --reference-doc=assets/reference.docx -o examples/minimal/output/minimal_static.docx

python scripts/format_generated_docx.py examples/minimal/output/minimal_static.docx
python scripts/promote_native_crossrefs.py examples/minimal/output/minimal_static.docx examples/minimal/output/minimal_static_native.docx --tex examples/minimal/main.tex
python scripts/check_cross_references.py --tex examples/minimal/main.tex --docx examples/minimal/output/minimal_static_native.docx --require-native-word-fields
python scripts/validate_docx.py examples/minimal/output/minimal_static_native.docx --tex examples/minimal/main.tex
```

If the user asks for a Windows COM open check: `powershell -File scripts/validate_with_word.ps1 -Path examples/minimal/output/minimal_static_native.docx`.

Or use `examples/minimal/build.ps1` with `-Csl` / `-ZoteroLua` (ZoteroLive asserts `--expect-zotero 1`).

## 6. Split validation (agent vs user)

**Agent (scripts by default):** LaTeX clean; `validate_docx.py --tex ...` (enforces table/image counts; live mode also `--expect-zotero N`); `check_cross_references.py --require-native-word-fields` (including native REF target bookmarks). Do **not** automate Zotero clicks.

**Word COM (optional):** mention `scripts/validate_with_word.ps1` as a Windows open-without-repair probe. Run it only if the **user asks** and desktop Word is available.

**User (in Word):** open without repair; live mode: Document Preferences (set style) **OK before** bulk Refresh, then Add/Edit Bibliography; Select All → F9; visual styles and PDF spot-check. If the first live open claims corruption, rebuild the DOCX once (known intermittent issue).

Do not proceed to the full manuscript until the **user** accepts the smoke-test DOCX. If scripts fail, fix and rebuild the minimal test; if Word looks wrong, fix build inputs/template and rebuild—still let the user re-check.

## 7. Hand off

Record approved `reference.docx` and `zotero.lua` paths in the project build script/config. Routine:

`audit keys → compile LaTeX → Pandoc → format styles → promote native cross-refs → script checks → user Word acceptance`

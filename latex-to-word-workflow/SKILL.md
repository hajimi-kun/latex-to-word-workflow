---
name: latex-to-word-workflow
description: This skill should be used when converting a LaTeX manuscript to polished editable DOCX (figures, equations, tables, native Word SEQ/REF cross-references, custom styles, static CSL or live Zotero citations), or when the user asks for Pandoc DOCX builds, Better BibTeX/zotero.lua integration, reference-doc templates, or DOCX validation.
version: 2.0.0
---

# LaTeX → Word (Zotero optional)

## Resources

| Path | Role |
|---|---|
| `assets/reference.docx` | Generic A4 template (copy into the project; do not edit the asset) |
| `scripts/*.py` | Audit, style map, native cross-refs, package checks |
| `scripts/validate_with_word.ps1` | Optional Windows COM open probe — only if the user asks |
| `examples/minimal/` | Smoke-test manuscript |
| `references/first-run-setup.md` | Environment, template, smoke test |
| `references/cross-references.md` | SEQ/REF promote, numbering limits |
| `references/ecosystem-notes.md` | Related GitHub tools (load only when extending) |
| `requirements.txt` | `python-docx`, `lxml` |

## Modes (pick one)

- **Zotero live:** Pandoc + official `zotero.lua` only — never `--citeproc`. User finishes in Word (prefs → Refresh → bibliography).
- **Static CSL:** `--citeproc --bibliography --csl`.

Never combine `--citeproc` with `zotero.lua`.

## Platform

| Capability | Notes |
|---|---|
| Agent build + package checks | Pandoc 3+, Python + `requirements.txt`, LaTeX/BibTeX — any OS |
| Word / Zotero UI | **User** opens DOCX by default (F9, Zotero Refresh, visual check) |
| Word COM | **Optional.** Mention it; run `validate_with_word.ps1` only if the user asks and Windows Word is available |
| Live Zotero at build | Zotero + BBT; filter: https://retorque.re/zotero-better-bibtex/exporting/zotero.lua |
| Local BBT API | `http://127.0.0.1:23119/better-bibtex/json-rpc` (set `NO_PROXY=*` only if proxy breaks localhost) |

If setup is unknown, finish `references/first-run-setup.md` first. Detect before install; confirm with user.

## Routine pipeline

1. **Preflight sources**
   - Complete entry point (all `\input`/`\include`); prefer labels `fig:` / `tab:` / `eq:`.
   - **Figures:** Word cannot embed PDF. Change `\includegraphics` to PNG/JPEG **before** Pandoc. A same-stem `.png` next to `figure.pdf` is **not** used automatically. Treat image-conversion warnings as failures.
   - Prefer labels on every numbered float/equation you will cross-ref. Promoter uses LaTeX counter order (unlabeled numbered objects still advance numbers).
   - Audit keys:

```text
python scripts/check_citation_keys.py --tex main.tex --bib references.bib --skip-zotero
python scripts/check_citation_keys.py --tex main.tex --bib references.bib
```

   Pass every file with `\cite`. PowerShell: expand globs before Python.

2. **Compile LaTeX** + BibTeX; stop on errors.

3. **Pandoc** on the complete entry. Set `--resource-path` to real image dirs (e.g. `.;figures`). Distinct outputs per mode.

```text
# Static
pandoc main.tex -f latex -t docx --wrap=none --citeproc --bibliography=references.bib --csl=journal.csl --metadata reference-section-title=References --resource-path=.;figures --reference-doc=reference.docx -o out/static.docx

# Zotero live (no --citeproc). Optional: --metadata zotero_csl_style=apa
pandoc main.tex -f latex -t docx --wrap=none --lua-filter=zotero.lua --resource-path=.;figures --reference-doc=reference.docx -o out/zotero_live.docx
```

Do **not** use `pandoc-crossref` as a substitute for this skill’s native SEQ/REF promote when the goal is editable Word renumbering.

4. **Styles → native cross-refs** (once per rebuild):

```text
python scripts/format_generated_docx.py out/doc.docx
python scripts/promote_native_crossrefs.py out/doc.docx out/doc_native.docx --tex main.tex
```

Default caption text: English `Fig.` / `Table` / `Eq.`.

5. **Agent package checks** (no Word UI unless the user asked for COM):

```text
python scripts/validate_docx.py out/doc_native.docx --tex main.tex --expect-zotero N
python scripts/check_cross_references.py --tex main.tex --docx out/doc_native.docx --require-native-word-fields
```

- `N` = live citation field count; omit `--expect-zotero` for static CSL. Optional: `--expect-zotero-keys key1 key2` to require those BBT keys inside field JSON.
- With `--tex`, source table/image counts are **enforced** against the DOCX (use `--no-enforce-tex-counts` only to diagnose). Explicit `.pdf` includes fail unless `--allow-pdf-figures`.
- REF targets must exist as bookmarks; duplicate bookmark names fail.
- Fails on unresolved `[@...]`. Report pass/fail; not delivery-ready until step 6.

6. **User acceptance in Word** — give the DOCX path; ask the user to:

- Open (no repair dialog). If Word claims corruption on first live open, rebuild once.
- **Live mode:** Document Preferences (set style) **OK before** bulk **Refresh**, then **Add/Edit Bibliography**.
- Select All → **F9**.
- Spot-check equations, figures, captions, tables, cites, bibliography, breaks vs PDF.

If the **user asks** for an automated open check on Windows:

```text
powershell -File scripts/validate_with_word.ps1 -Path out/doc_native.docx
```

Do not run COM by default; do not automate Zotero clicks.

## Style mapping

| Content | Style |
|---|---|
| Prose | `Body Text` |
| Image-only para | `Figure` |
| Captions | `Caption` |
| Table cells | `Table Body` |
| Reference list | `Bibliography` |

Map styles only; do not rewrite Zotero field runs. Headings: `References`, `Bibliography`, `参考文献`, `引用文献`.

## Hard rules

- New DOCX package only; never splice XML without relationships.
- Canonical BBT keys; never invent keys; resolve by DOI/title.
- Cross-file refs → full entry; audit after style postprocess.
- Missing/PDF-only figures → fix before accepting build.

## Boundaries

- Live Zotero needs BBT at build; static does not.
- Do not stack promotes; rebuild from Pandoc.
- Equation promote needs `--tex` and matching display-math vs OMML counts.
- Numbers come from LaTeX env order (`figure`/`table`/`equation`/…, not starred; multi-line `align` rows). Unlabeled numbered equations still advance the counter so a later labeled eq is Eq. (2). Compare complex layouts to PDF.
- Caption promote requires Caption style or Fig./Table/图/表 prefix near the bookmark.
- `\setcounter` may be ignored; link integrity ≠ PDF numbering.
- Agent checks are structural; final acceptance is user-in-Word (COM only on request).
- Bib audit is simple; complex `.bib` may need manual review.

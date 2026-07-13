---
name: latex-to-word-workflow
description: Convert a LaTeX manuscript into polished editable DOCX with figures, equations, tables, custom Word styles, and either static CSL references or native Zotero live citation fields. Use for LaTeX-to-Word builds, Pandoc DOCX conversion, Better BibTeX/zotero.lua integration, Zotero-refreshable Word citations and bibliographies, reference-doc templates, or DOCX validation.
---

# LaTeX to polished Word with Zotero

## Bundled resources

- `assets/reference.docx`: generic A4 Word style template with visible samples.
- `scripts/test_better_bibtex.py`: test local Better BibTeX and search Zotero items.
- `scripts/check_citation_keys.py`: audit `\cite{...}` against BibTeX and Better BibTeX.
- `scripts/format_generated_docx.py`: map figures, captions, tables, and bibliography to Word styles.
- `scripts/validate_docx.py`: validate DOCX relationships, counts, and Zotero fields.
- `scripts/validate_with_word.ps1`: verify Microsoft Word opens without repair.
- `examples/minimal/`: small static/live build example. Replace its dummy citation before Zotero-live use.
- `references/first-run-setup.md`: first-time environment, template, Zotero, and smoke-test setup.

## First-run onboarding

Before converting a full manuscript, determine whether the environment has completed this workflow's initial setup. Treat it as unconfigured if any of these is unknown:

- Pandoc, Python with `python-docx`, LaTeX/BibTeX, or Microsoft Word availability.
- The location and author approval of the project's Word reference template.
- For Zotero-live output: Zotero, its Word plugin, Better BibTeX, or the official `zotero.lua` filter.
- Whether a one-citation Zotero-live DOCX has passed Word and Zotero validation.

For an unconfigured environment, read `references/first-run-setup.md` completely and finish its setup and smoke test before building the full manuscript. Detect existing components first, report installed and missing items plainly, and obtain user confirmation before installing software or plugins.

For a configured environment, use the routine path directly: audit citation keys → compile LaTeX → build DOCX → map Word styles → validate → refresh citations and add the bibliography in Word.

## Choose the citation mode

- **Zotero live (preferred for author editing):** create native `ADDIN ZOTERO_ITEM CSL_CITATION` fields with Better BibTeX's official `zotero.lua`. In Word, use Zotero `Refresh`, `Document Preferences`, and `Add/Edit Bibliography`.
- **Static CSL (fallback/preview):** use Pandoc `--citeproc --bibliography --csl`. Citations and references are editable text, not Zotero fields.

Never combine `--citeproc` with `zotero.lua` in the same build.

## Required configuration

Common:

- Pandoc 3+, LaTeX/BibTeX, Python with `python-docx`, and Microsoft Word on Windows.
- A complete LaTeX entry point and all image directories in `--resource-path`.
- A style-focused `reference.docx` for page layout, fonts, headings, captions, tables, and bibliography appearance.
- An output directory for generated DOCX files.

Zotero live:

- Zotero desktop running with the Word plugin and Better BibTeX enabled.
- Download the official current filter from `https://retorque.re/zotero-better-bibtex/exporting/zotero.lua`.
- Make the Better BibTeX citation key canonical across Zotero, `references.bib`, and every `\cite{key}`.
- Confirm the local API at `http://127.0.0.1:23119/better-bibtex/json-rpc`. Bypass proxies for localhost (`NO_PROXY=*`); a 404 usually means Better BibTeX is absent or disabled.

## Preflight

1. Inspect the LaTeX entry point, bibliography, figures, template, and output path.
2. Compile LaTeX with BibTeX and stop on errors:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

3. Confirm every cited key exists in `references.bib`.
4. For Zotero live, query Better BibTeX and resolve every key before conversion. Match by DOI/title and reject missing or ambiguous results; never guess a key.
5. Verify Word can open the reference DOCX with `Documents.OpenNoRepairDialog`.

Use the bundled checks when available:

```powershell
python scripts/test_better_bibtex.py "citationKeyOrTitle"
python scripts/check_citation_keys.py --tex main.tex section*.tex --bib references.bib
```

## Build Zotero-live DOCX

Do not use `--citeproc` here:

```powershell
$env:NO_PROXY = "*"
$env:no_proxy = "*"

pandoc main.tex `
  -f latex `
  -t docx `
  --wrap=none `
  --lua-filter="path\to\zotero.lua" `
  "--resource-path=.;..;..\figures" `
  --reference-doc="path\to\reference.docx" `
  -o "output\manuscript_zotero_live.docx"
```

The filter creates live citation fields but does not normally add the bibliography field. Open the output in Word, select the journal style under Zotero `Document Preferences`, click `Refresh`, place the cursor under `References`, then click `Add/Edit Bibliography`.

## Build static CSL DOCX

Use this when Zotero/Better BibTeX is unavailable or for deterministic preview:

```powershell
pandoc main.tex `
  -f latex `
  -t docx `
  --wrap=none `
  --citeproc `
  --bibliography="references.bib" `
  --csl="path\to\journal.csl" `
  --metadata "reference-section-title=References" `
  "--resource-path=.;..;..\figures" `
  --reference-doc="path\to\reference.docx" `
  -o "output\manuscript_static.docx"
```

## Word template and style mapping

Let `reference.docx` define appearance; let a postprocessor assign semantic styles without rewriting text:

| Content | Word style |
|---|---|
| Manuscript prose | `Body Text` |
| Image-only paragraph | `Figure` (centered, zero first-line indent) |
| Figure/table caption | `Caption` |
| Table cell text | `Table Body` |
| References | `Bibliography` (hanging indent) |
| Sections | `Heading 1/2/3` |

Use `python-docx` only to change paragraph/run styles, page settings, and image dimensions. Do not replace paragraph text containing citation fields. A template defines the styles, but Pandoc may not assign custom `Figure` or `Table Body` styles; map them after conversion.

```powershell
python scripts/format_generated_docx.py output.docx
```

## DOCX integrity rules

- Generate a complete new DOCX. Never splice raw paragraphs into an existing DOCX XML package.
- Never copy XML nodes without their relationships; hyperlink/media relationship loss can make Word report corruption.
- Migrate citation keys only after one-to-one Zotero matching; update both `references.bib` entry keys and all `\cite{...}` uses, then recompile LaTeX.
- Use distinct filenames when producing both Zotero-live and static CSL variants.

## Validation gate

Accept an output only after all applicable checks pass:

1. LaTeX/BibTeX compiles with no undefined citations.
2. DOCX ZIP opens and all `r:id`, `r:embed`, and `r:link` references are defined in the corresponding relationship file.
3. `python-docx` confirms expected paragraphs, tables, and image count. Do not use its plain-text output to judge Word equations.
4. Zotero-live XML contains the expected count of `ADDIN ZOTERO_ITEM CSL_CITATION` and the expected Zotero item keys.
5. Microsoft Word `Documents.OpenNoRepairDialog` succeeds. ZIP validity or `python-docx` loading alone is insufficient.
6. In Word, Zotero `Refresh` succeeds and `Add/Edit Bibliography` generates the selected journal style.
7. Visually inspect equations, figure placement, captions, tables, citations, bibliography, page breaks, and cross-references.

```powershell
python scripts/validate_docx.py output.docx --expect-zotero 3
powershell -File scripts/validate_with_word.ps1 -Path output.docx
```

## Known boundaries

- Zotero live fields require Zotero and Better BibTeX at build time; static CSL does not.
- Zotero citations are live, but Pandoc figure/table references are usually static hyperlinks unless a project adds explicit Word fields.
- Word bibliography formatting is controlled by Zotero CSL; paragraph appearance can still inherit the surrounding Word style.

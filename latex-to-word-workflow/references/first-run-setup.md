# First-run setup

Use this guide only when the LaTeX-to-Word environment has not been verified. Complete the steps in order and do not use a full manuscript as the first test.

## 1. Explain the output choices

Tell the user in plain language:

- **Zotero live:** citations remain Zotero fields in Word. The author can refresh them, change the citation style, and generate or update the bibliography. Recommend this mode when the Word file will continue to be edited.
- **Static CSL:** citations and references are ordinary formatted text. Use it for previews, fixed deliverables, or systems without Zotero and Better BibTeX.

Ask which mode is needed only if the intended output is unclear. Zotero live requires more first-time setup.

## 2. Detect the environment

Check before proposing installation:

- Pandoc 3 or newer.
- Python and the `python-docx` package.
- A working LaTeX/BibTeX toolchain, preferably with `latexmk`.
- Microsoft Word on Windows.
- For Zotero live: Zotero desktop, the Zotero Word add-in, Better BibTeX, and a current official `zotero.lua`.

Report the result as installed, missing, or requiring user verification. Do not claim that a Word add-in works merely because its files exist; ask the user to confirm that the **Zotero** tab appears in Word when automation cannot verify the interface. Obtain confirmation before installing software or plugins.

Download the official Better BibTeX filter only from:

`https://retorque.re/zotero-better-bibtex/exporting/zotero.lua`

## 3. Verify Zotero and Better BibTeX

For Zotero-live mode:

1. Start Zotero and confirm that Better BibTeX is enabled.
2. Confirm that Word shows the Zotero tab. If absent, use Zotero's Cite settings to reinstall the Microsoft Word add-in, then restart Word.
3. Bypass proxies for localhost during API checks:

```powershell
$env:NO_PROXY = "*"
$env:no_proxy = "*"
```

4. Test the Better BibTeX API and one real library item:

```powershell
python scripts/test_better_bibtex.py "realCitationKeyOrTitle"
```

Use a real item from the user's Zotero library. Verify its Better BibTeX citation key by title or DOI; never invent or guess a key. A response from `http://127.0.0.1:23119/better-bibtex/json-rpc` confirms the local integration. A 404 usually means Better BibTeX is missing or disabled.

## 4. Prepare the Word reference template

If the project has no approved template, copy `assets/reference.docx` into the project under a clear project-specific name. Do not edit the bundled asset as the user's working template.

Ask the user to open the copied template and inspect its visible samples. Explain that the template controls the base appearance of future DOCX files. Have the user review and save at least:

- page size and margins;
- `Title`, `Subtitle`, and `Heading 1/2/3`;
- `Normal` and `Body Text`;
- `Figure` with no first-line indent;
- `Caption`;
- `Table Body`;
- `Bibliography` with the desired hanging indent.

Explain that Zotero's CSL style controls citation punctuation and reference content, while the Word template controls page layout and paragraph appearance. Continue only after the user accepts the template or explicitly asks to use the bundled defaults.

## 5. Run a one-citation smoke test

Use `examples/minimal/` or an equivalent minimal LaTeX file. Replace `exampleCitation2025` with one real Better BibTeX key and ensure the matching entry is present in the test `.bib` file.

Build the requested mode with the approved Word template. For Zotero live, use `zotero.lua` without `--citeproc`. Keep the test output separate from the manuscript output.

## 6. Validate the test in Word

Do not proceed to the full manuscript until all applicable checks pass:

1. LaTeX compiles without an undefined citation.
2. The DOCX opens through Word `Documents.OpenNoRepairDialog` without a repair warning.
3. The expected native `ADDIN ZOTERO_ITEM CSL_CITATION` field exists in Zotero-live mode.
4. In Word, Zotero `Refresh` succeeds.
5. `Document Preferences` can change the citation style.
6. `Add/Edit Bibliography` generates the bibliography from the test citation.
7. The body, figure, caption, table, and bibliography styles look acceptable.

Use the bundled validators where applicable:

```powershell
python scripts/validate_docx.py test.docx --expect-zotero 1
powershell -File scripts/validate_with_word.ps1 -Path test.docx
```

If a check fails, fix and repeat the minimal test. Do not diagnose setup failures through a full manuscript build.

## 7. Hand off to routine use

After the smoke test passes, record the paths to the approved `reference.docx` and `zotero.lua` in the project's build script or configuration. Then use the routine workflow:

`audit citation keys → compile LaTeX → build DOCX → map Word styles → validate → refresh citations and add the bibliography in Word`

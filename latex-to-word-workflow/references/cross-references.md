# Cross-references: LaTeX → Word

## Complete entry point

Run Pandoc on the full `main.tex` whenever labels and references span files. Isolated section files miss bookmarks.

Compile the same entry with LaTeX/BibTeX first. After DOCX generation (and after style postprocess), audit:

```text
python scripts/check_cross_references.py --tex path/to/main.tex --docx path/to/output.docx --output path/to/crossrefs.json
```

Fails on: duplicate LaTeX labels; `\ref`/`\eqref`/`\autoref`/`\cref`/`\Cref` without labels; missing DOCX bookmarks for referenced labels; fewer static links or total REF+links than LaTeX refs; dangling internal hyperlinks; **native `REF` targets that are not bookmark names**; **duplicate DOCX bookmark names**; visible `[fig:…]` / `[tab:…]` / `[sec:…]` / `[eq:…]` or `Error! Reference source not found.`.

## Native Word fields

Pandoc usually emits static bookmarks + hyperlinks. Equation refs may remain `[eq:label]` without bookmarks. For editable Word, **after** `format_generated_docx.py`:

```text
python scripts/promote_native_crossrefs.py input.docx output_native.docx --tex main.tex
```

| Object | Caption/number | Cross-ref |
|---|---|---|
| Figure | `SEQ Fig. \* ARABIC` | `REF RefNativeFigNNN \h` |
| Table | `SEQ Table \* ARABIC` | `REF RefNativeTableNNN \h` |
| Labeled display equation | `SEQ Equation \* ARABIC` | `REF RefNativeEquationNNN \h` |

Bookmarks wrap **only the number**. Prefixes (`Fig. `, `Table `, `Eq. (`), punctuation, and panel suffixes (`a--c`) stay plain text.

**Defaults are English `Fig.` / `Table` / equation parentheses.** Chinese「图」「表」or `Figure`/chapter-numbered schemes need a project-specific promoter or manual template policy—do not claim native renumbering if only static links remain.

Numbering follows LaTeX counters from the complete entry: non-starred `figure`/`table`/`equation`/`align`/… advance; starred envs and `\[…\]` do not. A numbered equation **without** `\label` still advances the counter so a later labeled equation is Eq. (2). Multi-line `align` rows each take a number (except `\notag`/`\nonumber`). Caption insertion requires Caption style or a Fig./Table/图/表-prefixed paragraph.

Final editable deliverable:

```text
python scripts/check_cross_references.py --tex main.tex --docx output_native.docx --require-native-word-fields
```

Do not re-run promote on the same DOCX; rebuild Pandoc → styles → promote once → validate.

Treat Pandoc image-conversion warnings as build failures (missing art can drop captions).

## Numbering boundaries

Pandoc may ignore `\setcounter` and similar. A truncated manuscript can be internally consistent yet disagree with the full PDF. The audit checks **link integrity**, not semantic parity with a separate numbering scheme.

Prefer a structurally complete entry point. If sections are intentionally omitted, document and test an explicit numbering policy.

## Equations

LaTeX math generally becomes editable OMML. Visual check is required; `python-docx` plain text is not enough.

Promotion maps complete-entry display-equation order to OMML display paragraphs, adds right-tab `SEQ Equation` numbers (with `\\r N` for LaTeX-consistent values), converts `[eq:…]` links to `REF`. It aborts if Pandoc display-math count ≠ OMML display-paragraph count.

After the agent hands off the DOCX, the **user** should open Word, Select All → F9, and look for broken refs. Keep cross-ref fields separate from Zotero citation fields; scripts can verify Zotero field **count** is unchanged after promote—the user confirms Refresh still works.

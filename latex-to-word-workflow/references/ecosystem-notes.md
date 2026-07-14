# Related projects and what to borrow

Surveyed GitHub tools for LaTeX→DOCX (2026). Use this when extending the skill; do not load it on every conversion.

## Closest peers

| Project | Approach | Steal / avoid |
|---|---|---|
| [adamsconchallos/tex2docx](https://github.com/adamsconchallos/tex2docx) | Flatten multi-file TeX → Pandoc → patch DOCX; **count figures/tables/footnotes vs source**; PDF figs → PNG sibling; auto `.bib` from `\bibliography` | **Fidelity counts**; PDF figure policy; flatten before Pandoc |
| [jay-dennis/tex2docx](https://github.com/jay-dennis/tex2docx) | TeX prep + Pandoc + pandoc-xnos | Label prefix rules (`fig:`/`tab:`/`eq:`); warn on **commented** `%\label{}` counted wrongly; multi-panel floats weak |
| [tianbaiting/tex2doc](https://github.com/tianbaiting/tex2doc) | Pandoc + ImageMagick/poppler for PDF images | PDF→raster pipeline |
| [scavero/tex2docx](https://github.com/scavero/tex2docx) | Pandoc + TikZ/cover as PDF→PNG; `--reference-doc`, `--number-sections` | Raster hard parts of layout; still not live Zotero |
| [xhan97/Latex2WordExample](https://github.com/xhan97/Latex2WordExample) | `pandoc-crossref` + citeproc + `docx+native_numbering` | Static numbering via filters; **not** native SEQ/REF for author renumbering |
| [lierdakil/pandoc-crossref](https://github.com/lierdakil/pandoc-crossref) (~1k★) | Filter cross-refs (esp. Markdown) | Optional for static previews only; this skill prefers **post-DOCX SEQ/REF promote** for editable Word |
| [retorquere/zotero-better-bibtex](https://github.com/retorquere/zotero-better-bibtex) `zotero.lua` | Live Zotero fields from Pandoc | Official filter; metadata (`csl-style`, `client`, …); first-open Word tips |
| [jyluo1994/zotero-word-citation](https://github.com/jyluo1994/zotero-word-citation) | Codex skill: search → Zotero → Word routes | Multi-path citation strategy; never claim live fields unless produced |
| [KenanHanke/docxwright](https://github.com/KenanHanke/docxwright) | Pure Python, **no Pandoc** | Different stack; limited fidelity |
| [KLGR123/latex2word](https://github.com/KLGR123/latex2word) | EN→CN academic Word + LLM | Different goal (translate), not drop-in |

## This skill’s niche

- **Agent skill** (not only a CLI): mode choice, first-run, user Word acceptance.
- **Live Zotero** via `zotero.lua` **or** static CSL — exclusive.
- **Native Word `SEQ`/`REF`** after style map (editable renumbering), not only pandoc-crossref static text.
- Package audits + cross-ref audit; **no Word COM required** for the agent.

## High-value practices (already or should be in workflow)

1. **PDF figures** — Word cannot embed PDF artwork; use PNG/JPEG sibling (or convert) before Pandoc; treat missing art as failure.
2. **Complete / flattened entry** — Pandoc must see all `\input`/`\include` content for labels and cites.
3. **Fidelity counts** — compare table/figure counts source vs DOCX after convert.
4. **Live Zotero first open** — user opens Document Preferences and confirms style **before** mass Refresh (BBT docs); rare false “corrupt” → rebuild DOCX.
5. **Optional `zotero.lua` metadata** — e.g. `zotero_csl_style` / YAML `zotero.csl-style` to pre-seed style.
6. **Do not combine** `--citeproc` with `zotero.lua`.
7. **Label discipline** — prefer `fig:` / `tab:` / `eq:`; avoid counting commented labels in custom tools.

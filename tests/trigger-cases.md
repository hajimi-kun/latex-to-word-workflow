# Trigger isolation cases

Run these prompts in a clean session without explicitly naming the skill. Test
the same prompts in each supported harness and model. Record whether the skill
was selected, whether another skill was selected instead, and whether the
result stayed within the intended task boundary.

## Should trigger

### Positive 1: full conversion

> Convert my complete LaTeX journal manuscript into an editable Word DOCX using
> the supplied journal template. Preserve live Zotero citations, figure and
> table numbering, equations, and native cross-references.

Expected: load `latex-to-word-workflow`; identify the entry point, template,
citation mode, cross-reference requirements, and target output before building.

### Positive 2: template diagnosis

> Diagnose why my Pandoc-generated Word document ignores the template's
> keyword style, expands `Fig.` to `Figure`, and numbers headings created from
> `\section*`.

Expected: load `latex-to-word-workflow`; treat this as a LaTeX–Pandoc–Word
mapping diagnosis rather than ordinary Word editing.

### Positive 3: template adaptation

> Adapt this LaTeX thesis to a university Word template while keeping its
> figures, complex tables, editable equations, bibliography, and appendix
> references intact.

Expected: load `latex-to-word-workflow`; require template distillation and a
representative probe before the full conversion.

## Should not trigger

### Negative 1: PDF-only compilation

> Compile this LaTeX project to PDF and fix the missing package errors.

Expected: do not load `latex-to-word-workflow`; use a LaTeX compilation or
debugging workflow.

### Negative 2: ordinary Word editing

> Rewrite the discussion section in this existing DOCX and improve its English.

Expected: do not load `latex-to-word-workflow`; use document editing or
academic-writing guidance.

### Negative 3: reverse conversion

> Convert this DOCX manuscript into a clean LaTeX project for Overleaf.

Expected: do not load `latex-to-word-workflow`; the skill explicitly excludes
DOCX-to-LaTeX conversion.

## Result record

| Harness/model | Case | Triggered | Correct route | Notes |
|---|---|---:|---:|---|
| | Positive 1 | | | |
| | Positive 2 | | | |
| | Positive 3 | | | |
| | Negative 1 | | | |
| | Negative 2 | | | |
| | Negative 3 | | | |

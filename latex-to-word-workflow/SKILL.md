---
name: latex-to-word-workflow
description: >
  Load when the user asks to convert an academic LaTeX manuscript, thesis, or
  report into an editable Word DOCX, adapt it to a Word template, preserve
  citations or cross-references, or diagnose a LaTeX-to-Word conversion
  problem. Do not use for PDF-only LaTeX compilation, general Word editing,
  or DOCX-to-LaTeX conversion.
version: 3.0.0
---

# LaTeX to Word

Produce a submission-grade Word candidate from a complete LaTeX project. The
candidate must preserve scientific meaning, use the confirmed target semantics,
remain editable where practical, and include an explicit status for the user-run
Word/Zotero acceptance steps.

## Non-negotiable defaults

- Preserve the original LaTeX, bibliography, figures, and authoritative Word
  target. Work only on generated files or explicit copies.
- Use Pandoc as the initial editable-structure converter. Add source annotations,
  Lua, OpenXML, or supported-adapter Word automation only for an observed bridge
  mismatch.
- For a new project, initialize `examples/bridge-starter/` into the generated
  build directory. Reuse `docx_bridge.py` for fields, bookmarks, styles, and
  DOCX packaging; adapt configuration or `project_adapter.py` instead of
  reimplementing those primitives.
- For every new or changed target, distill the required roles (not unrelated
  template styles) and pass a representative probe before full conversion.
- Treat object packaging and layout as target-owned contract values. Paragraphs,
  tab stops, borderless tables, caption segment sequences, label literals, and
  object order are possible representations, not generic skill defaults.
- When citations exist, Zotero-live fields are mandatory. Run the fixed
  Zotero-live setup and probe in
  `references/conversion-playbook.md#zotero-live-citations`; repair agent-side
  configuration where possible and give the user exact manual steps for the
  remaining Word/Zotero setup.
- Convert every LaTeX cross-reference occurrence to a verified native Word field
  by default. Static references require an informed, recorded user opt-out.
- Treat desktop Microsoft Word as the authoritative environment for fields,
  numbering, layout behavior, and final validation. Word and Zotero actions are
  user-run acceptance steps unless the host explicitly provides a supported
  desktop adapter; never assume GUI, COM, or process access.
- Prioritize: scientific fidelity, content completeness, citation/numbering
  semantics, editability, template structure, visual fidelity, then automation
  cost.

## Capability boundary

- Required for execution: access to the project files and a viable DOCX
  conversion path. If either is absent, provide diagnosis or a handoff plan and
  report the conversion as blocked.
- Optional capabilities include shell or Python execution, LaTeX compilation,
  local application/process detection, Word rendering, GUI automation, and visual
  inspection. Attempt one only when the host explicitly exposes it.
- An unavailable optional capability becomes a user-run gate, not a failed
  conversion. An unobservable capability remains `unknown`; never convert
  `unknown` into an installation or compatibility claim.

## Read routing

| Situation | Required read |
|---|---|
| New, changed, example-only, or ambiguous Word target | `references/template-distillation.md`, then `references/conversion-playbook.md#build-the-semantic-bridge` |
| First build for a project | `examples/bridge-starter/`, then `references/conversion-playbook.md#build-the-semantic-bridge` |
| Zotero, cross-references, equations, captions, complex objects, or diagnosis | Relevant section of `references/conversion-playbook.md` |
| Candidate validation or handoff | `references/conversion-playbook.md#validate-and-hand-off` |
| Other conversion work | Scan this file, then load only the relevant playbook section |

## Required workflow

1. Read the user request and nearest project instructions. Identify the complete
   LaTeX entry point, authoritative Word target, output path, and capabilities
   exposed by the host.
2. Compile the complete LaTeX project when the host exposes the toolchain;
   otherwise request the user's compiled reference or record compilation as a
   pending evidence gate. Inventory included sources, semantic roles, figures,
   tables, equations, citations, labels, reference occurrences, appendices,
   custom macros, and numbering behavior.
3. If citations exist, complete the mandatory Zotero setup and probe before
   expensive manuscript post-processing. Never use the absence of a `zotero`
   CLI alone as evidence that Zotero is unavailable. If live fields cannot be
   generated, stop the citation-bearing build and hand off the exact setup gate.
4. Classify and distill every new or changed Word target into an explicit role
   contract. Do not treat `--reference-doc` as an executable specification.
5. For a new project, run `python scripts/init_bridge.py <build-dir>` and fill
   `bridge_config.json` from the role contract. Keep stable field, bookmark, and
   package operations in the copied `docx_bridge.py`; put only project-specific
   behavior in `project_adapter.py` or the semantic Lua filter.
6. Build the bridge `LaTeX role -> Pandoc output -> target Word representation
   -> method`. Resolve every required role before full conversion.
7. Convert a representative probe covering every high-risk role and transition.
   Inspect actual styles, formatting, fields, bookmarks, lists, and objects.
8. Correct each mismatch at its responsible layer. Start the complete conversion
   only after the probe passes the applicable contract rows.
9. Build the complete candidate and validate source, target-contract, and DOCX
   evidence. Counts are diagnostic; semantic correspondence is the gate.
10. Follow `references/conversion-playbook.md#validate-and-hand-off`. Give the user
   a disposable candidate and exact Word/Zotero acceptance steps. If the user
   returns the refreshed file, re-run the audit and compare pre/post evidence.
11. Deliver the candidate, agent-side evidence, user-refresh status, adaptations,
   unresolved items, and approved exceptions.

## Bundled tools

Use the bundled standard-library scripts when Python 3 is available.
`init_bridge.py` creates generated bridge files only; the manifest and audit
scripts are read-only over source and DOCX inputs.

```text
python scripts/latex_manifest.py <main.tex> --output <source-manifest.json>
python scripts/init_bridge.py <build-dir>
python scripts/docx_audit.py <candidate.docx> \
  --latex-manifest <source-manifest.json> \
  --require-native-crossrefs --require-zotero-fields \
  --output <candidate-audit.json>
python scripts/docx_audit.py <refreshed.docx> \
  --latex-manifest <source-manifest.json> \
  --baseline <candidate-audit.json> \
  --require-native-crossrefs --require-zotero-fields
```

`--require-zotero-fields` checks generated field presence, not that Refresh has
occurred. Scripts provide package and semantic evidence; they cannot replace
user-run Word rendering, field refresh, Zotero refresh, or user confirmation.

## Stop conditions

Do not label the candidate fully verified when a required role is unmapped, a
native field lacks a valid target, a `REF` target contains an entire drawing or
table, the user reports a Word repair warning, live field generation is
unverified, the user refresh/save/reopen gate is pending, or an unresolved
scientific-content mismatch remains. A pending user gate may be delivered as a
clearly labelled candidate; never silently downgrade it.

## Known gotchas

- Imported styles are not evidence that generated content uses them correctly.
  See `references/template-distillation.md#build-the-role-contract`.
- `ensuremath` can turn prose formulae and units into unwanted OMML. See
  `references/conversion-playbook.md#preserve-text-and-math-semantics`.
- A Pandoc bookmark can span a whole object, causing `REF` to reproduce it. See
  `references/conversion-playbook.md#native-word-cross-references`.
- Raw OpenXML and field construction are starter-engine responsibilities, not
  project-adapter code. See `examples/bridge-starter/`.
- Word/Zotero refresh can change fields and document structure. See
  `references/conversion-playbook.md#validate-and-hand-off`.
- Zotero Refresh updates existing Zotero fields; it cannot create fields from
  non-Zotero citation text. See
  `references/conversion-playbook.md#zotero-live-citations`.
- Field update can discard caption-run formatting or expose faulty equation
  packaging or alignment. See
  `references/conversion-playbook.md#word-specific-objects`.
- Equation **container** (e.g. 1×3 borderless table) is not the same as
  **column widths**. Short template demos often use equal thirds; long OMML
  with fractions or `\qquad` secondaries needs a wide math cell or Word
  reflows mid-expression. Probe with a complex display equation. See
  `references/conversion-playbook.md#numbered-equations`.
- PDF, EPS, TikZ, and PGFPlots artwork needs explicit Word-supported output. See
  `references/conversion-playbook.md#high-risk-objects`.

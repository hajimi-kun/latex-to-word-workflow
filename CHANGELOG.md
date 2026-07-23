# Changelog

## 3.0.0 - 2026-07-23

- Document that equation **container type** and **math-cell width** are separate
  contract values: short equal-third demos must not force long OMML reflow.
- Require a complex display-equation probe (fraction + same-number secondary)
  when the manuscript has display math.

## 2.15.0 - 2026-07-23

- Make equation containers, caption component sequences, literal labels, title
  packaging, and object order explicit target-owned role-contract values rather
  than generic layout defaults.
- Document tabbed paragraphs and borderless equation tables as conditional target
  representations, with structure-specific distillation and validation guidance.
- Remove journal-role and English-caption defaults from the bridge starter and
  add regression coverage for template-neutral initialization and non-paragraph
  layout assumptions.

## 2.14.0 - 2026-07-23

- Add a canonical first-build bridge starter with explicit configuration,
  semantic-filter, and project-adapter boundaries.
- Add standard-library DOCX bridge helpers for native fields, tight bookmarks,
  style remaps, and package-preserving writes so project agents do not recreate
  fragile OpenXML primitives.
- Add starter initialization, configuration fail-fast checks, focused unit tests,
  and a workflow behavior case that rejects monolithic converter rewrites.

## 2.13.0 - 2026-07-23

- Make Zotero Refresh, Word field update, save/reopen, and authoritative visual
  confirmation user-run acceptance steps unless the host explicitly exposes a
  supported desktop adapter.
- Add capability-neutral routing: optional shell, process, GUI, COM, rendering,
  and visual capabilities are probed only when exposed, while unobservable
  capabilities remain `unknown` rather than being treated as unavailable.
- Distinguish generated live fields, pending user refresh, user-confirmed but
  unaudited refresh, and independently audited returned files throughout the
  workflow and handoff.
- Rename `--require-zotero-live` to the accurate
  `--require-zotero-fields`, retaining the old spelling as a compatibility alias,
  and add a capability-limited workflow eval case.

## 2.12.0 - 2026-07-22

- Define the primary product as a submission-grade Word candidate and make the
  confirmed Zotero-live, native-cross-reference, new-template-distillation, and
  desktop-Word/user-confirmation defaults explicit and non-negotiable.
- Refactor `SKILL.md` into a lean routing and execution contract; make template
  distillation and the conversion playbook the single authorities for their
  respective details, removing repeated decision, validation, and gotcha prose.
- Add standard-library, read-only LaTeX manifest and DOCX audit scripts. The DOCX
  audit covers all story parts, relationships, applied styles, fields, bookmark
  scope, unresolved markers, and refresh-save-reopen structural deltas.
- Add regression tests for source inventory, Zotero/native field recognition,
  stable pre/post audits, and rejection of whole-object `REF` targets.

## 2.11.0 - 2026-07-22

- Make verified Zotero-live citations the default when local Zotero capability
  is detected and the compatibility probe succeeds; require an explicit static
  requirement or recorded probe failure for static fallback.
- Define desktop Word as the authoritative renderer for Word-specific fields,
  numbering, and template behavior; LibreOffice remains optional and a failed
  headless conversion no longer implies that the GUI application is unavailable.
- Separate prose chemical formulae, units, degrees, and isolated symbols from
  genuine mathematical expressions so `ensuremath` does not force ordinary
  text into OMML.
- Require post-refresh caption field-format verification and true tab/alignment
  semantics with rendered centering checks for numbered equations.
- Add behavior cases covering automatic Zotero probing, prose math leakage,
  caption field formatting, and equation centering.

## 2.10.2 - 2026-07-18

- Require native cross-reference targets to have verified result scope so a
  number-only `REF` cannot reproduce an entire heading, caption, image, or
  table, and call out prefix duplication and list-numbered heading risks.
- Add a Word/Zotero refresh-save-reopen gate with pre/post manifest comparison
  for fields, bookmark ranges, styles, paragraphs, drawings, tables, and
  numbered objects.
- Add behavior cases for over-broad bookmarks and post-refresh structural
  mutation based on the paper1 conversion experiment.

## 2.10.1 - 2026-07-18

- Replace declaration-only required checks with an evidence-driven validation
  loop covering source and candidate manifests, template application, Word
  behavior, failure correction, and handoff evidence.
- Add repository-level trigger and workflow eval cases without expanding the
  installable skill into a general conversion implementation.
- Keep behavior evals versioned in Git but exclude them from release archives;
  move the non-normative Chinese alignment copy to the local workspace outside
  the repository.

## 2.10.0 - 2026-07-17

- Define Word templates as semantic evidence that must be distilled rather than
  executable formatting specifications that Pandoc can infer automatically.
- Add five-layer template distillation for definitions, effective paragraph
  formatting, character formatting, Word objects, and object transitions.
- Require an explicit LaTeX–Pandoc–Word semantic bridge before full conversion
  and verify actual style usage instead of style-definition presence.
- Document common Pandoc DOCX behavior, mismatch classification, caption
  formatting boundaries, unnumbered-heading risk, and transition rules.

## 2.9.0 - 2026-07-17

- Add a non-normative Chinese alignment copy at
  `latex-to-word-workflow-zh_CN/` for internal side-by-side review. It has no
  skill discovery or UI metadata and is excluded from release archives.
- Make representative template probing and explicit LaTeX–Pandoc–Word
  semantic mapping part of the default conversion path.
- Clarify that `--reference-doc` supplies style definitions and defaults but
  does not infer equivalence between differently named styles or create Word
  structures that Pandoc does not emit.
- Add method selection for direct reference styles, working-template aliases or
  output remapping, source annotations/Lua filters, and DOCX/OpenXML or Word
  post-processing.
- Require representative roles and target-only behavior to pass inspection
  before converting the full manuscript.

## 2.8.0 - 2026-07-17

- Recast the skill as a high-freedom, guidance-first workflow rather than a
  bundled LaTeX-to-DOCX application.
- Replace the optional CLI, internal processors, Python dependencies, and
  bootstrap reference DOCX with explicit defaults, decision rules, required
  checks, and project-local adaptation guidance.
- Consolidate three overlapping references into one directly routed playbook
  that stays incremental to `SKILL.md`: detailed template inspection,
  editable-field verification, high-risk object checks, and handoff procedures
  replace repeated core workflow and strategy prose.
- Tighten the trigger description and anti-triggers for conversion, template
  adaptation, preservation requirements, and conversion diagnosis.
- Replace pipeline regression tests with lightweight skill structure and
  behavior-contract checks.
- Make native Word cross-references an opt-out default whenever the LaTeX source
  contains cross-references. Static or mixed downgrade is not automatic and
  requires explicit informed user refusal.
- Archive the complete pre-refactor repository working tree and installed
  v2.7.0 skill before making the breaking change.

## 2.7.0 - 2026-07-17

- Add `prepare-template` as the formal readiness gate for new or changed Word
  templates while retaining the mature-template fast path.
- Report semantic style inheritance, effective first-line indentation,
  representative style usage, and representative table behavior.
- Add a template-gated `build` command that orchestrates Pandoc, optional
  formatting and project adaptation, native or static cross-references,
  structural validation, and optional Microsoft Word validation.
- Make native Word cross-references the default build mode for standard
  continuous figure, table, and equation counters.
- Add regression coverage for successful template readiness, full build
  orchestration, and incomplete-template rejection.

## 2.6.0 - 2026-07-16

- Redefine the product as a submission-ready Word candidate produced through
  agent reasoning, user-confirmed requirements, deterministic validation, and
  feedback-driven revision.
- Replace the mandatory Pandoc/format/promote pipeline with a high-freedom
  orchestration workflow; bundled commands are optional tools with explicit
  assumptions.
- Remove the mandatory project workspace, filename contract, preferences state
  machine, and approval lifecycle.
- Replace setup/source/semantics catalogs with three task-focused references:
  deliverable contract, template and requirements, and handoff and revision.
- Make Zotero-live citations and native Word cross-references requirement-driven
  rather than universal defaults.
- Add a mature-template fast path and require only material clarification.
- Preserve source-of-truth files while allowing agent-created build-local TeX,
  Lua filters, Python/OpenXML, Word automation, or other suitable strategies.
- Keep structural validation as the candidate delivery gate and user Word
  acceptance as the final authority.
- Retain deterministic utilities for template, citation, DOCX, field, and Word
  validation while documenting formatter/promoter limitations.
- Include recursive citation audit, case-insensitive caption matching, and
  strict Word COM validation improvements from the v2.5 development line.

## 2.5.0 - 2026-07-16

- Move project preferences to `<project-root>/latex-to-word/preferences.md`.
- Define a minimal project workspace containing `preferences.md`, a user-owned `reference.docx`, `build/`, and `output/`.
- Make the bundled reference DOCX bootstrap/smoke-test only; formal builds require user review and an approved project working template.
- Reference original project resources instead of copying them into a skill-managed resources directory.
- Standardize diagnostic intermediates as `<entry-stem>.pandoc.docx` and `<entry-stem>.formatted.docx`.
- Promote native cross-references directly into `output/<project-slug>.docx`; remove normal `.native` and `.zotero-live` filename conventions.
- Mark static fallback outputs as `<project-slug>.static.docx`.
- Remove the fixed reports directory; successful reports remain in the terminal and optional diagnostics live under `build/`.
- Replace example-like prescribed filenames in the skill workflow with explicit placeholders.

## 2.4.0 - 2026-07-15

- Require agents to probe Zotero/Better BibTeX and use Zotero live whenever available.
- Restrict static CSL to explicit user/submission requirements or documented unavailable live tooling.
- Make native Word cross-reference promotion and bookmark/REF validation part of the default manuscript contract.
- Require unsupported cross-reference constructs to be reported instead of silently downgraded to static text.
- Update workspace preference defaults accordingly.

## 2.3.0 - 2026-07-15

- Slim the installable skill and keep a concise Chinese quick guide.
- Add one public `latex_to_word.py` CLI while keeping focused OOXML processors internal.
- Move regression tests, template generation/upgrades, complete examples, and ecosystem notes to repository-level development folders.
- Merge Better BibTeX probing into the citation command.
- Remove the preference-management script; the agent now maintains the reviewed Markdown template directly.
- Consolidate four reference documents into `setup.md` and `word-semantics.md`.

## 2.2.0 - 2026-07-15

- Separate universal conversion invariants from optional manuscript-formatting policies.
- Add a workspace-local preference guide template with explicit instruction precedence and scoped overrides.
- Add `workspace_preferences.py` to find, initialize, and append inactive preference proposals.
- Require user review before learned observations become accepted persistent policy.
- Change table formatting default from `booktabs` to `preserve`; keep booktabs as an opt-in capability.
- Make manuscript-style and native-heading contracts opt-in flags in the reference DOCX audit.
- Retain the former v2.1 behavior as an explicitly enabled strict capability set and regression path.

## 2.1.0 - 2026-07-15

- Add LaTeX structure preflight with strict handling of intentionally unnumbered display equations.
- Require and audit native Word multilevel numbering bindings for Heading 1–3.
- Add dedicated `Abstract Heading` and `Abstract Body` style validation.
- Apply deterministic booktabs-style scientific-table geometry after Pandoc.
- Strengthen native equation-number, mixed-math-cell, caption-style, and Zotero-field validation.
- Add end-to-end success and expected-failure regression tests.
- Expand the bundled reference DOCX and minimal example for the stricter workflow contract.

## 2.0.0 - 2026-07-14

- Add native Word `SEQ`/`REF` promotion for figures, tables, and labeled equations.
- Preserve LaTeX numbering across numbered-but-unlabeled predecessor objects.
- Add native cross-reference target, bookmark, and occurrence audits.
- Enforce LaTeX-to-DOCX table and image fidelity checks.
- Strengthen Zotero-live smoke validation and unresolved citation detection.
- Upgrade the bundled Word template with editable equation, image, table, and cross-reference examples.
- Expand bilingual workflow guidance, first-run setup, and ecosystem notes.

## 1.0.0 - 2026-07-13

- Initial public workflow for LaTeX-to-DOCX conversion with static CSL or Zotero-live citations.

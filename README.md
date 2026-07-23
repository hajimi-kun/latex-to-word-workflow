# LaTeX to Word Workflow

An agent skill for planning, executing, and reviewing project-specific
academic LaTeX-to-Word conversions.

Current version: **3.0.0**

## Purpose

LaTeX-to-Word conversion is highly dependent on the manuscript, target
template, citation workflow, numbering semantics, and local Word environment.
This skill therefore provides a lean routing contract, detailed on-demand
guidance, read-only evidence tools, and acceptance gates instead of a fixed
conversion pipeline.

The agent should:

- understand the complete LaTeX project and compile it when the host exposes the
  toolchain, otherwise record compilation evidence as pending;
- inspect the target Word requirements and preserve original files;
- start with the smallest reliable approach, normally Pandoc with a reference
  DOCX, and add project-local processing only for observed needs;
- prove the LaTeX–Pandoc–Word semantic mapping with representative content;
  a reference DOCX does not align differently named styles or create target
  behavior that Pandoc does not emit;
- preserve scientific content and numbering semantics ahead of editability;
- verify rather than merely claim live citations;
- probe Zotero capability only through host-exposed evidence and prefer confirmed
  live fields unless static citations are explicitly required or probing fails;
- generate and validate native Word cross-references by default, allowing
  static references only after an explicit informed user opt-out;
- validate high-risk objects and disclose approved exceptions;
- preserve prose chemical formulae and units as ordinary subscript/superscript
  text unless they are genuine mathematical expressions;
- use the user's desktop Word as the authoritative renderer for Word-specific
  fields, numbering, and template behavior;
- hand off exact Word/Zotero steps for the user to run, and independently re-audit
  the refreshed file when the user returns it.

## Installable skill

The only installable and released skill directory is
[`latex-to-word-workflow/`](latex-to-word-workflow/).

Repository-level behavior evals are kept in [`tests/`](tests/). They are
versioned with the skill so trigger and workflow expectations can be reviewed,
but are excluded from `git archive` release artifacts.

```powershell
git clone https://github.com/hajimi-kun/latex-to-word-workflow.git
Copy-Item -Recurse .\latex-to-word-workflow\latex-to-word-workflow "$env:USERPROFILE\.codex\skills\"
```

```bash
git clone https://github.com/hajimi-kun/latex-to-word-workflow.git
cp -R latex-to-word-workflow/latex-to-word-workflow ~/.claude/skills/
```

No Python package or bundled conversion CLI is required. The tools needed for
a conversion depend on the project and may include Pandoc, a LaTeX toolchain,
Microsoft Word, Zotero, or small project-local adapters.

## Skill layout

```text
latex-to-word-workflow/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── conversion-playbook.md
│   └── template-distillation.md
└── scripts/
    ├── docx_audit.py
    └── latex_manifest.py
```

- `SKILL.md` routes the task and contains the default workflow, decision rules,
  required checks, and recurring gotchas.
- `conversion-playbook.md` supplies detail only for complex templates,
  citations, cross-references, high-risk objects, validation, and handoff.
- `template-distillation.md` explains how to extract paragraph, character,
  numbering, object, and transition semantics from a Word target before the
  Pandoc probe.
- `latex_manifest.py` generates a deterministic, read-only source inventory.
- `docx_audit.py` checks the OpenXML package, fields, bookmark scopes, applied
  styles, unresolved markers, and refresh-save-reopen structural deltas without
  modifying the DOCX.
- `openai.yaml` provides Codex UI metadata and a default invocation prompt.

## Design principles

- **Submission-grade product:** the primary deliverable is a reviewable Word
  candidate, not a quick conversion draft.
- **Guidance plus evidence:** conversion choices remain contextual while stable,
  read-only checks are scripted.
- **One default:** begin with editable Pandoc output and escalate only when an
  observed requirement justifies more processing.
- **Project-local adaptation:** do not turn one manuscript's workaround into a
  universal source requirement.
- **Explicit semantic bridge:** inspect what Pandoc actually emits, map it to
  target styles, and post-process Word-only behavior deliberately.
- **Honest semantics:** visible citation or numbering text is not proof of a
  dynamic Word/Zotero field; native Word cross-references are the default when
  the source contains references.
- **Proportionate validation:** inspect high-risk content without requiring
  page-by-page LaTeX/PDF equality by default.
- **Capability-neutral execution:** never assume shell, process, GUI, COM, export,
  or rendering access. Record unobservable capabilities as unknown and convert
  optional desktop work into explicit user-run gates.
- **Word acceptance:** desktop Word validation and user open-and-confirm are
  required; package inspection and LibreOffice cannot substitute for them.

## Repository checks

The repository-level eval definitions are:

- `tests/trigger-cases.md`: three should-trigger and three should-not-trigger
  prompts;
- `tests/workflow-cases.md`: template-semantic cases that must be recognized
  before full conversion;
- `tests/expected-behaviors.md`: scoring, with/without-skill comparison, and
  cross-harness result recording.

Run these prompts in the supported harnesses and record results in a separate
local work log. They evaluate skill behavior; they do not attempt to test a
universal document converter.

## License

MIT. See [LICENSE](LICENSE).

## Community

- [LINUX DO](https://linux.do/)

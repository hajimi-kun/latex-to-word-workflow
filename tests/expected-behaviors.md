# Eval rubric and expected behaviors

Apply this rubric to the trigger cases and workflow cases. Preserve the prompt,
harness, model, tool availability, selected skill, tool-call count, correction
count, and final outcome for each run.

## Critical behaviors

A workflow case passes only when the agent performs all applicable agent-side
items and declares all user-gated items before the full manuscript conversion:

- reads the nearest project requirements;
- classifies the target as style-only, completed example, visual example, or
  hybrid;
- distills paragraph, character, numbering/field, object, and transition
  evidence;
- inventories the relevant LaTeX semantic roles;
- writes or clearly states the LaTeX–Pandoc–Word bridge;
- includes every high-risk role and transition in the representative probe;
- distinguishes imported style definitions from styles actually applied;
- identifies ambiguity or semantic loss instead of silently applying a generic
  Word default;
- verifies that each native cross-reference target range returns only the
  intended number or text rather than a whole heading, caption, image, or table;
- declares user-run field update plus save-and-reopen as a behavioral gate,
  compares pre/post structure when the refreshed file is returned, and never
  claims completion from field XML alone;
- defines the evidence required before calling a gate passed.
- probes locally available Zotero capability only when the host exposes it;
  otherwise records `unknown` or asks the user when material, and defaults to
  confirmed live fields unless static output is required or the probe fails;
- distinguishes prose chemical formulae/units from genuine Word equations;
- requires user evidence or a returned file to verify caption field formatting
  after field update, not only before it;
- requires user-supplied or supported-adapter rendered evidence for equation
  centering and right-number alignment;
- treats the user's target desktop Word environment as authoritative without
  assuming GUI, COM, process, export, or rendering access, and without treating a
  failed headless LibreOffice command as proof that Word is unavailable.

Missing any critical behavior that is central to the case is a failure even if
the agent later repairs the full DOCX after trial and error.

## Scoring

| Score | Interpretation |
|---:|---|
| 2 | Behavior appears before full conversion and is tied to concrete evidence |
| 1 | Behavior appears only after a generated defect or is stated without evidence |
| 0 | Behavior is absent or contradicted |

Score each applicable critical behavior. A workflow case passes when:

- no central behavior scores `0`;
- at least 80% of applicable behaviors score `2`;
- the agent does not claim template fidelity from style presence alone;
- the agent does not claim Word or Zotero validation from a lower-level check.

## With/without comparison

For at least three workflow cases, run the same prompt once with the skill and
once without it. Compare:

- number of full-document conversion attempts;
- number of corrective turns;
- tool calls spent rediscovering template behavior;
- whether high-risk mappings were identified before conversion;
- whether the final evidence level matches the claim.

The skill is beneficial when it reduces repeated discovery or corrective turns
without weakening the final document or validation standard.

## Cross-harness matrix

Run all trigger cases and at least three workflow cases in each supported
harness. Use the same prompt text and record environmental differences rather
than rewriting prompts to favor one harness.

| Date | Harness | Model | Cases | Passed | Trigger errors | Workflow errors | Changes prompted |
|---|---|---|---:|---:|---:|---:|---|
| | | | | | | | |

After an eval exposes a real failure, update the smallest relevant description,
route, decision rule, gotcha, or reference section and rerun the same case.

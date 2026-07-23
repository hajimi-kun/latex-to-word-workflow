# Conversion playbook

Load only the section needed for the current task. This file owns conversion,
field, validation, and handoff detail. Template classification and five-layer
distillation are defined only in `template-distillation.md`.

## Inspect source and environment

Inspect available evidence before asking the user. Ask only about an ambiguity
that materially affects submission, scientific meaning, editability, or target
formatting.

1. Locate the complete LaTeX entry point and recursively included files.
2. Compile the project with its intended engine and bibliography workflow when
   the host exposes that toolchain. Otherwise use a user-supplied compiled
   reference or record compilation as pending evidence; do not claim it ran.
3. Record custom macros, conditional compilation, counters, starred headings,
   appendices, citations, labels, reference commands, and high-risk objects.
4. Locate the authoritative Word target and output location. User instructions
   and nearest project requirements override target examples and definitions.
5. Probe Pandoc, the LaTeX toolchain, desktop Word, Zotero, its Word add-in,
   Better BibTeX, and compatible bridges only through capabilities exposed by
   the host. Record unobservable items as `unknown` and route any material
   confirmation to the user.
6. Hash or otherwise record authoritative inputs when source preservation must
   be demonstrated.

Use forward slashes in cross-platform commands and generated configuration even
on Windows. Keep shell syntax internally consistent; do not mix Bash and
PowerShell quoting or escaping.

Pandoc can parse an entry point without reproducing macro expansion, conditional
compilation, custom counters, or package-specific semantics. A successful LaTeX
compile and source inventory therefore remain separate evidence.

## Build the semantic bridge

For a new or changed target, first follow `template-distillation.md` and create
one contract row per required semantic role. Then create the bridge:

```text
LaTeX role | Pandoc output style/object | Target Word representation | Method
body role | Body Text | target body role | style remap
table role | DOCX table + default style | target table contract | post-process
equation role | display math + static number | target container + editable expression + native number | object bridge
caption role | caption paragraph | target segment sequence and packaging | run/object bridge
unnumbered heading | numbered Heading 1 | target unnumbered heading | semantic remap
table -> heading | adjacent blocks | target separation behavior | transition rule
```

Build a representative probe that covers every high-risk contract row. Include,
as applicable, title, authors, affiliations, abstract, keywords, ordinary body,
numbered and unnumbered headings, lists, captions, tables, equations, prose
chemical formulae and units, citations, bibliography, appendices, and relevant
object transitions. When the manuscript has display math, the probe must include
at least one **complex** equation (fraction plus a same-number secondary such as
`\qquad`), not only a short demo like `E = E_g + E_a`.

Inspect what Pandoc actually emits. Useful expectations, never passing evidence:

- `--reference-doc` imports definitions and defaults but does not map arbitrary
  source roles to custom target styles.
- Bold text does not automatically become a metadata or heading role.
- Captions do not automatically acquire target literals, mixed formatting,
  number fields, or correct bookmark scope.
- A starred heading can use a Word heading bound to a numbered list.
- LaTeX whitespace around objects does not reliably create Word spacing.
- Internal hyperlinks and bookmarks do not prove native Word cross-references.
- `ensuremath` can cause prose symbols and units to become OMML.

Choose the smallest method that closes an observed gap:

1. **Reference definition:** Pandoc already applies the intended style and the
   complete behavior is expressible in that definition.
2. **Style remap or working-template alias:** source and target have equivalent
   roles under different stable style IDs. Preserve inheritance, numbering, and
   linked character styles.
3. **Source annotation or Lua filter:** Pandoc needs a semantic distinction that
   is absent from its output.
4. **DOCX/OpenXML or supported Word post-processing:** the target needs native
   fields, exact bookmark scopes, list bindings, advanced tables, section
   behavior, headers/footers, text boxes, or another Word-only object. Word-side
   execution still requires an exposed adapter or a user-run step.

For a first build, copy `examples/bridge-starter/` with
`python scripts/init_bridge.py <build-dir>`. Keep the boundary explicit:

| Layer | Owns | Agent changes |
|---|---|---|
| `docx_bridge.py` | XML namespaces, runs, fields, bookmarks, style remaps, DOCX package writes | None unless a reusable bug is found |
| `bridge_config.json` | Required roles, target styles, target-owned literals and packaging values, prose-math mappings | Fill from the role contract; the starter values are not defaults |
| `project_adapter.py` | Template-specific metadata, transitions, and exceptional objects | Add only observed project rules |
| `semantic_filter.lua` | AST distinctions that must survive before DOCX output | Keep semantic; do not build Word XML here |

Do not reimplement field, bookmark, or package helpers in the project adapter.
Unknown roles must fail configuration validation rather than silently receive a
generic style.

Classify a mismatch before fixing it:

| Layer | Diagnostic question |
|---|---|
| Source semantics | Does the LaTeX distinguish the required role? |
| Pandoc semantic loss | Did the distinction disappear in the AST or DOCX? |
| Style mapping | Does the correct target style exist but remain unapplied? |
| Effective formatting | Is the style applied but inheritance/direct formatting wrong? |
| Character pattern | Are literals, punctuation, emphasis, or field runs wrong? |
| Object transition | Is the relationship between adjacent objects wrong? |
| Word behavior | Does refresh, numbering, bookmark scope, or section behavior fail in Word? |

Fix the responsible layer and rerun the probe. Do not alter scientific LaTeX
content merely to compensate for a target-specific Word formatting rule.

## Zotero-live citations

Apply the capability rules in
[Inspect source and environment](#inspect-source-and-environment). Installation
or a running Zotero process alone is not compatibility evidence. When citations
exist, Zotero-live is a delivery requirement for this skill.

Use this fixed setup and probe before the full manuscript build:

1. Confirm the real cited keys are present in `references.bib`; never invent or
   silently remap keys.
2. If Zotero is installed, start it and check Better BibTeX. If Better BibTeX
   or the Word add-in is missing, tell the user exactly what to install or
   enable. A missing `zotero` CLI alone is not evidence that Zotero is
   unavailable.
3. Check Better BibTeX with a real key using
   `python scripts/test_better_bibtex.py <real-key>` when the script is present.
   A failed API probe is a setup gate, not a citation-mode choice.
4. Obtain the current official `zotero.lua` filter from
   `https://retorque.re/zotero-better-bibtex/exporting/zotero.lua` and build a
   one-citation DOCX with that filter and **without** `--citeproc`:

```text
pandoc <probe.tex> -f latex -t docx --lua-filter=<zotero.lua> \
  --reference-doc=<reference.docx> -o <probe.docx>
```

5. Inspect the probe for `ADDIN ZOTERO_ITEM CSL_CITATION` fields and the
   expected cited key. If the probe passes, use the same route for the full
   manuscript and audit the resulting field count. Never combine `--citeproc`
   with `zotero.lua`.
6. If the probe fails, record the attempted action and concrete error, stop the
   citation-bearing build, and hand the user the missing setup steps. A DOCX
   with formatted `[N]` text is not an acceptable deliverable for this skill.

Zotero Refresh updates existing Zotero fields; it cannot create fields from
non-Zotero citation text. The user should set Document Preferences and use
**Refresh** only after live fields exist, then use Zotero **Add/Edit Bibliography**
to insert or update the bibliography.

## Native Word cross-references

Every LaTeX reference occurrence becomes a native Word field by default. Preserve
the source command's semantics:

- `\ref`: normally the target number only;
- `\eqref`: normally an equation number in parentheses;
- `\autoref`: localized object-type prefix plus target result;
- cleveref-style commands: singular/plural names, conjunctions, ranges,
  compression, capitalization, and mixed target types.

Implementation and verification procedure:

1. Inventory every referenced label and every occurrence, including figures,
   tables, equations, sections, appendices, and custom objects.
2. Create a verified native target for every referenced object. A number-only
   result must target only the number, never an entire heading, caption, drawing,
   table, or equation object.
3. Use `SEQ`, `REF`, `STYLEREF`, `DOCVARIABLE`, formula, or another native field
   representation appropriate to the actual numbering semantics. The requirement
   is native update behavior, not universal use of `REF`.
4. Keep literal prefixes outside number-only targets so refresh cannot produce
   duplicated text such as `Fig. Fig. 3`.
5. Treat list-numbered headings separately. A bookmark around a heading may
   return its title; hidden number runs can become visible under Word display
   settings. Test hidden text both shown and hidden.
6. Follow the field-update and returned-evidence procedure in
   [Validate and hand off](#validate-and-hand-off). Field XML does not prove that
   cached results were refreshed.

Missing targets, whole-object target scopes, broken fields, duplicated labels,
wrong numbering, or silent static substitution block delivery. Static references
are allowed only after an informed user opt-out is recorded.

## Preserve text and math semantics

Classify source occurrences by meaning rather than by LaTeX math mode:

- genuine inline or display mathematics uses editable OMML where practical;
- prose chemical formulae such as CO2 use ordinary runs with subscript or
  superscript formatting;
- compact units and scientific notation use text runs or stable Unicode when no
  mathematical operator structure is required;
- isolated degree, micro, multiplication, and plus/minus symbols do not become
  standalone equation objects inside ordinary prose.

Include each category in the probe. Inventory OMML by semantic location, not
only total count, and fail the bridge when ordinary prose is fragmented into
equation objects without mathematical need.

## Word-specific objects

### Captions

Model captions from the target's observed component sequence and packaging. For
example, some targets use one paragraph with four segments:

```text
[label] [number field] [separator] [caption body]
```

Do not assume that all four segments exist or share a paragraph. Preserve the
target's actual order, containers, literal abbreviation, capitalization,
punctuation, spaces, and emphasis boundaries. When a component is a field, apply
required formatting to its complete run sequence, including begin, instruction,
separator, cached result, and end runs. Have the user update fields in Word and
inspect every observed component again. The agent may inspect a returned file,
but cached pre-refresh formatting alone is not passing evidence.

### Numbered equations

Reproduce the equation representation recorded in the role contract, including
its container, component order, geometry, editable math object, number field,
bookmark scope, and punctuation. A target may use a paragraph with real tab
stops, a borderless table such as a 1 x 3 row with the formula in the center cell
and number in the right cell, or another Word structure. Implement only the
observed or explicitly required representation; `--reference-doc` does not
perform this mapping.

Use genuine structural controls for the selected representation: real `w:tab`
elements for a tabbed target, or explicit grid, cell width, border, padding, and
alignment properties for a table target. Do not substitute spaces or text tab
characters for geometry.

**Container vs size:** keep the target container type, but treat example
**column widths** as size hints, not a universal contract. Equal-third math cells
fit short formulae; long OMML needs a wide center (or equivalent) cell. Field or
object counts do not catch mid-expression wrap—check grid/`tcW` against a
complex probe equation, and Word rendering when available.

If a visual-only target uses fragile internal markup, record that fact and
implement a stable Word structure that preserves the confirmed appearance and
behavior. Verify the equation's rendered position, the number's position, and
short/long/multiline behavior from user evidence or a supported rendering
adapter.

### Headings, sections, headers, and footers

Inspect actual list bindings for numbered and unnumbered headings. Tell the user
to refresh and inspect fields in headers, footers, text boxes, and the table of
contents separately because normal body-field updates may not cover them.
Preserve section breaks, page setup, page numbering, and header/footer
relationships explicitly.

## High-risk objects

Use targeted structural inspection plus visual evidence supplied by the user or
an explicitly supported rendering/inspection adapter:

- Convert PDF, EPS, TikZ, and PGFPlots artwork explicitly to a Word-supported
  format and verify the intended asset, resolution, labels, and legibility.
- Inspect multi-panel, wrapped, landscape, and page-boundary figure placement.
- For complex tables, inspect merged cells, notes, borders, widths, repeated
  headers, page breaks, editability, and target table styles.
- For equations, inspect container structure, **math-cell width**, multiline
  alignment, tags, symbols, fields, bookmarks, and mixed text/math.
- Inspect content controls, text boxes, section breaks, headers, footers, page
  numbering, and the table of contents as separate Word structures.

Raw figure/table counts are diagnostic. Subfigures, nested objects, repeated
media, and conversion choices can make naive equality checks misleading.

## Validate and hand off

### Evidence loop

1. Generate a source manifest. The bundled `scripts/latex_manifest.py` provides
   a deterministic baseline, supplemented by manual inspection of custom macros.
2. Generate a candidate audit with `scripts/docx_audit.py`. Inspect styles,
   fields, bookmarks, relationships, object locations, and unresolved markers.
3. Compare source, role contract, compiled LaTeX result, and candidate role by
   role. Classify and fix the first mismatch, rebuild, and repeat affected checks.
4. Give the user exact steps for the disposable copy: open in desktop Word,
   confirm Zotero Document Preferences and perform Zotero Refresh when
   applicable, update native fields, save, close, reopen, and inspect the named
   high-risk locations.
5. If the refreshed file is returned, re-run the DOCX audit with the pre-refresh
   audit as `--baseline`. Investigate every structural delta; bibliography
   refresh can legitimately add paragraphs, but duplicated drawings/tables or
   lost fields are defects.
6. Treat Word-visible inspection or Word PDF export supplied by the user as the
   authoritative visual gate. The agent may perform it only through an explicitly
   supported host adapter.
7. Record the acceptance state precisely: `pending user action`,
   `user-confirmed, unaudited`, or `returned file independently audited`.

### Passing evidence

| Gate | Passing evidence |
|---|---|
| Content completeness | Source and DOCX correspond by semantic role, order, target type, and occurrence |
| Scientific fidelity | High-risk values, units, symbols, labels, and numbering match source and compiled LaTeX |
| Editability | Body/table text is native Word content; equations are editable where practical |
| Template fidelity | Intended style IDs, effective formatting, list bindings, character patterns, and transitions are applied |
| Figures and tables | Correct relationships, assets, legibility, structure, and target behavior |
| Citations | Live field presence is verified; refreshed-live status additionally requires a returned refreshed file or explicit user confirmation labelled unaudited |
| Cross-references | Every occurrence has a valid native field and target scope; refreshed results require user evidence or a returned file |
| DOCX integrity | Package parses; Word open without repair is user evidence unless a supported adapter performed it |
| Preservation | Authoritative LaTeX, bibliography, figures, and Word target remain unchanged |
| Acceptance | User opened the final candidate and confirmed the required Word/Zotero behavior |

Package inspection cannot replace Word. The absence of desktop-control capability
does not authorize the agent to skip or pretend to complete the user's required
update-save-reopen sequence. Report pending gates, unresolved constructs, and
approved exceptions instead of marking them passed.

### Handoff format

```text
Deliverable: <path>
Target/template: <authoritative requirement source>
Citation mode: live fields, refresh pending | user-confirmed unaudited | independently audited live | none in source
Cross-reference mode: native Word fields | user-approved static opt-out | none
Validation: <agent-side checks; user-run steps; returned-file checks if any>
Adaptations/exceptions: <list or none>
User confirmation: pending | confirmed unaudited | confirmed and returned file audited
```

For feedback, request the page/section, object, current result, expected result,
and any Word/Zotero warning. Classify the cause, apply the smallest reliable fix,
and repeat the relevant evidence loop.

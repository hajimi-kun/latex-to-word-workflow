# Workflow behavior cases

Use these cases to test whether the skill changes agent behavior before a full
conversion is attempted. The target behavior is early discovery and an
explicit semantic bridge, not a preselected implementation technique.

## Case 1: specialized keyword roles

**Prompt fixture:** The LaTeX source expresses a bold `KEYWORDS` paragraph and a
plain keyword-list paragraph. The Word target contains dedicated zero-indent
styles for the keyword heading and keyword body.

**Expected behavior:** Identify a source-role ambiguity, inspect the target
styles and effective indentation, predict that Pandoc may emit ordinary body
or first-paragraph styles, and add both keyword roles to the probe and bridge.

**Failure:** Assume `--reference-doc` will select the dedicated styles or wait
for the full candidate to reveal first-line indentation.

## Case 2: mixed-format figure caption

**Prompt fixture:** The target example uses an abbreviated figure label. The
label, number, and separator are bold; the caption body is normal weight.

**Expected behavior:** Distill the observed four-segment sequence, literal label,
single-paragraph packaging, and run-format boundary, then verify the probe at
character level. Treat four segments as evidence in this target, not a universal
caption model.

**Failure:** Record only the paragraph style, substitute a generic expanded
label, or apply one weight to the full caption.

## Case 3: table transition rules

**Prompt fixture:** The target uses different spacing when a table is followed
by body text, a heading, or another table caption. Some examples use an empty
paragraph rather than paragraph spacing.

**Expected behavior:** Classify these as separate object transitions, determine
which examples are normative, and include each relevant transition in the
contract and probe.

**Failure:** Infer a single global table spacing rule or assume LaTeX blank
lines will create visible Word blank paragraphs.

## Case 4: starred headings

**Prompt fixture:** The source contains `\section*` headings. The target has
visually similar numbered and unnumbered heading styles, while the normal
Heading 1 style is bound to a multilevel list.

**Expected behavior:** Preserve the starred semantic distinction, map it to an
unnumbered target role, and inspect the generated list binding and list string.

**Failure:** Match only by heading level or visible font formatting.

## Case 5: imported but unused styles

**Prompt fixture:** The candidate package contains every custom target style,
but generated keyword, caption, and unnumbered-heading paragraphs use Pandoc's
default styles.

**Expected behavior:** Mark the roles as unmapped because the generated content
does not use the intended styles. Require actual style application evidence.

**Failure:** Treat style presence in `styles.xml` as template fidelity.

## Case 6: target evidence conflicts

**Prompt fixture:** A style definition suggests one spacing pattern, a completed
example uses a direct-format exception, and the user states a third explicit
requirement.

**Expected behavior:** Apply the evidence hierarchy: explicit user and project
requirements first, then authoritative normative examples, then reusable style
definitions. Report unresolved contradictions instead of silently merging
them.

**Failure:** Copy every direct-format exception or choose the easiest Pandoc
default without explaining the conflict.

## Case 7: over-broad cross-reference bookmarks

**Prompt fixture:** Pandoc creates bookmarks that span an entire numbered
heading, captioned image, or table. The target requires references such as
`Fig. 3`, `Table 2`, and `Section 2.1`, with only the number supplied by the
field.

**Expected behavior:** Inspect the exact bookmark ranges before promoting
links, create or choose number-only native targets, keep literal prefixes
outside those targets, then give the user the Word field-update steps and verify
refreshed results from returned-file or user evidence. Treat section list
numbers separately when an ordinary `REF` returns the heading text.

**Failure:** Point `REF` at the existing whole-object bookmark, infer target
scope from the bookmark name, or accept `Fig. Fig. 3`, copied drawings/tables,
or full heading titles after field update.

## Case 8: refresh-save structural stability

**Prompt fixture:** A generated DOCX has valid package XML and expected field
counts before refresh, but updating Word and Zotero fields and saving may alter
field boundaries, styles, paragraphs, drawings, or tables.

**Expected behavior:** Give the user the exact Word/Zotero update, save, close,
and reopen sequence. Compare pre/post manifests when the refreshed file is
returned; otherwise label the gate pending or user-confirmed but unaudited.

**Failure:** Treat package inspection, cached field results, or a read-only Word
open as proof that the editable-field document survives the user workflow.

## Case 9: installed Zotero without an explicit live request

**Prompt fixture:** The manuscript contains citations. Zotero is installed or
running and a compatible Word/Better BibTeX bridge may be available, but the
user did not explicitly choose static or live citations.

**Expected behavior:** Probe the complete Zotero route when the host exposes the
needed evidence. Otherwise ask only when material or record `unknown`. Use live
fields by default when compatibility is confirmed; use static citations only
after an explicit static requirement or a recorded probe failure.

**Failure:** Choose static citations merely because the user did not say
"Zotero live", claim live support from process presence, or pretend to inspect
an application or process that the host cannot expose.

## Case 10: prose chemical formulae emitted as OMML

**Prompt fixture:** A LaTeX macro uses `\ensuremath` for CO2, micrometres,
degrees Celsius, and plus/minus values throughout ordinary prose.

**Expected behavior:** Map genuine mathematics to OMML but represent prose
formulae and units as ordinary Word text with subscript/superscript or stable
Unicode symbols. Inspect OMML by semantic location.

**Failure:** Preserve every `\ensuremath` occurrence as a Word equation simply
because Pandoc emitted OMML.

## Case 11: caption field loses bold formatting

**Prompt fixture:** The template makes `Fig.`, the `SEQ` result, and the period
bold, while the caption body is normal. Field update can replace the cached
number run.

**Expected behavior:** Apply bold formatting to the complete number-field run
structure, tell the user to update fields, and verify all four caption segments
again only from returned-file or user evidence.

**Failure:** Inspect only the cached result before refresh or leave only the
literal `Fig.` label bold after update.

## Case 12: equation numbers disturb centering

**Prompt fixture:** The template uses center and right tab stops for an editable
equation with a right-side number. Short and long equations must share the same
visual center.

**Expected behavior:** Reproduce actual tab and paragraph alignment semantics,
then measure or visually verify the equation center relative to the text area
and the number against the right tab stop.

**Failure:** Insert spaces or a text tab only after the equation, validate only
the number's presence, or accept visibly off-center equations.

## Case 13: capability-limited generic agent

**Prompt fixture:** The agent can read and write project files and invoke a DOCX
converter, but the host exposes no process detection, desktop GUI, Word COM,
Zotero UI, Word rendering, or visual-inspection adapter.

**Expected behavior:** Record unobservable capabilities as `unknown`, complete
file-level conversion and audits, hand the user exact Word/Zotero/visual steps,
and report the resulting gates as pending or user-confirmed unaudited until a
refreshed file or equivalent evidence is returned.

**Failure:** Infer that Word or Zotero is absent, attempt unsupported UI
automation, or claim that Word, Zotero Refresh, or visual validation passed from
OpenXML evidence alone.

## Case 14: first build uses the canonical bridge starter

**Prompt fixture:** A complete LaTeX manuscript and a new custom Word target are
provided. No project-local bridge exists yet. Captions, equations, and
cross-references require native Word fields and tight bookmarks.

**Expected behavior:** Distill the required roles, run `scripts/init_bridge.py`
into the generated build directory, fill `bridge_config.json`, and adapt only
observed project rules in `project_adapter.py` or `semantic_filter.lua`. Reuse
`docx_bridge.py` for field, bookmark, style, and package operations, then validate
the representative probe before the complete build.

**Failure:** Write a new monolithic Lua/OpenXML converter, duplicate field or
bookmark constructors in project code, silently accept `__SET_ME__` roles, or
start the complete manuscript before the configured starter passes its probe.

## Case 15: numbered equations use a borderless table

**Prompt fixture:** The authoritative hybrid Word target demonstrates numbered
equations as a 1 x 3 borderless table. The formula is centered in the middle
cell, the native number field is right-aligned in the last cell, and the first
cell balances the number column. The target contains no equation tab-stop
example.

**Expected behavior:** Record the table container, grid and cell widths, border
state, padding, cell and paragraph alignment, editable equation representation,
number field, bookmark scope, and visual centering in the role contract. Build
that structure in the object bridge and probe short, long, and multiline
equations.

**Failure:** Emit the starter's or playbook's preferred paragraph/tab layout,
assume `--reference-doc` maps equations to the example table, or validate only
that an equation and number are present.

## Case 16: target has non-journal roles and caption order

**Prompt fixture:** A thesis target has no figure captions or references heading,
uses Chinese table labels, and places figure captions above figures and table
titles in two paragraphs.

**Expected behavior:** Configure only roles present in the source and required by
the target. Distill the target-owned literals, two-paragraph table-title
packaging, and actual object order, then implement and probe those transitions.

**Failure:** Require the starter's former journal role inventory, emit `Fig.` or
`Table` literals, collapse table titles to one paragraph, or force captions below
figures.

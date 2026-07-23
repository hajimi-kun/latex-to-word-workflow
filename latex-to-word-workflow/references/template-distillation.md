# Template distillation

Use this reference before the Pandoc probe whenever a Word template, completed
example, or retained DOCX controls the target formatting. The purpose is to
turn dispersed Word evidence into an explicit semantic contract. Do not assume
that passing the file to Pandoc performs this interpretation.

Inspect package-level evidence with available file tools. When a contract value
depends on rendered appearance and the host exposes no renderer or visual
inspection capability, ask the user for that evidence or mark the value pending;
never infer it from OpenXML structure alone.

## Classify the target evidence

Classify each target document before using it:

- **Style-only reference:** primarily supplies style, numbering, theme, page,
  header, footer, and table definitions.
- **Completed formatting example:** demonstrates the desired appearance and
  behavior through real manuscript content.
- **Hybrid:** contains both reusable definitions and normative example
  paragraphs or objects.
- **Visual example only:** communicates appearance but has inconsistent or
  unsuitable internal Word structure.

A document containing labels such as `Style: Figure Caption` followed by an
example paragraph is normally a hybrid. The style definition and the example
paragraph provide different evidence; inspect both.

User instructions and the nearest project requirements override the target
document. When two target documents disagree, identify which one is
authoritative instead of silently combining their conventions.

## Read five layers

Template requirements can be encoded at five different layers.

### 1. Definition layer

Inspect paragraph, character, table, and linked styles; style inheritance;
themes; numbering definitions; page and section settings; headers; footers; and
default document properties.

This layer establishes which resources exist. It does not prove that generated
content uses them.

### 2. Effective paragraph layer

For each semantic role, resolve inherited and direct formatting:

- first-line, left, right, and hanging indents;
- space before and after, line spacing, and contextual spacing;
- alignment, tabs, borders, shading, and outline level;
- keep-with-next, keep-lines-together, widow/orphan, and page-break behavior;
- list definition, list level, restart behavior, and displayed list string.

Do not compare style names alone. Two styles can look similar while differing
in numbering or inheritance, and one paragraph can override its style directly.

### 3. Character layer

Inspect formatting boundaries inside representative paragraphs. Record font,
size, bold, italic, underline, color, language, superscript/subscript, and field
result formatting for each semantic segment.

For captions, identify the actual sequence of semantic segments and its
packaging. A common single-paragraph pattern is:

```text
[label] [number] [separator] [caption body]
```

This pattern is an example, not a required model. The target may omit a segment,
reorder segments, place a label or title in a separate paragraph or table cell,
or use another structure. Confirm the literal label, capitalization,
abbreviation, punctuation, spaces, order, container, and emphasis boundary for
each observed segment. A paragraph style cannot by itself express that only a
caption prefix is bold.

When a segment contains a field, inspect the formatting of the complete field
run sequence, not only its cached result. Record which of the label, number,
separator, and body must remain bold or italic after Word updates the field.

### 4. Object layer

Inspect the internal structure and scope of:

- figures, tables, captions, notes, and equations;
- multilevel lists and heading numbering;
- `SEQ`, `REF`, `STYLEREF`, bibliography, and other fields;
- bookmarks and the exact content they enclose;
- section breaks, headers, footers, text boxes, and content controls.

Record whether a bookmark encloses a number, a paragraph, or an entire object.
Record the container, ordering, and scope of every caption component, including
whether the caption is one paragraph, multiple paragraphs, or part of another
Word object.

For equations, first record the enclosing Word structure: a paragraph, a
borderless or bordered table, a text box, or another container. Then record the
relevant geometry and contents, such as table dimensions, cell widths, borders,
cell and paragraph alignment, padding, tab stops and actual tab elements when
present, equation representation, number field, bookmark scope, punctuation,
and ordering. Record the visual center of the equation relative to the text area
when rendered evidence is available. Tabbed paragraphs and borderless 1 x 3
tables are examples of possible target structures; neither is the generic
default. **Do not copy equal-third cell widths from a short template demo onto
long manuscript OMML** without a complex-equation probe; container type and
usable math width are separate contract values. For prose chemical formulae,
units, degrees, and isolated symbols, record whether the target uses ordinary
subscript/superscript text rather than a Word equation object.

### 5. Transition layer

Inspect how adjacent semantic objects are separated. Rules may be expressed by
paragraph spacing, an intentional empty paragraph, keep behavior, or the order
of body elements rather than by a named style.

Record relevant transitions explicitly. The following are non-normative
examples; inspect the target's actual ordering and do not infer caption placement
from this list:

```text
abstract -> keywords heading
keywords -> first numbered heading
body -> figure
figure -> figure caption
figure caption -> figure
table caption -> table
table -> table caption
table -> table note
table -> body
table -> heading
table -> next table caption
```

Do not generalize from one transition. A table followed by body text may use a
different rule from a table followed by a heading or another table. LaTeX
source whitespace does not reliably create visible Word spacer paragraphs.

## Build the role contract

Create one row for every required manuscript role:

| Field | Record |
|---|---|
| Semantic role | The source role, such as keywords body, figure caption, or unnumbered heading |
| Target evidence | The style, example paragraph, field, or object that proves the requirement |
| Paragraph/table style | Stable style ID and human-readable name |
| Effective paragraph format | Indents, spacing, alignment, tabs, keep rules, and list binding |
| Character pattern | Segment-level formatting and literal text conventions |
| Object structure/packaging | Paragraphs, tables/cells, text boxes, object order, geometry, borders, and component scope |
| Numbering/field behavior | List, `SEQ`, `REF`, bookmark, reset, and display semantics |
| Math/text representation | OMML expression or ordinary text with subscript, superscript, or Unicode |
| Before transition | Required relationship to the preceding object |
| After transition | Required relationship to the following object |
| Pandoc observation | What the representative probe actually emits |
| Required bridge | Native use, style remap, annotation, filter, or targeted post-processing |

Use stable style IDs for structural mapping because displayed style names may
be localized. Retain the displayed names in the contract so a user can inspect
the document in Word.

## Interpret example content carefully

Normative examples can communicate rules that are absent from style
definitions:

- abbreviated versus expanded object labels;
- capitalization and punctuation;
- partial bold or italic formatting;
- whether a table caption uses one or two paragraphs;
- whether a title is numbered, unnumbered, or list-bound;
- empty paragraphs used for visible separation;
- the scope of fields and bookmarks.

Do not treat every empty paragraph or direct-format exception as normative.
Classify it by checking repeated examples, surrounding labels, project
instructions, and whether the behavior has a clear semantic purpose. Mark an
important unresolved value instead of inventing a rule.

## Distillation gate

Do not run the full manuscript conversion until:

- every required semantic role has a target representation;
- mixed character formatting has been recorded where present;
- numbered and unnumbered roles are distinguished;
- relevant object transitions are explicit;
- ambiguous or contradictory template evidence has been resolved or reported;
- the representative probe can test every high-risk contract row.

The probe is a test of the distilled contract. It is not the process by which
the contract is discovered after repeated full-document failures.

"""Promote Pandoc object links to native Word SEQ/REF fields."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W, M = f"{{{W_NS}}}", f"{{{M_NS}}}"
NS = {"w": W_NS, "m": M_NS}

LABEL_RE = re.compile(r"\\label\s*\{([^}]+)\}")
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
# Numbered float envs (not figure*/table*)
FLOAT_ENV_RE = re.compile(
    r"\\begin\{(figure\*?|table\*?)\}(.*?)\\end\{\1\}",
    re.S,
)
# Numbered display-equation envs (not starred)
EQ_ENV_RE = re.compile(
    r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|flalign\*?|eqnarray\*?)\}"
    r"(.*?)\\end\{\1\}",
    re.S,
)
# After "Fig." the next char is often space (not a word char), so avoid trailing \b only.
CAPTION_HINTS = {
    "fig": re.compile(r"^(fig\.?|figure|图)(?:\s|[.:：]|$|\d)", re.I),
    "tab": re.compile(r"^(tab\.?|table|表)(?:\s|[.:：]|$|\d)", re.I),
}
STYLE_CAPTION_NAMES = frozenset({"Caption", "Table Caption", "TableCaption", "题注"})
MULTILINE_EQ = frozenset({"align", "eqnarray", "flalign"})


def run(text: str = "", *, bold: bool = False, no_proof: bool = False) -> etree._Element:
    element = etree.Element(W + "r")
    if bold or no_proof:
        properties = etree.SubElement(element, W + "rPr")
        if bold:
            etree.SubElement(properties, W + "b")
            etree.SubElement(properties, W + "bCs")
        if no_proof:
            etree.SubElement(properties, W + "noProof")
    if text:
        node = etree.SubElement(element, W + "t")
        node.text = text
        if text[:1].isspace() or text[-1:].isspace():
            node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return element


def field(instruction: str, display: str, *, bold: bool = False) -> list[etree._Element]:
    begin, code, separate, result, end = (run(bold=bold) for _ in range(5))
    etree.SubElement(begin, W + "fldChar").set(W + "fldCharType", "begin")
    instruction_node = etree.SubElement(code, W + "instrText")
    instruction_node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    instruction_node.text = f" {instruction} "
    etree.SubElement(separate, W + "fldChar").set(W + "fldCharType", "separate")
    text_node = etree.SubElement(result, W + "t")
    text_node.text = display
    result_properties = result.find(W + "rPr")
    if result_properties is None:
        result_properties = etree.SubElement(result, W + "rPr")
    etree.SubElement(result_properties, W + "noProof")
    etree.SubElement(end, W + "fldChar").set(W + "fldCharType", "end")
    return [begin, code, separate, result, end]


def bookmark_field(name: str, bookmark_id: int, instruction: str, display: str,
                   *, bold: bool = False) -> list[etree._Element]:
    start = etree.Element(W + "bookmarkStart")
    start.set(W + "id", str(bookmark_id))
    start.set(W + "name", name)
    end = etree.Element(W + "bookmarkEnd")
    end.set(W + "id", str(bookmark_id))
    return [start, *field(instruction, display, bold=bold), end]


def text(element: etree._Element) -> str:
    return "".join(element.xpath(".//w:t/text()", namespaces=NS))


def paragraph_style(paragraph: etree._Element) -> str | None:
    styles = paragraph.xpath("./w:pPr/w:pStyle/@w:val", namespaces=NS)
    return styles[0] if styles else None


def replace_hyperlink(hyperlink: etree._Element, bookmark: str, display: str,
                      *, parentheses: bool = False) -> None:
    parent, index = hyperlink.getparent(), hyperlink.getparent().index(hyperlink)
    parent.remove(hyperlink)
    nodes = field(f"REF {bookmark} \\h", display)
    if parentheses:
        nodes = [run("("), *nodes, run(")")]
    for offset, node in enumerate(nodes):
        parent.insert(index + offset, node)


def caption_for_label(start: etree._Element, category: str) -> etree._Element:
    """Locate caption for a fig:/tab: bookmark; refuse arbitrary body text."""
    # Climb to the enclosing paragraph (bookmarkStart itself is not a stop tag).
    current = start
    while current is not None and current.tag not in {W + "p", W + "body"}:
        current = current.getparent()

    candidates: list[etree._Element] = []
    if current is not None and current.tag == W + "p":
        if text(current).strip():
            candidates.append(current)
        sibling = current.getnext()
    else:
        sibling = start.getnext()
    while sibling is not None and len(candidates) < 8:
        if sibling.tag == W + "p" and text(sibling).strip():
            candidates.append(sibling)
        sibling = sibling.getnext()

    hint = CAPTION_HINTS[category]
    for paragraph in candidates:
        style = paragraph_style(paragraph) or ""
        body = text(paragraph).strip()
        if style in STYLE_CAPTION_NAMES or style.endswith("Caption"):
            return paragraph
        if hint.match(body):
            return paragraph

    for paragraph in candidates:
        body = text(paragraph).strip()
        if CAPTION_HINTS["fig"].match(body) or CAPTION_HINTS["tab"].match(body):
            return paragraph

    label = start.get(W + "name")
    raise RuntimeError(
        f"Caption not found for {label}: need Caption style or "
        f"Fig./Figure/Table/图/表-prefixed paragraph near the bookmark"
    )


def strip_comments(source: str) -> str:
    cleaned: list[str] = []
    for line in source.splitlines():
        match = re.search(r"(?<!\\)%", line)
        cleaned.append(line[: match.start()] if match else line)
    return "\n".join(cleaned)


def expand_tex(path: Path, stack: tuple[Path, ...] = ()) -> str:
    resolved = path.resolve()
    if resolved in stack:
        chain = " -> ".join(str(item) for item in (*stack, resolved))
        raise RuntimeError(f"Cyclic LaTeX include: {chain}")
    if not resolved.exists():
        raise FileNotFoundError(f"LaTeX source not found: {resolved}")
    source = strip_comments(resolved.read_text(encoding="utf-8"))
    parts: list[str] = []
    cursor = 0
    for match in INPUT_RE.finditer(source):
        parts.append(source[cursor : match.start()])
        raw = match.group(1).strip()
        child = (resolved.parent / raw).resolve()
        if not child.suffix:
            child = child.with_suffix(".tex")
        parts.append(expand_tex(child, (*stack, resolved)))
        cursor = match.end()
    parts.append(source[cursor:])
    return "".join(parts)


def latex_float_numbers(tex: Path) -> dict[str, dict[str, int]]:
    """Map fig:/tab: labels to 1-based counters; figure*/table* do not advance."""
    source = expand_tex(tex)
    figures: dict[str, int] = {}
    tables: dict[str, int] = {}
    fig_n = tab_n = 0
    for match in FLOAT_ENV_RE.finditer(source):
        env, body = match.group(1), match.group(2)
        labels = LABEL_RE.findall(body)
        if env == "figure":
            fig_n += 1
            for label in labels:
                figures[label] = fig_n
        elif env == "table":
            tab_n += 1
            for label in labels:
                tables[label] = tab_n
    return {"fig": figures, "tab": tables}


def latex_equation_units(tex: Path) -> list[tuple[int, list[str]]]:
    """
    Ordered numbered equation units: (number, labels).

    Advances for equation/align/... even without \\label.
    Skips starred environments. Multi-line align/eqnarray/flalign: one unit per row
    (rows with \\notag/\\nonumber skipped).
    """
    source = expand_tex(tex)
    units: list[tuple[int, list[str]]] = []
    counter = 0
    for match in EQ_ENV_RE.finditer(source):
        env, body = match.group(1), match.group(2)
        if env.endswith("*"):
            continue
        base = env.rstrip("*")
        if base in MULTILINE_EQ:
            for row in re.split(r"\\\\", body):
                if re.search(r"\\(notag|nonumber)\b", row) or not row.strip():
                    continue
                counter += 1
                units.append((counter, LABEL_RE.findall(row)))
        else:
            counter += 1
            units.append((counter, LABEL_RE.findall(body)))
    return units


def equation_numbers_for_displays(
    units: list[tuple[int, list[str]]],
    display_labels: list[str | None],
) -> list[int | None]:
    """
    Map each Pandoc display-math slot to a LaTeX equation number or None (unnumbered).

    Labeled displays use the unit that defines that label (so unlabeled Eq.1 + labeled
    Eq.2 yields 2 for the labeled slot). Unlabeled displays consume remaining units
    in order (numbered-but-unlabeled equations still get a SEQ number).
    """
    label_to_number: dict[str, int] = {}
    for number, labels in units:
        for label in labels:
            label_to_number[label] = number

    used_numbers: set[int] = set()
    result: list[int | None] = [None] * len(display_labels)

    for index, label in enumerate(display_labels):
        if label and label in label_to_number:
            number = label_to_number[label]
            result[index] = number
            used_numbers.add(number)

    remaining = [number for number, _ in units if number not in used_numbers]
    rem_i = 0
    for index, label in enumerate(display_labels):
        if result[index] is not None:
            continue
        if rem_i < len(remaining):
            result[index] = remaining[rem_i]
            rem_i += 1
        # else: unnumbered display such as \[...\] with no matching unit left
    return result


def pandoc_display_math(tex: Path) -> list[str | None]:
    result = subprocess.run(
        ["pandoc", str(tex), "-f", "latex", "-t", "json"],
        cwd=tex.parent,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "pandoc failed")
    document = json.loads(result.stdout)
    equations: list[str | None] = []

    def visit(value):
        if isinstance(value, dict):
            if value.get("t") == "Math" and value.get("c", [{}])[0].get("t") == "DisplayMath":
                match = re.search(r"\\label\s*\{([^}]+)\}", value["c"][1])
                equations.append(match.group(1) if match else None)
            else:
                for child in value.values():
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(document.get("blocks", []))
    return equations


def set_equation_number_layout(paragraph: etree._Element) -> None:
    """Tab stops: center for math, right for the equation number."""
    p_pr = paragraph.find(W + "pPr")
    if p_pr is None:
        p_pr = etree.Element(W + "pPr")
        paragraph.insert(0, p_pr)
    for old in p_pr.findall(W + "tabs"):
        p_pr.remove(old)
    tabs = etree.SubElement(p_pr, W + "tabs")
    center = etree.SubElement(tabs, W + "tab")
    center.set(W + "val", "center")
    center.set(W + "pos", "4500")
    right = etree.SubElement(tabs, W + "tab")
    right.set(W + "val", "right")
    right.set(W + "pos", "9000")


def tab_run() -> etree._Element:
    element = etree.Element(W + "r")
    etree.SubElement(element, W + "tab")
    return element


def promote(input_path: Path, output_path: Path, tex: Path | None) -> None:
    float_numbers = latex_float_numbers(tex) if tex else {"fig": {}, "tab": {}}
    eq_units = latex_equation_units(tex) if tex else []

    with ZipFile(input_path) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))
        ids = [
            int(value)
            for value in root.xpath(".//w:bookmarkStart/@w:id", namespaces=NS)
            if value.isdigit()
        ]
        next_id = max(ids, default=0) + 1
        targets: dict[str, tuple[str, str, str]] = {}

        object_labels = [
            node
            for node in root.xpath(".//w:bookmarkStart", namespaces=NS)
            if (node.get(W + "name") or "").startswith(("fig:", "tab:"))
        ]
        fallback = {"fig": 0, "tab": 0}
        for start in object_labels:
            label = start.get(W + "name")
            category = label.split(":", 1)[0]
            kind = "Fig." if category == "fig" else "Table"
            tex_map = float_numbers.get(category, {})
            if label in tex_map:
                number = tex_map[label]
            else:
                fallback[category] += 1
                number = fallback[category]
            caption = caption_for_label(start, category)
            bookmark = f"RefNative{'Fig' if category == 'fig' else 'Table'}{number:03d}"
            instruction = f"SEQ {kind} \\* ARABIC \\r {number}"
            prefix = [run(f"{kind} ", bold=True)]
            prefix.extend(bookmark_field(bookmark, next_id, instruction, str(number), bold=True))
            prefix.extend([run(". ", bold=True)])
            insert_at = 1 if caption.find(W + "pPr") is not None else 0
            for offset, node in enumerate(prefix):
                caption.insert(insert_at + offset, node)
            targets[label] = (bookmark, str(number), category)
            next_id += 1

        if tex:
            labels = pandoc_display_math(tex)
            math_paragraphs = root.xpath(".//w:p[m:oMathPara]", namespaces=NS)
            if len(labels) != len(math_paragraphs):
                raise RuntimeError(
                    f"Pandoc found {len(labels)} display equations but DOCX contains "
                    f"{len(math_paragraphs)} OMML display paragraphs"
                )
            eq_numbers = equation_numbers_for_displays(eq_units, labels)
            for label, paragraph, eq_number in zip(labels, math_paragraphs, eq_numbers):
                if eq_number is None:
                    continue
                math_para = paragraph.find(M + "oMathPara")
                if math_para is None:
                    continue
                math = math_para.find(M + "oMath")
                if math is None:
                    continue
                math_para.remove(math)
                paragraph.replace(math_para, math)
                set_equation_number_layout(paragraph)
                # Layout: [center-tab][math][right-tab][(][SEQ][)]
                math_node = paragraph.find(M + "oMath")
                math_index = paragraph.index(math_node) if math_node is not None else 0
                paragraph.insert(math_index, tab_run())
                bookmark = f"RefNativeEquation{eq_number:03d}"
                instruction = f"SEQ Equation \\* ARABIC \\r {eq_number}"
                paragraph.append(tab_run())
                paragraph.append(run("("))
                for node in bookmark_field(bookmark, next_id, instruction, str(eq_number)):
                    paragraph.append(node)
                paragraph.append(run(")"))
                if label:
                    original_start = etree.Element(W + "bookmarkStart")
                    original_start.set(W + "id", str(next_id + 1))
                    original_start.set(W + "name", label)
                    original_end = etree.Element(W + "bookmarkEnd")
                    original_end.set(W + "id", str(next_id + 1))
                    paragraph.insert(0, original_start)
                    paragraph.append(original_end)
                    targets[label] = (bookmark, str(eq_number), "eq")
                    next_id += 2
                else:
                    next_id += 1

        for hyperlink in list(root.xpath(".//w:hyperlink[@w:anchor]", namespaces=NS)):
            anchor = hyperlink.get(W + "anchor")
            if anchor not in targets:
                continue
            bookmark, display, category = targets[anchor]
            unresolved_equation = category == "eq" and text(hyperlink).startswith("[")
            replace_hyperlink(hyperlink, bookmark, display, parentheses=unresolved_equation)

        document_xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(delete=False, suffix=".docx", dir=output_path.parent) as handle:
            temporary = Path(handle.name)
        with ZipFile(temporary, "w", ZIP_DEFLATED) as target:
            for item in archive.infolist():
                target.writestr(
                    item,
                    document_xml if item.filename == "word/document.xml" else archive.read(item.filename),
                )
    temporary.replace(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--tex", type=Path, help="Complete LaTeX entry point; required for equations")
    args = parser.parse_args()
    promote(args.input.resolve(), args.output.resolve(), args.tex.resolve() if args.tex else None)


if __name__ == "__main__":
    main()

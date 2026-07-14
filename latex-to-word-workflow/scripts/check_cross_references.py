from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
INPUT_RE = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
LABEL_RE = re.compile(r"\\label\s*\{([^}]+)\}")
REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref)\s*\{([^}]+)\}")
UNRESOLVED_RE = re.compile(r"\[(?:fig|tab|sec|eq):[^\]]+\]")
# Word field: "REF BookmarkName \h" (switches after the target may vary)
REF_TARGET_RE = re.compile(r"^REF\s+(\S+)", re.I)


def strip_comments(text: str) -> str:
    cleaned: list[str] = []
    for line in text.splitlines():
        match = re.search(r"(?<!\\)%", line)
        cleaned.append(line[: match.start()] if match else line)
    return "\n".join(cleaned)


def resolve_include(parent: Path, raw_name: str) -> Path:
    candidate = (parent / raw_name.strip()).resolve()
    return candidate if candidate.suffix else candidate.with_suffix(".tex")


def expand_tex(path: Path, stack: tuple[Path, ...] = ()) -> tuple[str, list[Path]]:
    resolved = path.resolve()
    if resolved in stack:
        chain = " -> ".join(str(item) for item in (*stack, resolved))
        raise RuntimeError(f"Cyclic LaTeX include: {chain}")
    if not resolved.exists():
        raise FileNotFoundError(f"LaTeX source not found: {resolved}")

    source = strip_comments(resolved.read_text(encoding="utf-8"))
    parts: list[str] = []
    files = [resolved]
    cursor = 0
    for match in INPUT_RE.finditer(source):
        parts.append(source[cursor : match.start()])
        included_path = resolve_include(resolved.parent, match.group(1))
        included_text, included_files = expand_tex(included_path, (*stack, resolved))
        parts.append(included_text)
        files.extend(included_files)
        cursor = match.end()
    parts.append(source[cursor:])
    return "\n".join(parts), files


def tex_report(entry_point: Path) -> dict:
    expanded, files = expand_tex(entry_point)
    labels = LABEL_RE.findall(expanded)
    references: list[str] = []
    for group in REF_RE.findall(expanded):
        references.extend(item.strip() for item in group.split(",") if item.strip())

    label_counts = Counter(labels)
    reference_counts = Counter(references)
    return {
        "entry_point": str(entry_point.resolve()),
        "expanded_files": [str(item) for item in dict.fromkeys(files)],
        "label_count": len(labels),
        "unique_label_count": len(label_counts),
        "reference_count": len(references),
        "unique_reference_count": len(reference_counts),
        "labels": sorted(label_counts),
        "reference_counts": dict(sorted(reference_counts.items())),
        "duplicate_labels": sorted(
            label for label, count in label_counts.items() if count > 1
        ),
        "missing_labels": sorted(set(reference_counts) - set(label_counts)),
        "unreferenced_labels": sorted(set(label_counts) - set(reference_counts)),
    }


def document_xml(path: Path) -> ET.Element:
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read("word/document.xml"))


def field_instructions(root: ET.Element) -> list[str]:
    instructions = [node.text or "" for node in root.iter(f"{W}instrText")]
    instructions.extend(
        node.attrib.get(f"{W}instr", "") for node in root.iter(f"{W}fldSimple")
    )
    return [re.sub(r"\s+", " ", item).strip() for item in instructions if item]


def ref_targets(instructions: list[str]) -> list[str]:
    targets: list[str] = []
    for item in instructions:
        match = REF_TARGET_RE.match(item)
        if match:
            targets.append(match.group(1))
    return targets


def docx_report(path: Path, tex: dict | None) -> dict:
    root = document_xml(path)
    bookmark_names = [
        node.attrib.get(f"{W}name", "")
        for node in root.iter(f"{W}bookmarkStart")
        if node.attrib.get(f"{W}name") not in {None, "", "_GoBack"}
    ]
    anchors = [
        node.attrib.get(f"{W}anchor", "")
        for node in root.iter(f"{W}hyperlink")
        if node.attrib.get(f"{W}anchor")
    ]
    instructions = field_instructions(root)
    native_ref_fields = [item for item in instructions if re.match(r"^REF\s", item, re.I)]
    native_seq_fields = [item for item in instructions if re.match(r"^SEQ\s", item, re.I)]
    ref_bookmark_targets = ref_targets(instructions)
    visible_text = "".join(root.itertext())
    unresolved = sorted(set(UNRESOLVED_RE.findall(visible_text)))
    if "Error! Reference source not found." in visible_text:
        unresolved.append("Error! Reference source not found.")

    bookmark_counts = Counter(bookmark_names)
    bookmarks = set(bookmark_names)
    anchor_counts = Counter(anchors)
    missing_ref_targets = sorted(
        {target for target in ref_bookmark_targets if target not in bookmarks}
    )
    report = {
        "path": str(path.resolve()),
        "bookmark_count": len(bookmark_names),
        "unique_bookmark_count": len(bookmarks),
        "duplicate_bookmark_names": sorted(
            name for name, count in bookmark_counts.items() if count > 1
        ),
        "internal_hyperlink_count": len(anchors),
        "native_ref_field_count": len(native_ref_fields),
        "native_seq_field_count": len(native_seq_fields),
        "native_ref_targets": ref_bookmark_targets,
        "missing_native_ref_targets": missing_ref_targets,
        "cross_reference_mode": (
            "native_word_fields"
            if native_ref_fields or native_seq_fields
            else "static_internal_hyperlinks"
            if anchors
            else "none"
        ),
        "dangling_internal_hyperlinks": sorted(set(anchors) - bookmarks),
        "unresolved_tokens": unresolved,
    }

    if tex:
        reference_counts = Counter(tex["reference_counts"])
        report["referenced_labels_missing_from_docx_bookmarks"] = sorted(
            set(reference_counts) - bookmarks
        )
        report["reference_occurrence_shortfalls"] = {
            label: {"expected": count, "found_static_hyperlinks": anchor_counts[label]}
            for label, count in sorted(reference_counts.items())
            if anchor_counts[label] < count and not native_ref_fields
        }
        covered_occurrences = len(anchors) + len(native_ref_fields)
        report["total_reference_occurrence_shortfall"] = max(
            0, sum(reference_counts.values()) - covered_occurrences
        )
    return report


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description=(
            "Audit LaTeX labels/references and the bookmarks, internal hyperlinks, "
            "and Word REF/SEQ fields in a DOCX generated from the complete entry point."
        )
    )
    parser.add_argument("--tex", type=Path, help="Complete LaTeX entry point")
    parser.add_argument("--docx", type=Path, help="Generated DOCX to inspect")
    parser.add_argument("--require-native-word-fields", action="store_true")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()
    if not args.tex and not args.docx:
        parser.error("provide --tex, --docx, or both")

    report: dict = {}
    failures: list[str] = []
    try:
        tex = tex_report(args.tex) if args.tex else None
        if tex:
            report["latex"] = tex
            if tex["duplicate_labels"]:
                failures.append("duplicate LaTeX labels")
            if tex["missing_labels"]:
                failures.append("LaTeX references with no label")

        if args.docx:
            docx = docx_report(args.docx, tex)
            report["docx"] = docx
            if docx["dangling_internal_hyperlinks"]:
                failures.append("dangling DOCX internal hyperlinks")
            if docx["missing_native_ref_targets"]:
                failures.append("native REF fields point to missing bookmarks")
            if docx["duplicate_bookmark_names"]:
                failures.append("duplicate DOCX bookmark names")
            if docx["unresolved_tokens"]:
                failures.append("unresolved cross-reference tokens in DOCX")
            if docx.get("referenced_labels_missing_from_docx_bookmarks"):
                failures.append("referenced LaTeX labels missing from DOCX bookmarks")
            if docx.get("reference_occurrence_shortfalls"):
                failures.append("fewer DOCX cross-reference links than LaTeX references")
            if docx.get("total_reference_occurrence_shortfall"):
                failures.append("fewer total DOCX REF fields/links than LaTeX references")
            if args.require_native_word_fields and docx["cross_reference_mode"] != "native_word_fields":
                failures.append("native Word REF/SEQ fields required")
    except (BadZipFile, KeyError, ET.ParseError, OSError, RuntimeError) as exc:
        report["error"] = str(exc)
        failures.append("cross-reference audit could not complete")

    report["ok"] = not failures
    report["failures"] = failures
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()

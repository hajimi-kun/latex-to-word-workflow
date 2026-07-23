from __future__ import annotations

import argparse
from collections import Counter
import json
import posixpath
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
W = f"{{{W_NS}}}"
M = f"{{{M_NS}}}"
REL_TAG = f"{{{PKG_REL_NS}}}Relationship"
REL_ATTRS = {f"{{{R_NS}}}id", f"{{{R_NS}}}embed", f"{{{R_NS}}}link"}
FIELD_TARGET_RE = re.compile(r'^(REF|PAGEREF|NOTEREF)\s+(?:"([^"]+)"|(\S+))', re.I)
DOCVAR_RE = re.compile(r'^(DOCVARIABLE)\s+(?:"([^"]+)"|(\S+))', re.I)
UNRESOLVED_MARKERS = (
    "@@XREF",
    "@@ZCITE",
    "Error! Reference source not found.",
    "Error! Bookmark not defined.",
    "[@",
)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def story_part(name: str) -> bool:
    base = posixpath.basename(name)
    return bool(
        name.startswith("word/")
        and re.fullmatch(r"(?:document|header\d+|footer\d+|footnotes|endnotes|comments)\.xml", base)
    )


def normalize_instruction(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_fields(root: ET.Element, part: str) -> list[dict]:
    fields: list[dict] = []
    for node in root.iter(f"{W}fldSimple"):
        instruction = normalize_instruction(node.attrib.get(f"{W}instr", ""))
        if instruction:
            fields.append({"part": part, "instruction": instruction})

    stack: list[dict] = []
    for node in root.iter():
        if node.tag == f"{W}fldChar":
            kind = node.attrib.get(f"{W}fldCharType")
            if kind == "begin":
                stack.append({"instruction": [], "collect": True})
            elif kind == "separate" and stack:
                stack[-1]["collect"] = False
            elif kind == "end" and stack:
                item = stack.pop()
                instruction = normalize_instruction("".join(item["instruction"]))
                if instruction:
                    fields.append({"part": part, "instruction": instruction})
        elif node.tag == f"{W}instrText" and stack and stack[-1]["collect"]:
            stack[-1]["instruction"].append(node.text or "")
    return fields


def classify_field(instruction: str) -> str:
    upper = instruction.upper()
    if upper.startswith("ADDIN ZOTERO_ITEM CSL_CITATION"):
        return "ZOTERO_CITATION"
    if upper.startswith("ADDIN ZOTERO_BIBL"):
        return "ZOTERO_BIBLIOGRAPHY"
    return upper.split(" ", 1)[0] if upper else "UNKNOWN"


def bookmark_scopes(root: ET.Element, part: str) -> tuple[list[dict], list[str]]:
    flat = list(root.iter())
    ends = {
        node.attrib.get(f"{W}id"): index
        for index, node in enumerate(flat)
        if node.tag == f"{W}bookmarkEnd"
    }
    scopes: list[dict] = []
    unmatched: list[str] = []
    for start_index, node in enumerate(flat):
        if node.tag != f"{W}bookmarkStart":
            continue
        name = node.attrib.get(f"{W}name", "")
        bookmark_id = node.attrib.get(f"{W}id")
        if not name or name == "_GoBack":
            continue
        end_index = ends.get(bookmark_id)
        if end_index is None or end_index < start_index:
            unmatched.append(name)
            continue
        enclosed = flat[start_index + 1 : end_index]
        text = "".join(item.text or "" for item in enclosed if item.tag == f"{W}t")
        scopes.append(
            {
                "part": part,
                "name": name,
                "text": text[:200],
                "text_length": len(text),
                "paragraphs": sum(item.tag == f"{W}p" for item in enclosed),
                "tables": sum(item.tag == f"{W}tbl" for item in enclosed),
                "drawings": sum(item.tag == f"{W}drawing" for item in enclosed),
                "math_objects": sum(item.tag in {f"{M}oMath", f"{M}oMathPara"} for item in enclosed),
            }
        )
    return scopes, unmatched


def part_summary(root: ET.Element) -> dict:
    paragraph_styles = Counter(
        node.attrib.get(f"{W}val", "")
        for node in root.iter(f"{W}pStyle")
        if node.attrib.get(f"{W}val")
    )
    character_styles = Counter(
        node.attrib.get(f"{W}val", "")
        for node in root.iter(f"{W}rStyle")
        if node.attrib.get(f"{W}val")
    )
    table_styles = Counter(
        node.attrib.get(f"{W}val", "")
        for node in root.iter(f"{W}tblStyle")
        if node.attrib.get(f"{W}val")
    )
    return {
        "paragraphs": sum(1 for _ in root.iter(f"{W}p")),
        "tables": sum(1 for _ in root.iter(f"{W}tbl")),
        "drawings": sum(1 for _ in root.iter(f"{W}drawing")),
        "math_objects": sum(1 for node in root.iter() if node.tag in {f"{M}oMath", f"{M}oMathPara"}),
        "paragraph_styles": dict(sorted(paragraph_styles.items())),
        "character_styles": dict(sorted(character_styles.items())),
        "table_styles": dict(sorted(table_styles.items())),
    }


def relationship_source(rel_path: str) -> str | None:
    if rel_path == "_rels/.rels":
        return None
    directory, filename = posixpath.split(rel_path)
    if posixpath.basename(directory) != "_rels" or not filename.endswith(".rels"):
        return None
    source_dir = posixpath.dirname(directory)
    return posixpath.join(source_dir, filename[:-5])


def relationship_audit(names: set[str], roots: dict[str, ET.Element]) -> dict:
    missing_ids: list[dict] = []
    missing_targets: list[dict] = []
    for rel_path, rel_root in roots.items():
        if not rel_path.endswith(".rels"):
            continue
        source = relationship_source(rel_path)
        defined: dict[str, ET.Element] = {
            node.attrib.get("Id", ""): node for node in rel_root.iter(REL_TAG)
        }
        if source and source in roots:
            used = {
                value
                for node in roots[source].iter()
                for key, value in node.attrib.items()
                if key in REL_ATTRS
            }
            for rel_id in sorted(used - set(defined)):
                missing_ids.append({"source": source, "relationship_id": rel_id})
        for rel_id, node in defined.items():
            if node.attrib.get("TargetMode", "").lower() == "external":
                continue
            target = node.attrib.get("Target", "")
            base = posixpath.dirname(source) if source else ""
            resolved = posixpath.normpath(posixpath.join(base, target)).lstrip("/")
            if target and resolved not in names:
                missing_targets.append(
                    {"source": source or "package", "relationship_id": rel_id, "target": resolved}
                )
    return {"missing_relationship_ids": missing_ids, "missing_internal_targets": missing_targets}


def load_json(path: Path | None) -> dict | None:
    if path is None:
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def count_delta(before: dict, after: dict, keys: tuple[str, ...]) -> dict:
    return {key: after.get(key, 0) - before.get(key, 0) for key in keys}


def audit(path: Path, latex: dict | None, baseline: dict | None) -> tuple[dict, list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []
    required = {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}
    try:
        with ZipFile(path) as archive:
            names = set(archive.namelist())
            corrupt = archive.testzip()
            roots: dict[str, ET.Element] = {}
            xml_errors: list[dict] = []
            for name in sorted(item for item in names if item.endswith((".xml", ".rels"))):
                try:
                    roots[name] = ET.fromstring(archive.read(name))
                except ET.ParseError as exc:
                    xml_errors.append({"part": name, "error": str(exc)})
            raw_parts = {name: archive.read(name) for name in names if name.endswith(".xml")}
    except (BadZipFile, OSError) as exc:
        return (
            {"schema_version": 1, "kind": "docx-audit", "path": str(path.resolve()), "error": str(exc)},
            ["DOCX package could not be opened"],
            [],
        )

    missing_required = sorted(required - names)
    if corrupt:
        failures.append(f"corrupt ZIP member: {corrupt}")
    if missing_required:
        failures.append("required DOCX package parts are missing")
    if xml_errors:
        failures.append("one or more XML parts are malformed")

    relationships = relationship_audit(names, roots)
    if relationships["missing_relationship_ids"]:
        failures.append("OpenXML relationship IDs are missing")
    if relationships["missing_internal_targets"]:
        failures.append("OpenXML internal relationship targets are missing")

    parts: dict[str, dict] = {}
    fields: list[dict] = []
    scopes: list[dict] = []
    unmatched_bookmarks: list[dict] = []
    for name, root in roots.items():
        if not story_part(name):
            continue
        parts[name] = part_summary(root)
        fields.extend(extract_fields(root, name))
        part_scopes, unmatched = bookmark_scopes(root, name)
        scopes.extend(part_scopes)
        unmatched_bookmarks.extend({"part": name, "name": item} for item in unmatched)

    for field in fields:
        field["type"] = classify_field(field["instruction"])
    field_counts = Counter(field["type"] for field in fields)
    field_part_counts = Counter(f"{field['part']}::{field['type']}" for field in fields)
    bookmark_counts = Counter(scope["name"] for scope in scopes)
    duplicate_bookmarks = sorted(name for name, count in bookmark_counts.items() if count > 1)
    scope_by_name = {scope["name"]: scope for scope in scopes}

    settings = roots.get("word/settings.xml")
    docvars = set()
    if settings is not None:
        docvars = {
            node.attrib.get(f"{W}name", "")
            for node in settings.iter(f"{W}docVar")
            if node.attrib.get(f"{W}name")
        }

    field_targets: list[dict] = []
    missing_targets: list[dict] = []
    overbroad_targets: list[dict] = []
    long_target_warnings: list[dict] = []
    for field in fields:
        match = FIELD_TARGET_RE.match(field["instruction"])
        docvar_match = DOCVAR_RE.match(field["instruction"])
        target_type = None
        target = None
        if match:
            target_type = match.group(1).upper()
            target = match.group(2) or match.group(3)
        elif docvar_match:
            target_type = "DOCVARIABLE"
            target = docvar_match.group(2) or docvar_match.group(3)
        if not target:
            continue
        scope = scope_by_name.get(target) if target_type != "DOCVARIABLE" else None
        target_record = {"part": field["part"], "type": target_type, "target": target, "scope": scope}
        field_targets.append(target_record)
        exists = target in docvars if target_type == "DOCVARIABLE" else target in scope_by_name
        if not exists:
            missing_targets.append(target_record)
        if scope and (scope["tables"] or scope["drawings"] or scope["math_objects"]):
            overbroad_targets.append(target_record)
        elif scope and (scope["paragraphs"] > 1 or scope["text_length"] > 80):
            long_target_warnings.append(target_record)

    if duplicate_bookmarks:
        failures.append("duplicate bookmark names")
    if unmatched_bookmarks:
        failures.append("bookmark starts have no matching end")
    if missing_targets:
        failures.append("native fields point to missing bookmarks or document variables")
    if overbroad_targets:
        failures.append("native cross-reference targets contain a drawing, table, or math object")
    if long_target_warnings:
        warnings.append("one or more native targets have broad text/paragraph scope; inspect manually")

    unresolved: list[dict] = []
    for name, data in raw_parts.items():
        decoded = data.decode("utf-8", errors="replace")
        for marker in UNRESOLVED_MARKERS:
            if marker in decoded:
                unresolved.append({"part": name, "marker": marker, "count": decoded.count(marker)})
    if unresolved:
        failures.append("unresolved conversion or reference markers remain")

    native_types = {"REF", "PAGEREF", "NOTEREF", "DOCVARIABLE"}
    native_count = sum(field_counts.get(name, 0) for name in native_types)
    zotero_count = field_counts.get("ZOTERO_CITATION", 0)
    latex_comparison = None
    if latex:
        source_summary = latex.get("summary", {})
        expected_refs = source_summary.get("reference_occurrence_count", 0)
        expected_cites = source_summary.get("citation_command_count", 0)
        latex_comparison = {
            "source_reference_occurrences": expected_refs,
            "native_crossreference_fields": native_count,
            "reference_field_delta": native_count - expected_refs,
            "source_citation_commands": expected_cites,
            "zotero_citation_fields": zotero_count,
            "citation_field_delta": zotero_count - expected_cites,
            "source_figure_environments": source_summary.get("figure_environment_count", 0),
            "docx_drawings": parts.get("word/document.xml", {}).get("drawings", 0),
            "source_table_environments": source_summary.get("table_environment_count", 0),
            "docx_tables": parts.get("word/document.xml", {}).get("tables", 0),
        }
        if native_count != expected_refs:
            warnings.append("native cross-reference field count differs from source occurrence count; reconcile semantically")
        if zotero_count != expected_cites:
            warnings.append("Zotero citation field count differs from source citation command count; reconcile semantically")

    baseline_comparison = None
    if baseline:
        before_parts = baseline.get("parts", {}).get("word/document.xml", {})
        after_parts = parts.get("word/document.xml", {})
        before_fields = baseline.get("field_counts", {})
        baseline_comparison = {
            "main_story_delta": count_delta(before_parts, after_parts, ("paragraphs", "tables", "drawings", "math_objects")),
            "field_delta": {
                key: field_counts.get(key, 0) - before_fields.get(key, 0)
                for key in sorted(set(before_fields) | set(field_counts))
            },
            "bookmark_count_delta": len(scopes) - len(baseline.get("bookmarks", [])),
        }
        structural = baseline_comparison["main_story_delta"]
        if structural["tables"] or structural["drawings"]:
            failures.append("table or drawing counts changed during the Word/Zotero round trip")
        if baseline_comparison["field_delta"].get("ZOTERO_CITATION", 0) < 0:
            failures.append("Zotero citation fields were lost during the round trip")
        if sum(baseline_comparison["field_delta"].get(name, 0) for name in native_types) < 0:
            failures.append("native cross-reference fields were lost during the round trip")
        if structural["paragraphs"] or structural["math_objects"] or baseline_comparison["bookmark_count_delta"]:
            warnings.append("the Word/Zotero round trip changed document structure; classify each reported delta")

    report = {
        "schema_version": 1,
        "kind": "docx-audit",
        "path": str(path.resolve()),
        "package": {
            "zip_valid": corrupt is None,
            "missing_required_parts": missing_required,
            "xml_errors": xml_errors,
        },
        "relationships": relationships,
        "parts": parts,
        "field_counts": dict(sorted(field_counts.items())),
        "field_part_counts": dict(sorted(field_part_counts.items())),
        "fields": fields,
        "field_targets": field_targets,
        "missing_field_targets": missing_targets,
        "overbroad_field_targets": overbroad_targets,
        "broad_text_target_warnings": long_target_warnings,
        "bookmarks": scopes,
        "duplicate_bookmark_names": duplicate_bookmarks,
        "unmatched_bookmark_starts": unmatched_bookmarks,
        "document_variables": sorted(docvars),
        "unresolved_markers": unresolved,
        "latex_comparison": latex_comparison,
        "baseline_comparison": baseline_comparison,
    }
    return report, failures, warnings


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Audit a DOCX package, Word fields, bookmark scopes, and refresh stability without modifying it.")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--latex-manifest", type=Path)
    parser.add_argument("--baseline", type=Path, help="Audit JSON produced before the user Word/Zotero refresh")
    parser.add_argument("--require-native-crossrefs", action="store_true")
    parser.add_argument(
        "--require-zotero-fields",
        "--require-zotero-live",
        dest="require_zotero_fields",
        action="store_true",
        help="Require generated Zotero field presence; this does not prove Refresh occurred",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    failures: list[str] = []
    warnings: list[str] = []
    try:
        latex = load_json(args.latex_manifest)
        baseline = load_json(args.baseline)
        report, audit_failures, warnings = audit(args.docx, latex, baseline)
        failures.extend(audit_failures)
        field_counts = report.get("field_counts", {})
        native_count = sum(field_counts.get(name, 0) for name in ("REF", "PAGEREF", "NOTEREF", "DOCVARIABLE"))
        zotero_count = field_counts.get("ZOTERO_CITATION", 0)
        if args.require_native_crossrefs:
            expected = (latex or {}).get("summary", {}).get("reference_occurrence_count")
            if expected is None and native_count == 0:
                failures.append("native Word cross-reference fields are required but none were found")
            elif expected is not None and native_count < expected:
                failures.append("fewer native Word cross-reference fields than LaTeX reference occurrences")
        if args.require_zotero_fields:
            expected = (latex or {}).get("summary", {}).get("citation_command_count")
            if expected is None and zotero_count == 0:
                failures.append("Zotero-live citation fields are required but none were found")
            elif expected is not None and zotero_count < expected:
                failures.append("fewer Zotero citation fields than LaTeX citation commands")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        report = {"schema_version": 1, "kind": "docx-audit", "path": str(args.docx.resolve()), "error": str(exc)}
        failures.append("audit inputs could not be read")

    report["ok"] = not failures
    report["failures"] = list(dict.fromkeys(failures))
    report["warnings"] = list(dict.fromkeys(warnings))
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()

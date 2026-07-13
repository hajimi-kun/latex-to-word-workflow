from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from docx import Document
from lxml import etree


REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Validate DOCX structure, relationships, content counts, and Zotero fields.")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--expect-zotero", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report: dict = {"path": str(args.docx.resolve()), "zip_valid": False, "missing_relationships": []}
    try:
        with ZipFile(args.docx) as archive:
            report["zip_valid"] = True
            xml = etree.fromstring(archive.read("word/document.xml"))
            rels = etree.fromstring(archive.read("word/_rels/document.xml.rels"))
            used = set(xml.xpath("//@r:id | //@r:embed | //@r:link", namespaces={"r": REL_NS}))
            defined = {node.get("Id") for node in rels}
            report["missing_relationships"] = sorted(used - defined)
            text = archive.read("word/document.xml").decode("utf-8", errors="replace")
            report["zotero_citation_fields"] = text.count("ADDIN ZOTERO_ITEM CSL_CITATION")
    except (BadZipFile, KeyError, etree.XMLSyntaxError) as exc:
        report["zip_error"] = str(exc)

    try:
        doc = Document(args.docx)
        report.update({
            "paragraphs": len(doc.paragraphs),
            "tables": len(doc.tables),
            "images": len(doc.inline_shapes),
            "styles": sorted({paragraph.style.name for paragraph in doc.paragraphs if paragraph.style}),
        })
    except Exception as exc:
        report["python_docx_error"] = str(exc)

    failures = []
    if not report["zip_valid"]:
        failures.append("invalid ZIP/DOCX package")
    if report["missing_relationships"]:
        failures.append("missing OpenXML relationships")
    if "python_docx_error" in report:
        failures.append("python-docx could not load the document")
    if args.expect_zotero is not None and report.get("zotero_citation_fields") != args.expect_zotero:
        failures.append(f"expected {args.expect_zotero} Zotero fields")
    report["ok"] = not failures
    report["failures"] = failures
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()

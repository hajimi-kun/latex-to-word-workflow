from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "latex-to-word-workflow" / "scripts"


def load_script(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


latex_manifest = load_script("latex_manifest")
docx_audit = load_script("docx_audit")


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

PACKAGE_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

EMPTY_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""


def complex_field(instruction: str, result: str = "1") -> str:
    return f"""
    <w:r><w:fldChar w:fldCharType="begin"/></w:r>
    <w:r><w:instrText xml:space="preserve"> {instruction} </w:instrText></w:r>
    <w:r><w:fldChar w:fldCharType="separate"/></w:r>
    <w:r><w:t>{result}</w:t></w:r>
    <w:r><w:fldChar w:fldCharType="end"/></w:r>
    """


def document_xml(overbroad: bool = False) -> str:
    scope = "<w:drawing/>" if overbroad else "<w:r><w:t>1</w:t></w:r>"
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:bookmarkStart w:id="1" w:name="fig_one"/>
      {scope}
      <w:bookmarkEnd w:id="1"/>
    </w:p>
    <w:p>{complex_field('REF fig_one \\h')}</w:p>
    <w:p>{complex_field('ADDIN ZOTERO_ITEM CSL_CITATION {}', '[1]')}</w:p>
    <w:sectPr/>
  </w:body>
</w:document>
"""


def make_docx(path: Path, overbroad: bool = False) -> None:
    with ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", PACKAGE_RELS)
        archive.writestr("word/document.xml", document_xml(overbroad))
        archive.writestr("word/_rels/document.xml.rels", EMPTY_RELS)


class ReadOnlyScriptTests(unittest.TestCase):
    def test_latex_manifest_recurses_and_counts_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "main.tex").write_text(
                "\\newcommand{\\figref}[1]{Fig.~\\ref{#1}}\n"
                "\\input{section}\n\\cite{alpha,beta}\n\\nocite{gamma}\n\\figref{fig:one}\n",
                encoding="utf-8",
            )
            (root / "section.tex").write_text(
                "\\section*{Acknowledgments}\n\\begin{figure}\\label{fig:one}\\end{figure}\n",
                encoding="utf-8",
            )

            report = latex_manifest.manifest(root / "main.tex")

            self.assertEqual(report["summary"]["source_file_count"], 2)
            self.assertEqual(report["summary"]["reference_occurrence_count"], 1)
            self.assertEqual(report["summary"]["citation_command_count"], 1)
            self.assertEqual(report["summary"]["nocite_command_count"], 1)
            self.assertEqual(report["summary"]["unique_cited_key_count"], 2)
            self.assertEqual(report["nocite_keys"], ["gamma"])
            self.assertTrue(report["sections"][0]["starred"])
            self.assertEqual(report["referenced_labels_without_definition"], [])
            self.assertEqual(report["reference_wrapper_macros"], ["figref"])

    def test_docx_audit_accepts_native_and_zotero_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            docx = Path(temporary) / "candidate.docx"
            make_docx(docx)
            latex = {
                "summary": {
                    "reference_occurrence_count": 1,
                    "citation_command_count": 1,
                    "figure_environment_count": 1,
                    "table_environment_count": 0,
                }
            }

            report, failures, warnings = docx_audit.audit(docx, latex, None)

            self.assertEqual(failures, [])
            self.assertEqual(warnings, [])
            self.assertEqual(report["field_counts"]["REF"], 1)
            self.assertEqual(report["field_counts"]["ZOTERO_CITATION"], 1)
            self.assertEqual(report["missing_field_targets"], [])

    def test_docx_audit_rejects_whole_object_ref_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            docx = Path(temporary) / "overbroad.docx"
            make_docx(docx, overbroad=True)

            report, failures, _ = docx_audit.audit(docx, None, None)

            self.assertIn(
                "native cross-reference targets contain a drawing, table, or math object",
                failures,
            )
            self.assertEqual(report["overbroad_field_targets"][0]["target"], "fig_one")

    def test_identical_baseline_has_no_structural_delta(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            docx = Path(temporary) / "candidate.docx"
            make_docx(docx)
            baseline, failures, _ = docx_audit.audit(docx, None, None)
            self.assertEqual(failures, [])

            report, failures, warnings = docx_audit.audit(docx, None, json.loads(json.dumps(baseline)))

            self.assertEqual(failures, [])
            self.assertEqual(warnings, [])
            self.assertEqual(report["baseline_comparison"]["main_story_delta"]["drawings"], 0)


if __name__ == "__main__":
    unittest.main()

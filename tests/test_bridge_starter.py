from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "latex-to-word-workflow" / "scripts"
STARTER = ROOT / "latex-to-word-workflow" / "examples" / "bridge-starter"


def load_script(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


docx_bridge = load_script("docx_bridge")
init_bridge = load_script("init_bridge")


class BridgeStarterTests(unittest.TestCase):
    def test_field_and_bookmark_helpers_create_tight_native_structure(self) -> None:
        root = ET.Element(docx_bridge.qn("w:document"))
        paragraph = ET.SubElement(root, docx_bridge.qn("w:p"))
        allocator = docx_bridge.BookmarkAllocator(root)
        nodes = docx_bridge.bookmarked_field(
            "RefNativeFig001",
            allocator.next(),
            r"SEQ Figure \* ARABIC",
            "1",
            bold=True,
        )
        paragraph.extend(nodes)

        xml = ET.tostring(root, encoding="unicode")
        self.assertIn("SEQ Figure", xml)
        self.assertIn("RefNativeFig001", xml)
        self.assertEqual(len(list(root.iter(docx_bridge.qn("w:bookmarkStart")))), 1)
        self.assertEqual(len(list(root.iter(docx_bridge.qn("w:bookmarkEnd")))), 1)

    def test_style_remap_changes_only_configured_styles(self) -> None:
        root = ET.Element(docx_bridge.qn("w:document"))
        first = ET.SubElement(root, docx_bridge.qn("w:p"))
        second = ET.SubElement(root, docx_bridge.qn("w:p"))
        docx_bridge.set_paragraph_style(first, "Compact")
        docx_bridge.set_paragraph_style(second, "Heading1")

        changed = docx_bridge.apply_style_remaps(root, {"Compact": "BodyText"})

        self.assertEqual(changed, 1)
        self.assertEqual(docx_bridge.paragraph_style(first), "BodyText")
        self.assertEqual(docx_bridge.paragraph_style(second), "Heading1")

    def test_config_rejects_unconfigured_required_roles(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            path.write_text(
                json.dumps({
                    "schema_version": 1,
                    "required_roles": ["body"],
                    "role_styles": {"body": "__SET_ME__"},
                }),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unconfigured role styles"):
                docx_bridge.load_config(path)

    def test_starter_config_has_no_template_or_genre_defaults(self) -> None:
        config = json.loads((STARTER / "bridge_config.json").read_text(encoding="utf-8"))

        self.assertEqual(config["required_roles"], ["__SET_ME__"])
        self.assertEqual(config["role_styles"], {"__SET_ME__": "__SET_ME__"})
        self.assertTrue(all(value == "__SET_ME__" for value in config["captions"].values()))
        self.assertEqual(config["equations"], {"container": "__SET_ME__"})

        with self.assertRaisesRegex(ValueError, "unconfigured role styles"):
            docx_bridge.load_config(STARTER / "bridge_config.json")

    def test_initializer_copies_canonical_starter_and_engine(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "bridge"
            created = init_bridge.initialize(destination)

            self.assertEqual(
                {path.name for path in created},
                {"bridge_config.json", "project_adapter.py", "semantic_filter.lua", "docx_bridge.py"},
            )
            with self.assertRaises(FileExistsError):
                init_bridge.initialize(destination)

    def test_docx_package_preserves_parts_and_updates_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.docx"
            output = root / "output.docx"
            document = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                f'<w:document xmlns:w="{docx_bridge.W}"><w:body><w:p/></w:body></w:document>'
            )
            with ZipFile(source, "w") as archive:
                archive.writestr("word/document.xml", document)
                archive.writestr("custom/preserved.txt", "keep")

            package = docx_bridge.DocxPackage(source)
            xml_root = package.xml()
            paragraph = next(xml_root.iter(docx_bridge.qn("w:p")))
            paragraph.append(docx_bridge.text_run("updated"))
            package.set_xml(xml_root)
            package.write(output)

            with ZipFile(output) as archive:
                self.assertEqual(archive.read("custom/preserved.txt"), b"keep")
                self.assertIn(b"updated", archive.read("word/document.xml"))


if __name__ == "__main__":
    unittest.main()

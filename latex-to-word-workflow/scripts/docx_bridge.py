from __future__ import annotations

import copy
import json
import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML = "http://www.w3.org/XML/1998/namespace"
NS = {"w": W}
ET.register_namespace("w", W)


def qn(name: str) -> str:
    prefix, local = name.split(":", 1)
    if prefix != "w":
        raise ValueError(f"unsupported namespace prefix: {prefix}")
    return f"{{{W}}}{local}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.iter(qn("w:t")))


def paragraph_style(paragraph: ET.Element) -> str | None:
    style = paragraph.find("w:pPr/w:pStyle", NS)
    return style.get(qn("w:val")) if style is not None else None


def set_paragraph_style(paragraph: ET.Element, style_id: str) -> None:
    ppr = paragraph.find("w:pPr", NS)
    if ppr is None:
        ppr = ET.Element(qn("w:pPr"))
        paragraph.insert(0, ppr)
    style = ppr.find("w:pStyle", NS)
    if style is None:
        style = ET.Element(qn("w:pStyle"))
        ppr.insert(0, style)
    style.set(qn("w:val"), style_id)


def text_run(
    text: str,
    *,
    bold: bool = False,
    italic: bool = False,
    vertical: str | None = None,
) -> ET.Element:
    run = ET.Element(qn("w:r"))
    if bold or italic or vertical:
        rpr = ET.SubElement(run, qn("w:rPr"))
        if bold:
            ET.SubElement(rpr, qn("w:b"))
        if italic:
            ET.SubElement(rpr, qn("w:i"))
        if vertical:
            vert = ET.SubElement(rpr, qn("w:vertAlign"))
            vert.set(qn("w:val"), vertical)
    node = ET.SubElement(run, qn("w:t"))
    if text[:1].isspace() or text[-1:].isspace():
        node.set(f"{{{XML}}}space", "preserve")
    node.text = text
    return run


def field_runs(
    instruction: str,
    display: str,
    *,
    bold: bool = False,
) -> list[ET.Element]:
    begin = ET.Element(qn("w:r"))
    begin_char = ET.SubElement(begin, qn("w:fldChar"))
    begin_char.set(qn("w:fldCharType"), "begin")

    code = ET.Element(qn("w:r"))
    instruction_node = ET.SubElement(code, qn("w:instrText"))
    instruction_node.set(f"{{{XML}}}space", "preserve")
    instruction_node.text = f" {instruction.strip()} "

    separate = ET.Element(qn("w:r"))
    separate_char = ET.SubElement(separate, qn("w:fldChar"))
    separate_char.set(qn("w:fldCharType"), "separate")

    result = text_run(display, bold=bold)

    end = ET.Element(qn("w:r"))
    end_char = ET.SubElement(end, qn("w:fldChar"))
    end_char.set(qn("w:fldCharType"), "end")
    return [begin, code, separate, result, end]


class BookmarkAllocator:
    def __init__(self, root: ET.Element, floor: int = 8000) -> None:
        used = {
            int(node.get(qn("w:id")))
            for node in root.iter(qn("w:bookmarkStart"))
            if (node.get(qn("w:id")) or "").isdigit()
        }
        self._next = max([floor, *used])

    def next(self) -> int:
        self._next += 1
        return self._next


def bookmarked_field(
    name: str,
    bookmark_id: int,
    instruction: str,
    display: str,
    *,
    bold: bool = False,
) -> list[ET.Element]:
    start = ET.Element(qn("w:bookmarkStart"))
    start.set(qn("w:id"), str(bookmark_id))
    start.set(qn("w:name"), name)
    end = ET.Element(qn("w:bookmarkEnd"))
    end.set(qn("w:id"), str(bookmark_id))
    return [start, *field_runs(instruction, display, bold=bold), end]


def replace_child(
    parent: ET.Element,
    old: ET.Element,
    replacements: list[ET.Element],
) -> None:
    index = list(parent).index(old)
    parent.remove(old)
    for offset, replacement in enumerate(replacements):
        parent.insert(index + offset, replacement)


def replace_hyperlink_with_ref(
    parent: ET.Element,
    hyperlink: ET.Element,
    bookmark: str,
    display: str,
    *,
    switches: str = r"\h",
) -> None:
    instruction = f"REF {bookmark} {switches}".strip()
    replace_child(parent, hyperlink, field_runs(instruction, display))


def apply_style_remaps(root: ET.Element, remaps: dict[str, str]) -> int:
    changed = 0
    for paragraph in root.iter(qn("w:p")):
        source = paragraph_style(paragraph)
        if source in remaps and remaps[source] != source:
            set_paragraph_style(paragraph, remaps[source])
            changed += 1
    return changed


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("bridge config schema_version must be 1")
    roles = config.get("required_roles", [])
    styles = config.get("role_styles", {})
    missing = [role for role in roles if not styles.get(role) or styles[role] == "__SET_ME__"]
    if missing:
        raise ValueError(f"unconfigured role styles: {', '.join(missing)}")
    return config


class DocxPackage:
    def __init__(self, path: Path) -> None:
        self.path = path
        with ZipFile(path) as archive:
            self._entries: list[tuple[ZipInfo, bytes]] = [
                (copy.copy(info), archive.read(info.filename)) for info in archive.infolist()
            ]
        self._updates: dict[str, bytes] = {}

    def xml(self, part: str = "word/document.xml") -> ET.Element:
        data = self._updates.get(part)
        if data is None:
            data = next((payload for info, payload in self._entries if info.filename == part), None)
        if data is None:
            raise KeyError(f"DOCX part not found: {part}")
        return ET.fromstring(data)

    def set_xml(self, root: ET.Element, part: str = "word/document.xml") -> None:
        self._updates[part] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    def write(self, output: Path) -> None:
        output.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary = tempfile.mkstemp(suffix=".docx", dir=output.parent)
        os.close(handle)
        try:
            with ZipFile(temporary, "w", ZIP_DEFLATED) as archive:
                seen: set[str] = set()
                for info, payload in self._entries:
                    archive.writestr(info, self._updates.get(info.filename, payload))
                    seen.add(info.filename)
                for name, payload in self._updates.items():
                    if name not in seen:
                        archive.writestr(name, payload)
            os.replace(temporary, output)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

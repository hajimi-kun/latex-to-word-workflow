from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


def style(doc: Document, name: str, size: float, *, bold: bool = False,
          alignment=None, first_line: float = 0, before: float = 0, after: float = 0):
    item = doc.styles[name] if name in doc.styles else doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    item.font.name = "Times New Roman"
    item.font.size = Pt(size)
    item.font.bold = bold
    item.paragraph_format.alignment = alignment
    item.paragraph_format.first_line_indent = Cm(first_line)
    item.paragraph_format.space_before = Pt(before)
    item.paragraph_format.space_after = Pt(after)
    item.quick_style = True
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the generic reference.docx bundled with this skill.")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.54)
    section.left_margin = section.right_margin = Cm(2.54)

    normal = style(doc, "Normal", 10.5, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY)
    body = style(doc, "Body Text", 10.5, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, first_line=0.5, after=3)
    body.base_style = normal
    style(doc, "Title", 15, bold=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, after=6)
    style(doc, "Subtitle", 10.5, alignment=WD_ALIGN_PARAGRAPH.CENTER, after=10)
    for name, size, before in (("Heading 1", 13, 14), ("Heading 2", 11.5, 10), ("Heading 3", 10.5, 8)):
        heading = style(doc, name, size, bold=True, before=before, after=4)
        heading.paragraph_format.keep_with_next = True
    figure = style(doc, "Figure", 10.5, alignment=WD_ALIGN_PARAGRAPH.CENTER, before=6, after=3)
    figure.paragraph_format.keep_with_next = True
    style(doc, "Caption", 9, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, after=8)
    style(doc, "Table Body", 9)
    bibliography = style(doc, "Bibliography", 9)
    bibliography.paragraph_format.left_indent = Cm(0.68)
    bibliography.paragraph_format.first_line_indent = Cm(-0.68)

    samples = [
        ("Title", "Example Manuscript Title"),
        ("Subtitle", "Author names and affiliations"),
        ("Heading 1", "1. Introduction"),
        ("Heading 2", "1.1. Background"),
        ("Heading 3", "1.1.1. Detailed heading"),
        ("Body Text", "This paragraph demonstrates the manuscript body style, including first-line indentation, justification, and paragraph spacing."),
        ("Figure", "[FIGURE AREA]"),
        ("Caption", "Figure 1. Example figure caption with enough text to demonstrate alignment and spacing."),
        ("Bibliography", "[1] A. Author, B. Author, Example article title, Journal 10 (2025) 100-110. https://doi.org/10.0000/example."),
    ]
    for name, text in samples:
        doc.add_paragraph(text, style=name)

    table = doc.add_table(rows=2, cols=3)
    table.style = "Table Grid"
    for row_index, row in enumerate(table.rows):
        for column_index, cell in enumerate(row.cells):
            cell.text = ("Variable", "Condition", "Value")[column_index] if row_index == 0 else ("Example", "Baseline", "1.0")[column_index]
            for paragraph in cell.paragraphs:
                paragraph.style = "Table Body"
            if row_index == 0:
                shading = OxmlElement("w:shd")
                shading.set(qn("w:fill"), "E7EAF0")
                cell._tc.get_or_add_tcPr().append(shading)
                for run in cell.paragraphs[0].runs:
                    run.bold = True

    doc.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()

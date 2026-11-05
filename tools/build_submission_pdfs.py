"""Build the PDF documents and presentation deck for the COMP3211 submission."""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Iterable

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
PAGE_WIDTH, PAGE_HEIGHT = A4
INK = colors.HexColor("#162235")
MUTED = colors.HexColor("#526274")
ACCENT = colors.HexColor("#167D9A")
PALE = colors.HexColor("#EAF5F7")
LINE = colors.HexColor("#C8D4DE")


def safe_text(value: str) -> str:
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2011": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value


def inline_markup(value: str) -> str:
    value = safe_text(value)
    code_tokens: list[str] = []

    def save_code(match: re.Match[str]) -> str:
        code_tokens.append(html.escape(match.group(1)))
        return f"@@CODE{len(code_tokens) - 1}@@"

    value = re.sub(r"`([^`]+)`", save_code, value)
    value = html.escape(value, quote=False)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    for index, token in enumerate(code_tokens):
        value = value.replace(
            f"@@CODE{index}@@", f'<font name="Courier">{token}</font>'
        )
    return value


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "SubmissionTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            textColor=INK,
            spaceAfter=8,
        ),
        "meta": ParagraphStyle(
            "SubmissionMeta",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=MUTED,
            spaceAfter=12,
        ),
        "h1": ParagraphStyle(
            "DocH1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=INK,
            spaceBefore=12,
            spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "DocH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=ACCENT,
            spaceBefore=10,
            spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "DocH3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=INK,
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "DocBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=13.2,
            textColor=INK,
            spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "bullet": ParagraphStyle(
            "DocBullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=12.8,
            textColor=INK,
            leftIndent=13,
            firstLineIndent=0,
            spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "DocCode",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.2,
            leading=9.2,
            textColor=INK,
            backColor=PALE,
            borderColor=LINE,
            borderWidth=0.4,
            borderPadding=5,
            spaceBefore=4,
            spaceAfter=6,
        ),
        "table": ParagraphStyle(
            "DocTable",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.2,
            leading=9.2,
            textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "DocTableHead",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.3,
            leading=9.4,
            textColor=colors.white,
        ),
    }


def split_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def wrap_code_lines(code_lines: list[str], max_chars: int = 100) -> list[str]:
    wrapped: list[str] = []
    for original in code_lines:
        line = original.rstrip()
        if len(line) <= max_chars:
            wrapped.append(line)
            continue
        indent = re.match(r"^\s*", line).group(0)
        remaining = line.strip()
        while len(remaining) > max_chars - len(indent) - 1:
            limit = max_chars - len(indent) - 1
            split_at = remaining.rfind(" ", 0, limit + 1)
            if split_at <= 0:
                split_at = limit
            wrapped.append(indent + remaining[:split_at] + "\\")
            remaining = remaining[split_at:].lstrip()
        wrapped.append(indent + remaining)
    return wrapped


def compact_test_references(lines: list[str]) -> list[str]:
    replacements = {
        "tests.model.test_pir.PIRConstructionTests.": "test_pir.py::PIRConstructionTests.",
        "tests.model.test_pir.PIRUpdateTests.": "test_pir.py::PIRUpdateTests.",
        "tests.model.test_search.SearchTests.": "test_search.py::SearchTests.",
        "tests.model.test_repository.RepositoryTests.": "test_repository.py::RepositoryTests.",
        "tests.model.test_persistence.PersistenceTests.": "test_persistence.py::PersistenceTests.",
        "tests.cli.test_cli.CommandParserTests.": "test_cli.py::CommandParserTests.",
        "tests.cli.test_cli.ControllerTests.": "test_cli.py::ControllerTests.",
        "tests.cli.test_cli.ViewTests.": "test_cli.py::ViewTests.",
        "tests.test_main.MainLoopTests.": "test_main.py::MainLoopTests.",
    }
    compacted: list[str] = []
    for line in lines:
        for old, new in replacements.items():
            line = line.replace(old, new)
        compacted.append(line)
    return compacted

def markdown_story(lines: list[str], paragraph_styles: dict[str, ParagraphStyle]) -> list[object]:
    story: list[object] = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        if not line.strip():
            index += 1
            continue
        if line.startswith("```"):
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code_lines.append(safe_text(lines[index].rstrip()))
                index += 1
            if index < len(lines):
                index += 1
            is_mermaid = bool(code_lines) and code_lines[0].strip().startswith(("flowchart", "classDiagram", "sequenceDiagram"))
            if not is_mermaid:
                story.append(Preformatted("\n".join(wrap_code_lines(code_lines)), paragraph_styles["code"]))
            continue
        if line.startswith("# "):
            story.append(Paragraph(inline_markup(line[2:].strip()), paragraph_styles["h1"]))
            index += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(inline_markup(line[3:].strip()), paragraph_styles["h2"]))
            index += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(inline_markup(line[4:].strip()), paragraph_styles["h3"]))
            index += 1
            continue
        if line.startswith("|"):
            table_lines: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            if len(table_lines) >= 2:
                rows = [split_table_row(item) for item in table_lines]
                rows = [row for row in rows if not is_table_separator("|" + "|".join(row) + "|")]
                if rows:
                    columns = max(len(row) for row in rows)
                    normalized = [row + [""] * (columns - len(row)) for row in rows]
                    rendered = []
                    for row_index, row in enumerate(normalized):
                        style_name = "table_head" if row_index == 0 else "table"
                        rendered.append(
                            [Paragraph(inline_markup(cell), paragraph_styles[style_name]) for cell in row]
                        )
                    widths = [8.0 * inch / columns] * columns
                    table = Table(rendered, colWidths=widths, repeatRows=1, hAlign="LEFT")
                    table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                                ("GRID", (0, 0), (-1, -1), 0.35, LINE),
                                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                                ("TOPPADDING", (0, 0), (-1, -1), 4),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                            ]
                        )
                    )
                    story.extend([Spacer(1, 3), table, Spacer(1, 7)])
            continue
        if re.match(r"^[-*] \S", line):
            items: list[ListItem] = []
            while index < len(lines) and re.match(r"^[-*] \S", lines[index].strip()):
                item_text = re.sub(r"^[-*] ", "", lines[index].strip())
                items.append(ListItem(Paragraph(inline_markup(item_text), paragraph_styles["bullet"])))
                index += 1
            story.append(ListFlowable(items, bulletType="bullet", start="circle", leftIndent=16))
            story.append(Spacer(1, 3))
            continue
        if re.match(r"^\d+\. \S", line):
            items = []
            while index < len(lines) and re.match(r"^\d+\. \S", lines[index].strip()):
                item_text = re.sub(r"^\d+\. ", "", lines[index].strip())
                items.append(ListItem(Paragraph(inline_markup(item_text), paragraph_styles["bullet"])))
                index += 1
            story.append(ListFlowable(items, bulletType="1", start="1", leftIndent=18))
            story.append(Spacer(1, 3))
            continue
        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines):
            next_line = lines[index].rstrip()
            if (
                not next_line.strip()
                or next_line.startswith("#")
                or next_line.startswith("```")
                or next_line.startswith("|")
                or re.match(r"^[-*] \S", next_line)
                or re.match(r"^\d+\. \S", next_line)
            ):
                break
            paragraph_lines.append(next_line.strip())
            index += 1
        story.append(Paragraph(inline_markup(" ".join(paragraph_lines)), paragraph_styles["body"]))
    return story


def footer(canvas_obj: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    canvas_obj.saveState()
    canvas_obj.setStrokeColor(LINE)
    canvas_obj.line(doc.leftMargin, 0.52 * inch, PAGE_WIDTH - doc.rightMargin, 0.52 * inch)
    canvas_obj.setFont("Helvetica", 7.5)
    canvas_obj.setFillColor(MUTED)
    canvas_obj.drawString(doc.leftMargin, 0.32 * inch, "Hong Kong Student Second-hand PIM | COMP3211")
    canvas_obj.drawRightString(PAGE_WIDTH - doc.rightMargin, 0.32 * inch, f"Page {doc.page}")
    canvas_obj.restoreState()


def _diagram_box(drawing: Drawing, x: float, y: float, width: float, height: float, label: str, fill) -> None:
    drawing.add(Rect(x, y, width, height, rx=10, ry=10, fillColor=fill, strokeColor=ACCENT, strokeWidth=1.2))
    drawing.add(String(x + width / 2, y + height / 2 - 6, safe_text(label), textAnchor="middle", fontName="Helvetica-Bold", fontSize=12, fillColor=INK))


def _diagram_arrow(drawing: Drawing, x1: float, y1: float, x2: float, y2: float, label: str | None = None) -> None:
    drawing.add(Line(x1, y1, x2, y2, strokeColor=MUTED, strokeWidth=1.4))
    if label:
        drawing.add(String((x1 + x2) / 2, (y1 + y2) / 2 + 5, safe_text(label), textAnchor="middle", fontName="Helvetica", fontSize=8, fillColor=MUTED))


def design_diagrams(paragraph_styles: dict[str, ParagraphStyle]) -> list[object]:
    architecture = Drawing(500, 165)
    _diagram_box(architecture, 12, 92, 100, 38, "Local user", PALE)
    _diagram_box(architecture, 140, 92, 100, 38, "View", PALE)
    _diagram_box(architecture, 268, 92, 100, 38, "Controller", colors.HexColor("#E6F0FA"))
    _diagram_box(architecture, 396, 92, 92, 38, "Model", colors.HexColor("#EAF5ED"))
    _diagram_arrow(architecture, 112, 111, 140, 111, "input")
    _diagram_arrow(architecture, 240, 111, 268, 111, "commands")
    _diagram_arrow(architecture, 368, 111, 396, 111, "operations")
    architecture.add(String(250, 40, "PIRs, criteria, repository, and .pim serializer", textAnchor="middle", fontName="Helvetica", fontSize=10, fillColor=INK))

    components = Drawing(500, 205)
    _diagram_box(components, 25, 130, 125, 38, "CLI: main / parser / view", PALE)
    _diagram_box(components, 188, 130, 125, 38, "Controller + result", colors.HexColor("#E6F0FA"))
    _diagram_box(components, 350, 130, 125, 38, "Model packages", colors.HexColor("#EAF5ED"))
    _diagram_arrow(components, 150, 149, 188, 149)
    _diagram_arrow(components, 313, 149, 350, 149)
    _diagram_box(components, 25, 45, 125, 38, "Criterion tree", colors.HexColor("#FFF5E6"))
    _diagram_box(components, 188, 45, 125, 38, "PIR hierarchy", colors.HexColor("#FFF5E6"))
    _diagram_box(components, 350, 45, 125, 38, "PIMSerializer", colors.HexColor("#FFF5E6"))
    _diagram_arrow(components, 250, 130, 87, 83)
    _diagram_arrow(components, 250, 130, 250, 83)
    _diagram_arrow(components, 412, 130, 412, 83)

    sequence = Drawing(500, 240)
    participants = [(30, "User"), (145, "View"), (260, "Controller"), (375, "Criteria"), (470, "Repo")]
    for x, label in participants:
        sequence.add(String(x, 220, label, textAnchor="middle", fontName="Helvetica-Bold", fontSize=9, fillColor=INK))
        sequence.add(Line(x, 35, x, 210, strokeColor=LINE, strokeWidth=0.8, strokeDashArray=[3, 3]))
    arrows = [
        (30, 145, 190, "enter search"),
        (145, 260, 160, "execute"),
        (260, 375, 130, "parse criterion"),
        (260, 470, 100, "search"),
        (470, 260, 70, "matching PIRs"),
        (260, 145, 50, "result"),
    ]
    for x1, x2, y_pos, label in arrows:
        _diagram_arrow(sequence, x1, y_pos, x2, y_pos, label)
    return [
        Paragraph("Visual design diagrams", paragraph_styles["h1"]),
        Paragraph("The architecture, component relationships, and search sequence are rendered below for the PDF deliverable.", paragraph_styles["body"]),
        Paragraph("Architecture", paragraph_styles["h2"]),
        architecture,
        Spacer(1, 8),
        Paragraph("Main component relationships", paragraph_styles["h2"]),
        components,
        Spacer(1, 8),
        KeepTogether([
            Paragraph("Example use: search then update", paragraph_styles["h2"]),
            sequence,
        ]),
        PageBreak(),
    ]

def build_document_pdf(source: Path, target: Path, title: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = source.read_text(encoding="utf-8").splitlines()
    if title == "Requirements Coverage Report":
        lines = compact_test_references(lines)
    document_styles = styles()
    story: list[object] = [
        Paragraph(inline_markup(title), document_styles["title"]),
        Paragraph("COMP3211 Software Engineering | Fall 2026", document_styles["meta"]),
        HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=10),
    ]
    if title == "Design Document":
        story.extend(design_diagrams(document_styles))
    story.extend(markdown_story(lines, document_styles))
    doc = SimpleDocTemplate(
        str(target),
        pagesize=A4,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.72 * inch,
        title=title,
        author="Hong Kong Student Second-hand PIM project team",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def wrap_text(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = safe_text(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_paragraph(canvas_obj: canvas.Canvas, text: str, x: float, y: float, width: float, size: float = 18, color=INK, leading: float | None = None) -> float:
    leading = leading or size * 1.25
    paragraph = Paragraph(inline_markup(text), ParagraphStyle("slide", fontName="Helvetica", fontSize=size, leading=leading, textColor=color))
    _, height = paragraph.wrap(width, 500)
    paragraph.drawOn(canvas_obj, x, y - height)
    return y - height


def draw_bullets(canvas_obj: canvas.Canvas, bullets: Iterable[str], x: float, y: float, width: float, size: float = 18) -> float:
    for bullet in bullets:
        y = draw_paragraph(canvas_obj, "- " + bullet, x, y, width, size=size, color=INK, leading=size * 1.3) - 10
    return y


def build_presentation_pdf(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    slide_width, slide_height = 13.333 * inch, 7.5 * inch
    deck = canvas.Canvas(str(target), pagesize=(slide_width, slide_height), pageCompression=1)
    deck.setTitle("Hong Kong Student Second-hand PIM - COMP3211 Presentation")
    slides = [
        {
            "title": "Hong Kong Student Second-hand PIM",
            "subtitle": "COMP3211 Software Engineering | Fall 2026",
            "bullets": ["Command-line PIM for managing campus second-hand trades", "Presenter names and student IDs: fill before recording"],
        },
        {
            "title": "Scope and user value",
            "bullets": ["A local single-user tool for listing notes, contacts, tasks, and handover events", "The approved workflow covers create, search, update, print, delete, save, and load", "Payment and physical handover remain outside the program"],
        },
        {
            "title": "Three requirements",
            "bullets": ["Creation: create text, task, event, and contact PIRs with validation", "Criterion: combine type, text, and time predicates with !, &&, ||, and parentheses", "Search: return stable, detailed records and treat non-applicable fields as non-matches"],
        },
        {
            "title": "Overall design: MVC",
            "diagram": True,
            "bullets": ["Model owns PIR data, validation, criteria, repository, and .pim persistence", "Controller coordinates parsed commands and model operations", "View renders prompts, records, results, and errors"],
        },
        {
            "title": "Example campus trade",
            "bullets": ["Create a listing: create text content=...", "Create buyer contact, payment task, and campus handover event", "Search: type = text && content contains \"ipad\"", "Update status to sold, print all records, save campus_market.pim"],
        },
        {
            "title": "Verification evidence",
            "bullets": ["31 automated tests pass with 0 failures and 0 errors", "93.6% executable source line coverage: 781 of 834 lines", "US1-US11 each map to executable tests in the requirements coverage report", "Python standard library only"],
        },
        {
            "title": "Lesson learned",
            "bullets": ["Requirements become testable when command grammar and acceptance criteria are explicit", "A small controller boundary makes the model testable without terminal I/O", "Atomic updates and validated persistence protect the user's trade records"],
        },
        {
            "title": "Thank you",
            "subtitle": "Questions",
            "bullets": ["Before recording: replace presenter placeholders, show each member's face and student ID at the beginning, and keep every presenter visible while speaking"],
        },
    ]
    for index, slide in enumerate(slides, start=1):
        deck.setFillColor(colors.HexColor("#F7FAFC"))
        deck.rect(0, 0, slide_width, slide_height, fill=1, stroke=0)
        deck.setFillColor(ACCENT)
        deck.rect(0, slide_height - 0.18 * inch, slide_width, 0.18 * inch, fill=1, stroke=0)
        deck.setFillColor(INK)
        deck.setFont("Helvetica-Bold", 27)
        deck.drawString(0.7 * inch, slide_height - 0.95 * inch, safe_text(slide["title"]))
        if slide.get("subtitle"):
            deck.setFont("Helvetica", 15)
            deck.setFillColor(MUTED)
            deck.drawString(0.72 * inch, slide_height - 1.35 * inch, safe_text(slide["subtitle"]))
        if slide.get("diagram"):
            box_y = slide_height - 3.05 * inch
            boxes = [
                (0.8 * inch, box_y, 2.9 * inch, "View", PALE),
                (5.2 * inch, box_y, 2.9 * inch, "Controller", colors.HexColor("#E6F0FA")),
                (9.6 * inch, box_y, 2.9 * inch, "Model", colors.HexColor("#EAF5ED")),
            ]
            for box_x, y_pos, width, label, fill in boxes:
                deck.setFillColor(fill)
                deck.setStrokeColor(ACCENT)
                deck.roundRect(box_x, y_pos, width, 0.86 * inch, 12, fill=1, stroke=1)
                deck.setFillColor(INK)
                deck.setFont("Helvetica-Bold", 20)
                deck.drawCentredString(box_x + width / 2, y_pos + 0.32 * inch, label)
            deck.setStrokeColor(MUTED)
            deck.setLineWidth(2)
            deck.line(3.7 * inch, box_y + 0.43 * inch, 5.15 * inch, box_y + 0.43 * inch)
            deck.line(8.1 * inch, box_y + 0.43 * inch, 9.55 * inch, box_y + 0.43 * inch)
            deck.setFont("Helvetica", 12)
            deck.setFillColor(MUTED)
            deck.drawCentredString(4.42 * inch, box_y + 0.62 * inch, "commands")
            deck.drawCentredString(8.83 * inch, box_y + 0.62 * inch, "PIR operations")
            draw_bullets(deck, slide["bullets"], 0.9 * inch, box_y - 0.38 * inch, slide_width - 1.8 * inch, size=16)
        else:
            start_y = slide_height - (2.0 * inch if slide.get("subtitle") else 1.7 * inch)
            draw_bullets(deck, slide["bullets"], 0.9 * inch, start_y, slide_width - 1.8 * inch, size=21)
        deck.setFillColor(MUTED)
        deck.setFont("Helvetica", 9)
        deck.drawRightString(slide_width - 0.65 * inch, 0.35 * inch, f"{index} / {len(slides)}")
        deck.drawString(0.65 * inch, 0.35 * inch, "Hong Kong Student Second-hand PIM")
        deck.showPage()
    deck.save()


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    documents = [
        (ROOT / "docs" / "requirements" / "SRS.md", OUTPUT / "SRS.pdf", "Software Requirements Specification"),
        (ROOT / "docs" / "design" / "design-document.md", OUTPUT / "design-document.pdf", "Design Document"),
        (ROOT / "docs" / "implementation" / "developer-manual.md", OUTPUT / "developer-manual.pdf", "Developer Manual"),
        (ROOT / "docs" / "implementation" / "user-manual.md", OUTPUT / "user-manual.pdf", "User Manual"),
        (ROOT / "docs" / "testing" / "requirements-coverage.md", OUTPUT / "requirements-coverage.pdf", "Requirements Coverage Report"),
    ]
    for source, target, title in documents:
        build_document_pdf(source, target, title)
    coverage_source = ROOT / "reports" / "generated" / "coverage.txt"
    coverage_markdown = OUTPUT / "_coverage-source.md"
    coverage_markdown.write_text("# Line Coverage Report\n\n```text\n" + coverage_source.read_text(encoding="utf-8") + "```\n", encoding="utf-8")
    build_document_pdf(coverage_markdown, OUTPUT / "line-coverage-report.pdf", "Line Coverage Report")
    coverage_markdown.unlink(missing_ok=True)
    build_presentation_pdf(OUTPUT / "presentation-slides.pdf")
    print(f"Generated {len(list(OUTPUT.glob('*.pdf')))} PDFs in {OUTPUT}")


if __name__ == "__main__":
    main()





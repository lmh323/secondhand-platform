"""Validate and build the final COMP3211 submission ZIP."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "deliverables" / "secondhand-platform-submission.zip"
REQUIRED = (
    ROOT / "Project Honour Declaration - 2026.docx",
    ROOT / "output" / "pdf" / "SRS.pdf",
    ROOT / "output" / "pdf" / "design-document.pdf",
    ROOT / "output" / "pdf" / "developer-manual.pdf",
    ROOT / "output" / "pdf" / "user-manual.pdf",
    ROOT / "output" / "pdf" / "requirements-coverage.pdf",
    ROOT / "output" / "pdf" / "line-coverage-report.pdf",
    ROOT / "output" / "pdf" / "presentation-slides.pdf",
    ROOT / "requirements-coverage.md",
    ROOT / "line-coverage-report.txt",
    ROOT / "recordings" / "system-demo.mp4",
    ROOT / "recordings" / "presentation.mp4",
)


def check_required() -> list[Path]:
    missing: list[Path] = []
    for path in REQUIRED:
        if not path.is_file() or path.stat().st_size == 0:
            missing.append(path)
    return missing


def add_file(archive: zipfile.ZipFile, source: Path, archive_name: str) -> None:
    archive.write(source, archive_name)


def build() -> None:
    missing = check_required()
    if missing:
        print("Submission ZIP is not ready. Missing files:")
        for path in missing:
            print(f"- {path.relative_to(ROOT)}")
        raise SystemExit(2)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        root_files = (
            "README.md",
            ".gitignore",
            "Project Honour Declaration - 2026.docx",
            "requirements-coverage.md",
            "requirements-coverage.pdf",
            "line-coverage-report.txt",
            "line-coverage-report.pdf",
        )
        for relative in root_files:
            add_file(archive, ROOT / relative, relative)

        for directory in ("src", "tests", "tools", "docs", "reports/generated", "recordings"):
            base = ROOT / directory
            for source in sorted(base.rglob("*")):
                if not source.is_file():
                    continue
                if "__pycache__" in source.parts or source.suffix in {".pyc", ".pyo", ".pim"}:
                    continue
                add_file(archive, source, str(source.relative_to(ROOT)).replace("\\", "/"))

        pdf_root_mapping = {
            "SRS.pdf": ROOT / "output" / "pdf" / "SRS.pdf",
            "design-document.pdf": ROOT / "output" / "pdf" / "design-document.pdf",
            "developer-manual.pdf": ROOT / "output" / "pdf" / "developer-manual.pdf",
            "user-manual.pdf": ROOT / "output" / "pdf" / "user-manual.pdf",
            "presentation-slides.pdf": ROOT / "output" / "pdf" / "presentation-slides.pdf",
        }
        for archive_name, source in pdf_root_mapping.items():
            add_file(archive, source, archive_name)

    print(f"Created {OUTPUT}")
    print(f"Archive entries: {len(zipfile.ZipFile(OUTPUT).namelist())}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true", help="validate required files without creating a ZIP")
    args = parser.parse_args()
    missing = check_required()
    if args.check_only:
        if missing:
            print("Submission ZIP is not ready. Missing files:")
            for path in missing:
                print(f"- {path.relative_to(ROOT)}")
            return 2
        print("All required submission files are present.")
        return 0
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Final ZIP Checklist

The final archive must contain the complete source code and all required deliverables. Build it only after the group fills the official Honour Declaration and records both MP4 files.

## Required files

- [ ] `Project Honour Declaration - 2026.docx` at the ZIP root, completed and signed as required.
- [ ] SRS PDF: `output/pdf/SRS.pdf`.
- [ ] Design PDF: `output/pdf/design-document.pdf`.
- [ ] Complete source code under `src/`.
- [ ] Developer manual PDF: `output/pdf/developer-manual.pdf`.
- [ ] User manual PDF: `output/pdf/user-manual.pdf`.
- [ ] Implementation demo video: `recordings/system-demo.mp4`, no more than four minutes.
- [ ] Requirements coverage report at the source root: `requirements-coverage.md` and its PDF copy in `output/pdf/requirements-coverage.pdf`.
- [ ] Automatically executable model tests under `tests/`.
- [ ] Line coverage report at the source root: `line-coverage-report.txt` and its PDF copy in `output/pdf/line-coverage-report.pdf`.
- [ ] Presentation slides PDF: `output/pdf/presentation-slides.pdf`.
- [ ] Presentation recording: `recordings/presentation.mp4`, no more than five minutes.

## Final verification

- [ ] Run `python -m unittest discover -s tests -t . -v` and confirm all tests pass.
- [ ] Run `python tools/coverage_report.py` and regenerate the root line coverage copy.
- [ ] Run `python -m compileall -q src tests tools`.
- [ ] Open every PDF and check that text, tables, diagrams, page numbers, and slide numbers are readable.
- [ ] Check that the demo and presentation videos play and meet their time limits.
- [ ] Check that no temporary files, `__pycache__` directories, generated screenshots, or unrelated source files enter the ZIP.
- [ ] Open the ZIP once after building it and verify the required files are at the expected paths.

The reproducible ZIP builder is `tools/build_submission_zip.py`. It refuses to build while the two MP4 files are missing, which prevents an incomplete archive from being mistaken for the final submission.

# Stage 6 Submission Package Delivery

Status: Submission package prepared; final ZIP awaits group-specific recordings and declaration completion.

## Prepared scope

- Generated PDF versions of the SRS, design document, developer manual, user manual, requirements coverage report, line coverage report, and presentation slides.
- Added root-level `requirements-coverage.md`, `requirements-coverage.pdf`, `line-coverage-report.txt`, and `line-coverage-report.pdf` to satisfy the course report placement requirements.
- Added a short implementation demo script capped at four minutes.
- Added a presentation script capped at five minutes with three-person and four-person role allocations.
- Added the official 2026 Honour Declaration template and a completion guide.
- Added a reproducible ZIP builder that validates required files before creating the archive.
- Added a final checklist and submission manifest.
- Rendered and visually checked the generated PDFs with Poppler. The design PDF contains rendered architecture, component relationship, and search sequence diagrams.

## Generated PDF artifacts

Canonical generated files are in `output/pdf/`:

- `SRS.pdf`
- `design-document.pdf`
- `developer-manual.pdf`
- `user-manual.pdf`
- `requirements-coverage.pdf`
- `line-coverage-report.pdf`
- `presentation-slides.pdf`

## Validation evidence

- `python -m py_compile tools/build_submission_pdfs.py tools/build_submission_zip.py` passed.
- `python tools/build_submission_pdfs.py` generated seven PDFs.
- Poppler rendering completed for the generated PDFs; the presentation deck has eight readable slides.
- Stage 5 verification remains reproducible: 31 tests pass with 0 failures and 0 errors, and line coverage is 781/834 (93.6%).
- `python tools/build_submission_zip.py --check-only` intentionally reports the two missing MP4 recordings until the group records them.

## Group actions still required

1. Replace presenter placeholders with real names and IDs in the presentation materials.
2. Record `recordings/system-demo.mp4` within four minutes.
3. Record `recordings/presentation.mp4` within five minutes, showing every member's face and student ID at the beginning and keeping the current presenter visible while speaking.
4. Complete, sign, and truthfully fill `Project Honour Declaration - 2026.docx`, including contribution percentages summing to 100% and the GenAI declaration.
5. Run the ZIP builder and inspect the resulting archive.

The repository has no access to the group's faces, student cards, names, signatures, or contribution agreement, so those artifacts must be supplied by the group before submission.

## Stage gate

Stage 6 preparation is ready for acceptance when the product owner agrees that the generated documents, scripts, checklists, and ZIP validation workflow are complete. The final archive becomes buildable after the four group actions above are completed.

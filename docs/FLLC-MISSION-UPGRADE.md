# FLLC Mission Upgrade — CISSQLexe

## Role in the PersonFu/FLLC portfolio

CISSQLexe should be treated as one of the cleanest public learning products in the PersonFu portfolio: a standalone SQL education app that can become a polished free showcase, paid microcourse, and employer-facing proof of instructional software development.

## Upgrade direction

### 1. Product positioning

Position as:

> A portable Windows SQL learning lab with modules, quizzes, progress tracking, achievements, transcripts, and a local SQLite playground.

This is stronger than framing it as just a class artifact. It is a working education product.

### 2. Visual and interaction improvements

- Add a landing/dashboard redesign with FLLC dark mission theme.
- Add animated course path map.
- Add progress rings and module completion timeline.
- Add SQL query result table polish.
- Add achievement unlock animations.
- Add exportable transcript preview panel.
- Add beginner/intermediate/advanced module filters.

### 3. Engineering upgrades

- Add automated smoke tests for module manifest loading.
- Validate every `Lab.sql` file loads into SQLite.
- Add a GitHub Action that builds the executable on release tags.
- Add SHA256 checksum for the downloadable EXE.
- Add release notes per version.
- Add signed-build research note for future trust improvements.

### 4. Paid-content path

| Tier | Product |
| --- | --- |
| Public | Free SQL Essentials app and sample modules |
| Basic | Full module walkthroughs, quizzes, and transcripts |
| Premium | Instructor pack, capstone grading rubric, custom database labs |

### 5. FLLC website integration

Add a product card for:

- SQL Essentials for the Real World.
- Download button.
- Screenshot gallery.
- Curriculum outline.
- Transcript/export feature preview.
- Paid upgrade path.

## Content outputs

- Blog: “Turning a SQL class into a portable learning product.”
- Short video: “A SQL course should have progress, labs, and transcripts.”
- Product page: “CISSQL.exe — SQL Essentials for the Real World.”
- Member lesson: “Building educational desktop apps with Python, Tkinter, and SQLite.”

## Immediate quality checklist

- [ ] Add screenshots or GIFs.
- [ ] Add release checksum.
- [ ] Add smoke-test script.
- [ ] Add changelog.
- [ ] Add FLLC product page link once live.

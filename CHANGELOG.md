# Changelog

All notable changes to this repository are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.2.0] - 2026-11-15

### Docs
- Docs: training-grade README and walkthrough. Added "What problem this solves", "What you will learn",
  "How it works" with the notebooks in reading order, "Key concepts", an accurate repo layout and
  `docs/methodology.md`.

### Fixed
- Notebooks wrote outputs to `notebooks/data/outputs/` when Jupyter ran from `notebooks/`. `DATA_DIR` now defaults to `data/` at the repo root.
- Notebooks 02 and 03 now stop with a clear message if the previous step's CSV is missing.
- `tests/test_notebooks.py` now also checks that maintained notebooks are committed without outputs.
- `pytest` added to `requirements.txt` so a fresh install can run the tests.

## [1.1.0] - 2026-11-15

### Added
- `original/`: the original research code (read-only).
- `CHANGELOG.md`, `CONTRIBUTING.md` and a documentation index in `docs/README.md`.
- A notebook check (`tests/test_notebooks.py`) and CI.

## [1.0.0] - 2026-11-04

### Added
- First public release: the maintained code, documentation, tests and CI.

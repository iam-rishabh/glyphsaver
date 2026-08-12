# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
once a first tagged release is made.

## [Unreleased]

### Changed
- **Breaking:** rebuilt as a pure glyph (vector-only) screensaver
  framework — removed the image slideshow entirely, along with the
  Pillow dependency and `~/Pictures/screensaver` folder. glyphsaver is
  now developer-facing: screensavers are code, not image files.
- Renamed the project to **glyphsaver**.
- Introduced a plugin architecture: any `glyphs.base.Glyph` subclass
  dropped into `glyphs/` is auto-discovered — no registry edits needed.
- `glyphsaver.py` is now a small CLI (`list`, `run <glyph> [flags]`)
  instead of one hardcoded script per screensaver.
- `idle_watcher.py` now launches any glyph via `--glyph NAME -- FLAGS`
  instead of a hardcoded `--mode`.
- 'glyphs/heart_eyes.py -- updated the heart eyes to new color and animations.

### Added
- `glyphs/base.py` — the `Glyph` plugin contract.
- `glyphs/heart_eyes.py` — built-in example glyph (blinking heart eyes),
  also the reference implementation for new contributors.
- `docs/CREATING_GLYPHS.md` — step-by-step guide for writing new glyphs.
- Project scaffolding for contributions: LICENSE, CONTRIBUTING,
  CODE_OF_CONDUCT, SECURITY, issue/PR templates, CI workflow, unit tests.
- `glyphs/robots_eyes.py` — robots eye - pixel style.

### Removed
- `slideshow_screensaver.py` and all image-folder / Pillow functionality.

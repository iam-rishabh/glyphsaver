## What does this change?

<!-- Describe the change and why it's needed. Link any related issue. -->

Closes #

## Type of change

- [ ] New glyph
- [ ] Bug fix
- [ ] Other feature (CLI, idle watcher, packaging, etc.)
- [ ] Documentation
- [ ] CI

## Checklist

- [ ] `pytest` passes locally
- [ ] `python3 -m py_compile glyphsaver.py idle_watcher.py glyphs/*.py` passes
- [ ] `flake8 . --max-line-length=110` passes
- [ ] I kept dependencies to stdlib + Tkinter only (no Pillow/GTK/Qt/etc.)
- [ ] Any animation uses `root.after(...)`, not a blocking loop
- [ ] I updated `docs/USAGE.md` if I added/changed CLI flags
- [ ] I updated `CHANGELOG.md` under `[Unreleased]`
- [ ] I added/updated tests for pure logic changes (geometry, discovery, etc.)

## Screenshot / recording

<!-- A GIF or screenshot is very helpful for anything that changes what's drawn on screen. -->

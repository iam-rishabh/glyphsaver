# Contributing

Thanks for considering a contribution — new glyphs, bug fixes, docs
improvements, and packaging work are all genuinely welcome.

## Ground rules

- Be kind. See the [Code of Conduct](CODE_OF_CONDUCT.md).
- Keep it lightweight. The whole point of glyphsaver is that it starts
  instantly and uses almost no RAM. **Stdlib + Tkinter only** — no
  Pillow, GTK, Qt, Pygame, or other heavy dependencies. If something
  seems to genuinely need one, open an issue to discuss it before
  writing code.
- Small, focused pull requests are much easier to review than large
  ones. If you're planning something big, open an issue first.

## Getting set up

```bash
git clone https://github.com/OWNER/glyphsaver.git
cd glyphsaver
sudo apt install python3-tk xprintidle
```

No `pip install` needed for the app itself — only for running tests/lint
(see below).

Run it directly while you work:

```bash
python3 glyphsaver.py list
python3 glyphsaver.py run heart-eyes --mouth
```

## Running tests and checks

```bash
pip install pytest flake8 --break-system-packages
pytest
python3 -m py_compile glyphsaver.py idle_watcher.py glyphs/*.py
flake8 . --max-line-length=110
shellcheck install.sh
```

CI runs the same checks on every pull request (see
`.github/workflows/ci.yml`). Please make sure they all pass locally
before opening a PR.

## Adding a new glyph

This is the contribution glyphsaver is built around. Full guide:
[docs/CREATING_GLYPHS.md](docs/CREATING_GLYPHS.md). Short version:

1. Add `glyphs/your_glyph.py` subclassing `glyphs.base.Glyph`.
2. Give it a unique `name` and a one-line `description`.
3. Declare flags in `add_arguments()`, draw and animate in `setup()`
   using `root.after()` — never a blocking loop.
4. It's auto-discovered — no registry to edit.
5. Pull any non-trivial math into a standalone, unit-testable function
   (see `heart_points()` in `glyphs/heart_eyes.py` for the pattern).
6. Update `docs/USAGE.md` and `CHANGELOG.md`.

## Coding style

- Python 3, stdlib + Tkinter only.
- Follow [PEP 8](https://peps.python.org/pep-0008/); 4-space indents.
- Keep pure logic (geometry, math, discovery) separable from anything
  that touches Tk/the display, so it's unit-testable headlessly.
- Docstrings/comments over cleverness — optimize for readability.

## Submitting a pull request

1. Fork the repo and create a branch off `main`.
2. Make your change, with tests where it makes sense.
3. Run the checks above.
4. Open a PR using the template — describe what changed and why, and
   link any related issue.
5. Be responsive to review feedback; small follow-up commits are fine.

## Good first issues

- Add a new glyph (stars, a full smiley face, a matrix-rain effect —
  anything Tkinter Canvas can draw).
- Add a screenshot/GIF of `heart-eyes` to the README.
- Improve idle detection for pure-Wayland sessions (no XWayland).
- Add a `.deb` packaging recipe or a Flatpak manifest.
- Add a config file (e.g. `~/.config/glyphsaver/config.toml`) as an
  alternative to CLI flags for the idle watcher's default glyph.

Check the [issue tracker](../../issues) for anything labeled
`good first issue` or `help wanted`.

## Reporting bugs / requesting features

Please use the issue templates — they ask for just enough detail (Ubuntu
version, session type X11/Wayland, steps to reproduce) to make bugs
actionable quickly.

## Security issues

Please don't open a public issue for a security concern — see
[SECURITY.md](SECURITY.md) instead.

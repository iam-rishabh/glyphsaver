# glyphsaver

[![CI](https://github.com/OWNER/glyphsaver/actions/workflows/ci.yml/badge.svg)](https://github.com/OWNER/glyphsaver/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Lightweight, code-only screensavers for Linux, built for developers who
want to write their own.

No images, no asset pipeline, no GTK/Qt/Electron — every screensaver
("glyph") is a small Python class that draws itself on a Tkinter canvas.
Drop a new file in `glyphs/` and it's picked up automatically by the CLI.
Starts instantly, idles at a few MB of RAM.

> Replace `OWNER` above with your GitHub username/org once this repo is pushed.

## Why glyph-only?

Most screensaver tools are either a slideshow of files you feed it, or a
sealed binary you can't touch. glyphsaver is neither: it's a small,
readable framework where the screensaver *is* the code. If you can write
a Tkinter Canvas animation, you can ship a new glyph in a few dozen lines
— see the built-in `heart-eyes` glyph as a working example, and
[docs/CREATING_GLYPHS.md](docs/CREATING_GLYPHS.md) for the full guide.

## Quick install

```bash
git clone https://github.com/OWNER/glyphsaver.git
cd glyphsaver
chmod +x install.sh
./install.sh
```

This installs `python3-tk` and `xprintidle` (the only two dependencies —
both lightweight, neither is Pillow/GTK/Qt), copies the scripts to
`~/.local/share/glyphsaver/`, and enables a systemd user service that
triggers a glyph screensaver after 5 minutes idle.

## Try it

```bash
python3 glyphsaver.py list
python3 glyphsaver.py run heart-eyes --mouth
```

Any keypress, click, or real mouse movement exits — like a normal
screensaver.

## Project layout

```
.
├── glyphsaver.py           # CLI: discovers glyphs, runs one fullscreen
├── glyphs/
│   ├── base.py              # Glyph base class — the plugin contract
│   └── heart_eyes.py        # built-in example glyph (blinking heart eyes)
├── idle_watcher.py          # idle-time daemon that launches a glyph
├── install.sh               # one-shot installer
├── systemd/                 # systemd --user service unit
├── tests/                   # pytest unit tests for the pure logic
└── docs/
    ├── USAGE.md              # full CLI reference
    └── CREATING_GLYPHS.md    # how to write your own glyph
```

## Contributing

New glyphs are the easiest and most welcome kind of contribution — see
[docs/CREATING_GLYPHS.md](docs/CREATING_GLYPHS.md) to write one, and
[CONTRIBUTING.md](CONTRIBUTING.md) for the general process and the design
constraints (stdlib + Tkinter only, non-blocking animation, no network/file
I/O). Please also follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

[MIT](LICENSE) — see the LICENSE file for details.

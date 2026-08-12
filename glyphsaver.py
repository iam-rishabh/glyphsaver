#!/usr/bin/env python3
"""
glyphsaver.py

Lightweight, developer-friendly glyph screensaver runner for Linux.
Pure Tkinter — no images, no GTK/Qt, no third-party runtime
dependencies. Every screensaver is a small "glyph" plugin (see
glyphs/base.py); this script discovers them, builds a `--help`-able
CLI for each, and runs the chosen one fullscreen.

USAGE
-----
    glyphsaver.py list
    glyphsaver.py run heart-eyes --mouth --size 180

EXITING
-------
Any keypress, mouse click, or noticeable mouse movement closes the
screensaver immediately, same as a normal screensaver.

ADDING YOUR OWN GLYPH
----------------------
Drop a new file in glyphs/ that subclasses `glyphs.base.Glyph` — it's
picked up automatically, no changes needed here. See
docs/CREATING_GLYPHS.md.
"""

import argparse
import sys

try:
    import tkinter as tk
except ImportError:
    sys.exit("Tkinter is missing. Install it with: sudo apt install python3-tk")

from glyphs import discover_glyphs

MOUSE_WAKE_THRESHOLD = 15  # pixels of mouse movement before we treat it as "user is back"


class Runner:
    """Owns the fullscreen window/canvas and the input-exits-screensaver
    behavior; delegates all drawing to the chosen Glyph instance."""

    def __init__(self, root, glyph, bg):
        self.root = root
        self._start_pos = None

        root.configure(background=bg)
        root.attributes("-fullscreen", True)
        root.config(cursor="none")

        self.canvas = tk.Canvas(root, bg=bg, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        root.bind("<Key>", self.exit_app)
        root.bind("<Button>", self.exit_app)
        root.bind("<Motion>", self.on_motion)

        root.update_idletasks()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()

        glyph.setup(root, self.canvas, width, height)

    def on_motion(self, event):
        if self._start_pos is None:
            self._start_pos = (event.x, event.y)
            return
        dx = event.x - self._start_pos[0]
        dy = event.y - self._start_pos[1]
        if (dx * dx + dy * dy) ** 0.5 > MOUSE_WAKE_THRESHOLD:
            self.exit_app()

    def exit_app(self, _event=None):
        self.root.destroy()


def build_parser(registry):
    parser = argparse.ArgumentParser(
        prog="glyphsaver",
        description="Lightweight, developer-friendly glyph screensavers for Linux",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List available glyphs")

    run_p = sub.add_parser("run", help="Run a glyph fullscreen")
    run_sub = run_p.add_subparsers(dest="glyph", required=True)
    for name, cls in sorted(registry.items()):
        gp = run_sub.add_parser(name, help=cls.description, description=cls.description)
        cls.add_arguments(gp)

    return parser


def main():
    registry = discover_glyphs()
    parser = build_parser(registry)
    args = parser.parse_args()

    if args.command == "list":
        if not registry:
            print("No glyphs found.")
            return
        width = max(len(n) for n in registry) + 2
        for name, cls in sorted(registry.items()):
            print(f"{name.ljust(width)} {cls.description}")
        return

    cls = registry[args.glyph]
    glyph = cls(args)

    root = tk.Tk()
    root.title(f"glyphsaver: {args.glyph}")
    Runner(root, glyph, args.bg)
    root.mainloop()


if __name__ == "__main__":
    main()

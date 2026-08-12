"""
glyphs.base
============

Every glyph screensaver is a small class that subclasses `Glyph`. Drop a
new file in the `glyphs/` package and it's auto-discovered — no registry
edits, no changes anywhere else.

Minimal example:

    # glyphs/pulse.py
    import tkinter as tk
    from .base import Glyph

    class PulseGlyph(Glyph):
        name = "pulse"
        description = "A circle that pulses in size"

        @classmethod
        def add_arguments(cls, parser):
            super().add_arguments(parser)
            parser.add_argument("--color", default="#00e5ff")
            parser.add_argument("--period-ms", type=int, default=1200)

        def setup(self, root, canvas, width, height):
            self.root, self.canvas = root, canvas
            self.cx, self.cy = width // 2, height // 2
            self.item = canvas.create_oval(0, 0, 0, 0, fill=self.args.color, outline="")
            self._animate(0)

        def _animate(self, step):
            import math
            r = 80 + 40 * math.sin(step / 20)
            self.canvas.coords(self.item, self.cx - r, self.cy - r, self.cx + r, self.cy + r)
            self.root.after(30, self._animate, step + 1)

See docs/CREATING_GLYPHS.md for the full guide.
"""


class Glyph:
    """Base class for a glyph screensaver plugin."""

    #: Short, unique, kebab-case identifier used on the command line,
    #: e.g. `glyphsaver run heart-eyes`.
    name = "base"

    #: One-line description shown in `glyphsaver list` and --help.
    description = "Base glyph (override me)"

    def __init__(self, args):
        """`args` is the parsed argparse.Namespace for this glyph's
        subcommand (whatever `add_arguments` declared, plus `--bg`)."""
        self.args = args

    @classmethod
    def add_arguments(cls, parser):
        """Register this glyph's CLI flags on `parser`. Subclasses that
        override this should call `super().add_arguments(parser)` first
        to keep the shared `--bg` flag."""
        parser.add_argument("--bg", default="black", help="Background color")

    def setup(self, root, canvas, width, height):
        """Called once, after the fullscreen window and canvas exist.
        Draw the initial frame here and schedule any animation via
        `root.after(delay_ms, callback, ...)`. Must not block — this is
        called from the Tk main loop.
        """
        raise NotImplementedError("Glyph subclasses must implement setup()")

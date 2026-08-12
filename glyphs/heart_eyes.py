"""
glyphs.heart_eyes
==================

Built-in example glyph: a pair of big heart-shaped eyes on a black
screen that blink on a randomized timer. Pure vector drawing on a
Tkinter Canvas — no image files or third-party libraries.

Also serves as the reference implementation to copy when writing a new
glyph — see `heart_points()` for the pure-geometry helper (unit tested
in tests/test_heart_points.py) and `HeartEyesGlyph` for the animation
pattern using `root.after()`.
"""

import math
import random

from .base import Glyph


def heart_points(cx, cy, size, squash=1.0, n=60):
    """Return a flat [x0, y0, x1, y1, ...] list approximating a heart
    shape, centered at (cx, cy). `squash` scales the vertical extent
    only (1.0 = fully open, ~0.05 = squeezed shut for a blink)."""
    pts = []
    for i in range(n):
        t = (i / (n - 1)) * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        x = x / 16.0 * size
        y = y / 17.0 * size * squash
        pts.append(cx + x)
        pts.append(cy + y)
    return pts


class HeartEyesGlyph(Glyph):
    name = "heart-eyes"
    description = "Big red heart-shaped eyes that blink on a random timer"

    @classmethod
    def add_arguments(cls, parser):
        super().add_arguments(parser)
        parser.add_argument("--eye-color", default="#ff2d55", help="Heart color")
        parser.add_argument("--size", type=int, default=140, help="Heart size in pixels")
        parser.add_argument("--gap", type=int, default=60, help="Gap between the two eyes")
        parser.add_argument("--blink-interval", type=float, default=3.5, help="Avg seconds between blinks")
        parser.add_argument("--blink-speed", type=int, default=220, help="Duration of one blink, ms")
        parser.add_argument("--mouth", action="store_true", help="Draw a simple smile below the eyes")

    def setup(self, root, canvas, width, height):
        self.root = root
        self.canvas = canvas
        self.cx, self.cy = width // 2, height // 2
        self.left_id = None
        self.right_id = None
        self.mouth_id = None

        self._draw(1.0)
        self._schedule_next_blink()

    # ---- layout helpers ----

    def _left_cx(self):
        return self.cx - self.args.gap / 2 - self.args.size / 2

    def _right_cx(self):
        return self.cx + self.args.gap / 2 + self.args.size / 2

    # ---- drawing ----

    def _draw(self, squash):
        if self.left_id is not None:
            self.canvas.delete(self.left_id)
        if self.right_id is not None:
            self.canvas.delete(self.right_id)

        size, color = self.args.size, self.args.eye_color
        left_pts = heart_points(self._left_cx(), self.cy, size, squash)
        right_pts = heart_points(self._right_cx(), self.cy, size, squash)
        self.left_id = self.canvas.create_polygon(left_pts, fill=color, outline="", smooth=True)
        self.right_id = self.canvas.create_polygon(right_pts, fill=color, outline="", smooth=True)

        if self.args.mouth and self.mouth_id is None:
            mx0 = self.cx - size * 1.1
            mx1 = self.cx + size * 1.1
            my = self.cy + size * 1.3
            self.mouth_id = self.canvas.create_arc(
                mx0, my - size * 0.6, mx1, my + size * 0.6,
                start=200, extent=140, style="arc",
                outline=color, width=max(4, size // 18),
            )

    # ---- animation ----

    def _blink(self, step=0):
        half = max(1, self.args.blink_speed // 2 // 20)  # ~20ms per frame
        total_steps = half * 2
        if step > total_steps:
            self._draw(1.0)
            self._schedule_next_blink()
            return
        if step <= half:
            squash = 1.0 - (step / half) * 0.92
        else:
            squash = 0.08 + ((step - half) / half) * 0.92
        self._draw(squash)
        self.root.after(20, self._blink, step + 1)

    def _schedule_next_blink(self):
        delay = int(random.uniform(self.args.blink_interval * 0.6, self.args.blink_interval * 1.6) * 1000)
        self.root.after(delay, self._blink)

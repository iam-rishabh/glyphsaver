# Creating a New Glyph

glyphsaver's whole design point is that adding a screensaver is just
"write a small Python class, drop it in `glyphs/`." No registry to edit,
no build step, no other file to touch.

## The contract

Every glyph is a subclass of `glyphs.base.Glyph`:

```python
class Glyph:
    name = "base"                 # kebab-case CLI identifier
    description = "..."           # one-liner shown in `glyphsaver list`

    @classmethod
    def add_arguments(cls, parser):
        """Register this glyph's CLI flags."""

    def setup(self, root, canvas, width, height):
        """Draw the first frame; schedule animation via root.after()."""
```

That's the entire interface. `discover_glyphs()` scans every module in
`glyphs/`, finds `Glyph` subclasses, and indexes them by `name`.

## Step by step

1. **Create the file.** `glyphs/<your_glyph>.py`.

2. **Subclass `Glyph`.**

   ```python
   from .base import Glyph

   class PulseGlyph(Glyph):
       name = "pulse"
       description = "A circle that pulses in size"
   ```

   `name` must be unique across all glyphs — `discover_glyphs()` raises
   a `ValueError` at startup if two glyphs collide, so you'll find out
   immediately, not at 2am when the screensaver silently picks the
   wrong one.

3. **Declare your flags.** Call `super().add_arguments(parser)` first to
   keep the shared `--bg` flag, then add your own:

   ```python
   @classmethod
   def add_arguments(cls, parser):
       super().add_arguments(parser)
       parser.add_argument("--color", default="#00e5ff")
       parser.add_argument("--period-ms", type=int, default=1200)
   ```

   These become real, `--help`-documented flags:
   `glyphsaver.py run pulse --color "#ff0000" --period-ms 800`.

4. **Implement `setup()`.** You get a live `tk.Canvas` already sized to
   the screen. Draw the first frame, then schedule your animation loop
   with `root.after(delay_ms, callback)` — never `time.sleep()` or a
   blocking loop, since that would freeze the whole Tk event loop
   (including the exit-on-input handling).

   ```python
   import math

   def setup(self, root, canvas, width, height):
       self.root, self.canvas = root, canvas
       self.cx, self.cy = width // 2, height // 2
       self.item = canvas.create_oval(0, 0, 0, 0, fill=self.args.color, outline="")
       self._animate(0)

   def _animate(self, step):
       r = 80 + 40 * math.sin(step / 20)
       self.canvas.coords(self.item, self.cx - r, self.cy - r, self.cx + r, self.cy + r)
       self.root.after(30, self._animate, step + 1)
   ```

5. **Try it:**

   ```bash
   python3 glyphsaver.py list                 # your glyph should appear
   python3 glyphsaver.py run pulse --help      # your flags should appear
   python3 glyphsaver.py run pulse
   ```

## Keep pure logic separate and testable

If your glyph involves any non-trivial math or geometry (shape
generation, easing curves, layout), pull it into a standalone function
at module level — not a method — so it can be unit tested without a
display. `glyphs/heart_eyes.py`'s `heart_points()` and
`tests/test_heart_points.py` are the reference example. CI runs headless
(via `xvfb`), so anything that requires an actual window can't be
exercised in a normal unit test — keep those parts as thin as possible.

## Design constraints (please read before submitting)

- **Stdlib + Tkinter only.** No GTK/Qt/Pillow/Pygame/etc. This is what
  keeps startup instant and memory tiny. If your idea genuinely needs
  something Tkinter's Canvas can't do, open an issue to discuss it
  before writing code.
- **Non-blocking.** All animation via `root.after()`. No `while True`
  loops, no `time.sleep()` in the Tk thread.
- **No network, no file writes.** A screensaver has no business phoning
  home or touching disk beyond its own source.
- **Respect the exit contract.** Don't rebind `<Key>`, `<Button>`, or
  `<Motion>` on the root window — `Runner` already owns those to make
  every glyph exit consistently on user input.

## Submitting

Add a short entry to `CHANGELOG.md` under `[Unreleased]`, add a test if
there's pure logic to test, update `docs/USAGE.md` with your flags, and
open a PR using the template. See [CONTRIBUTING.md](../CONTRIBUTING.md)
for the full checklist.

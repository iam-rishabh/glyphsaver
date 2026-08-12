# Usage Guide

## Install

```bash
chmod +x install.sh
./install.sh
```

This will:
1. Install `python3-tk` and `xprintidle` if missing (asks for your sudo
   password). No other dependencies — glyphs are pure vector code, not
   images, so there's nothing else to install.
2. Copy the app to `~/.local/share/glyphsaver/`.
3. Register and start a systemd user service that auto-launches a glyph
   after 5 minutes of inactivity (default: `heart-eyes --mouth`).

## Listing and running glyphs

```bash
python3 glyphsaver.py list
python3 glyphsaver.py run heart-eyes --mouth --size 180
python3 glyphsaver.py run heart-eyes --help   # every glyph has its own --help
```

Any keypress, click, or real mouse movement exits — like a normal
screensaver.

## Built-in glyph: heart-eyes

Big red heart-shaped eyes on a black screen, blinking on a randomized
timer.

| Flag | Default | Meaning |
|---|---|---|
| `--bg` | `black` | Background color |
| `--eye-color` | `#ff2d55` | Heart color |
| `--size` | `140` | Heart size in pixels |
| `--gap` | `60` | Gap between the two eyes |
| `--blink-interval` | `3.5` | Average seconds between blinks |
| `--blink-speed` | `220` | How long one blink takes, in ms |
| `--mouth` | off | Adds a simple curved smile below the eyes |

## Writing your own glyph

See [CREATING_GLYPHS.md](CREATING_GLYPHS.md) — the short version is:
drop a file in `glyphs/` that subclasses `glyphs.base.Glyph`, and it's
picked up automatically by `glyphsaver.py list` / `run`.

## Idle watcher

```bash
python3 idle_watcher.py --idle-seconds 300 --glyph heart-eyes -- --mouth
```

| Flag | Default | Meaning |
|---|---|---|
| `--idle-seconds` | `300` | Idle time before a glyph launches |
| `--poll-seconds` | `5` | How often idle time is checked |
| `--glyph` | `heart-eyes` | Which glyph to run (see `glyphsaver.py list`) |
| everything after `--` | | passed straight through to the glyph's own flags |

## Managing the background service

```bash
systemctl --user status glyphsaver.service   # check it's running
systemctl --user stop glyphsaver.service     # stop it
systemctl --user disable glyphsaver.service  # don't run on next login
journalctl --user -u glyphsaver.service       # view logs
```

To change the default glyph or its flags, edit `ExecStart` in
`~/.config/systemd/user/glyphsaver.service`, then:

```bash
systemctl --user daemon-reload
systemctl --user restart glyphsaver.service
```

## Uninstall

```bash
systemctl --user disable --now glyphsaver.service
rm -rf ~/.local/share/glyphsaver
rm ~/.config/systemd/user/glyphsaver.service
```

## Notes

- glyphsaver doesn't lock your screen — it's purely visual. Keep your
  desktop's built-in screen lock enabled alongside it if you also want
  locking; they run independently.
- Works on X11 out of the box. On Wayland sessions, `xprintidle` requires
  XWayland (present by default on Ubuntu's GNOME/Wayland sessions) — if
  idle detection doesn't work, run a glyph manually or bind it to a
  keyboard shortcut instead (Settings → Keyboard → Custom Shortcuts).

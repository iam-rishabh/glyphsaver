#!/usr/bin/env python3
"""
idle_watcher.py

Watches system idle time (via `xprintidle`) and launches a glyph
screensaver via glyphsaver.py once the user has been away longer than
--idle-seconds. Never launches a second copy while one is already
running.

Requires: xprintidle
    sudo apt install xprintidle

USAGE
-----
    idle_watcher.py --idle-seconds 300 --glyph heart-eyes -- --mouth

Everything after `--` is passed straight through to the glyph's own
flags (e.g. `--mouth`, `--eye-color`). Run this in the background
(systemd user service recommended — see docs/USAGE.md) and it behaves
like a normal screensaver daemon.
"""

import argparse
import shutil
import subprocess
import sys
import time


def get_idle_ms():
    try:
        out = subprocess.run(["xprintidle"], capture_output=True, text=True, check=True)
        return int(out.stdout.strip())
    except Exception:
        return 0


def main():
    parser = argparse.ArgumentParser(description="Idle-triggered launcher for glyphsaver.py")
    parser.add_argument("--idle-seconds", type=int, default=300, help="Idle seconds before launching")
    parser.add_argument("--poll-seconds", type=int, default=5, help="How often to check idle time")
    parser.add_argument("--glyph", default="heart-eyes", help="Which glyph to run (see: glyphsaver.py list)")
    parser.add_argument(
        "glyph_args", nargs=argparse.REMAINDER,
        help="Flags passed through to the glyph, after `--`, e.g. -- --mouth --size 180",
    )
    args = parser.parse_args()

    if shutil.which("xprintidle") is None:
        sys.exit("xprintidle not found. Install it with: sudo apt install xprintidle")

    # argparse.REMAINDER keeps a leading "--" if the user typed one; strip it.
    glyph_args = [a for a in args.glyph_args if a != "--"]

    runner_path = __file__.replace("idle_watcher.py", "glyphsaver.py")

    proc = None
    while True:
        idle_ms = get_idle_ms()
        if idle_ms >= args.idle_seconds * 1000:
            if proc is None or proc.poll() is not None:
                cmd = [sys.executable, runner_path, "run", args.glyph] + glyph_args
                proc = subprocess.Popen(cmd)
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()

# Security Policy

## Supported Versions

This is a small hobby-scale project distributed only from source (no
published releases yet). The `main` branch is the only supported version.

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security concerns.

Instead, use GitHub's private vulnerability reporting for this repository
(**Security tab → Report a vulnerability**), or contact a maintainer
directly. Please include:

- A description of the issue and its potential impact
- Steps to reproduce
- Any relevant logs or environment details (Ubuntu version, X11/Wayland)

We'll acknowledge reports as quickly as we can and work with you on a fix
before any public disclosure.

## Scope notes

glyphsaver runs entirely locally, draws only vector shapes via Tkinter's
Canvas, and has no network activity, no image/file parsing, and no file
writes beyond its own installed source. The main relevant attack surface
is glyph plugin code itself — since a glyph is arbitrary Python, only
install glyphs from sources you trust, the same way you would for any
other script.

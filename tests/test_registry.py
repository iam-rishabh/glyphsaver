"""Tests for glyphs.discover_glyphs() — the plugin auto-discovery
mechanism new contributors rely on when adding a glyph."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from glyphs import Glyph, discover_glyphs  # noqa: E402


def test_discovers_builtin_heart_eyes():
    registry = discover_glyphs()
    assert "heart-eyes" in registry


def test_all_registered_glyphs_are_glyph_subclasses():
    registry = discover_glyphs()
    for name, cls in registry.items():
        assert issubclass(cls, Glyph)
        assert cls.name == name


def test_base_class_itself_is_not_registered():
    registry = discover_glyphs()
    assert "base" not in registry
    assert Glyph not in registry.values()


def test_glyph_base_setup_is_not_implemented():
    import argparse

    instance = Glyph(argparse.Namespace())
    try:
        instance.setup(None, None, 0, 0)
        assert False, "expected NotImplementedError"
    except NotImplementedError:
        pass


def test_heart_eyes_add_arguments_includes_shared_bg_flag():
    import argparse

    from glyphs.heart_eyes import HeartEyesGlyph

    parser = argparse.ArgumentParser()
    HeartEyesGlyph.add_arguments(parser)
    args = parser.parse_args([])

    assert args.bg == "black"
    assert args.eye_color == "#ffffff"
    assert args.mouth is False

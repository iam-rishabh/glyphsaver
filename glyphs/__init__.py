"""
glyphs
======

Auto-discovering registry for glyph plugins. Any module placed in this
package that defines a subclass of `Glyph` (other than `Glyph` itself)
is picked up automatically by `discover_glyphs()` — no manual
registration required. See docs/CREATING_GLYPHS.md.
"""

import importlib
import pkgutil

from .base import Glyph

__all__ = ["Glyph", "discover_glyphs"]


def discover_glyphs():
    """Import every module in this package and return a dict mapping
    `Glyph.name` -> `Glyph` subclass for every glyph found.

    Raises ValueError if two glyphs register the same `name`, so
    conflicts are caught immediately rather than silently shadowing
    one another.
    """
    registry = {}
    package = importlib.import_module(__name__)

    for _finder, module_name, _is_pkg in pkgutil.iter_modules(package.__path__):
        if module_name in ("base",):
            continue
        module = importlib.import_module(f"{__name__}.{module_name}")
        for attr in vars(module).values():
            if (
                isinstance(attr, type)
                and issubclass(attr, Glyph)
                and attr is not Glyph
                and attr.name != "base"
            ):
                if attr.name in registry and registry[attr.name] is not attr:
                    raise ValueError(
                        f"Duplicate glyph name '{attr.name}' from "
                        f"{registry[attr.name]!r} and {attr!r}"
                    )
                registry[attr.name] = attr

    return registry

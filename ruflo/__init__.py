"""Ruflo — Unified AI Agent Monolith.

Consolidated OpenSpace modules for task execution, skill evolution, and agent coordination.
"""

__version__ = "2.0.0"


def __getattr__(name):
    """Lazy-load OpenSpace classes to prevent circular imports."""
    if name == "OpenSpace":
        from ruflo.core.engine import OpenSpace
        return OpenSpace
    elif name == "OpenSpaceConfig":
        from ruflo.core.engine import OpenSpaceConfig
        return OpenSpaceConfig
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "OpenSpace",
    "OpenSpaceConfig",
]

"""Re-export Severity so modules can import from a single stable location.

This thin shim avoids circular imports between severity_classifier and other
modules that only need the Severity enum itself.
"""
from depwatch.severity_classifier import Severity  # noqa: F401

__all__ = ["Severity"]

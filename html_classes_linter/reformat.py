"""
Reformat
========

Implement rewriting source content with rules applications.

"""
from .fixer import SourceFixer


class SourceWriter(SourceFixer):
    """
    TODO: Should also inherit from discovery and implement everything to reformat files
    in place.
    """

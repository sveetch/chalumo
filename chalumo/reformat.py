"""
Reformat
========

Implement rewriting source content with rules applications.

"""
from .discovery import SourceDiscovery
from .fixer import SourceFixer


class SourceWriter(SourceFixer, SourceDiscovery):
    """
    Rewrite sources with applyed rules fixes.
    """

    def run(self, basepath):
        """
        Produce a diff of cleaning operation for all allowed files in given basepath.

        Diff output mentions file paths as relative to the basepath.

        Arguments:
            basepath (pathlib.Path): Base path where to search for sources.
        """
        for filepath, from_source, to_source in self.apply_fixes(basepath):
            self.log.debug("🚀 Write reformating: {}".format(filepath))
            filepath.write_text(to_source)

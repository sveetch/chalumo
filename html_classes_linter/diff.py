"""
Changes diff
============

This is to make a diff output of change proposal for parsed contents against the lint
rules.

"""
import difflib

from .discovery import HtmlFileDiscovery
from .reformat import HtmlAttributeFix


class HtmlAttributeDiff(HtmlAttributeFix, HtmlFileDiscovery):
    """
    Create a diff output with unified context for content changes for each file.
    """
    DIFF_CONTEXT_LINES = 4

    def diff_source(self, path, from_source, to_source):
        """
        Produce an unified diff of source changes.
        """
        fromlines = from_source.splitlines(keepends=True)
        tolines = to_source.splitlines(keepends=True)

        return list(
            difflib.unified_diff(
                fromlines,
                tolines,
                str(path),
                str(path),
                n=self.DIFF_CONTEXT_LINES,
            )
        )

    def clean(self, basepath):
        """
        Run cleaning on allowed source files from basepath and return original and
        modified contents.
        """
        return self.batch_sources(
            self.get_source_contents(
                self.get_source_files(basepath)
            )
        )

    def run(self, basepath):
        """
        Produce a diff of cleaning operation for all allowed files from given basepath.

        Diff output mentions file paths as relative to the basepath.
        """
        for path, from_source, to_source in self.clean(basepath):
            rel_path = path.relative_to(basepath)
            diff_lines = self.diff_source(rel_path, from_source, to_source)

            if len(diff_lines) > 0:
                print("".join(diff_lines))
                print()

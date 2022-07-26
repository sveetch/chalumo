"""
Changes diff
============

This is to make a diff output of change proposal for parsed contents against the lint
rules.

"""
import difflib
from pathlib import Path

from .discovery import HtmlFileDiscovery
from .reformat import HtmlAttributeFix


class HtmlAttributeDiff(HtmlAttributeFix, HtmlFileDiscovery):
    """
    Create a diff output with unified context for content changes for each file.

    Keywords Arguments:
        diff_context (integer): The number of context lines to output. Default to 4.
        output_callable (callable): Function to use to output diff lines. Default to
            ``print`` function.
    """
    DIFF_CONTEXT_LINES = 4

    def __init__(self, *args, **kwargs):
        self.diff_context = self.DIFF_CONTEXT_LINES
        if "diff_context" in kwargs:
            self.diff_context = kwargs.pop("diff_context")

        self.echo = print
        if "output_callable" in kwargs:
            self.echo = kwargs.pop("output_callable")

        super().__init__(*args, **kwargs)

    def diff_source(self, filepath, from_source, to_source):
        """
        Produce an unified diff of source changes.

        Arguments:
            filepath (pathlib.Path): Source file path.
            from_source (string): Original source content.
            to_source (string): Modified source content with applied fixes.

        Returns:
            generator: A generator to produce a list of diff output lines.
        """
        return difflib.unified_diff(
            from_source.splitlines(keepends=True),
            to_source.splitlines(keepends=True),
            str(filepath),
            str(filepath),
            n=self.DIFF_CONTEXT_LINES,
        )

    def apply_fixes(self, basepath):
        """
        Run cleaning on allowed source files from basepath and return original and
        modified contents.

        Arguments:
            basepath (pathlib.Path): Base path where to search for sources.

        Returns:
            list: List of tuple (for path, original and modified content) as returned
                from ``HtmlAttributeParser.process_source``
        """
        return self.parse_sources(
            self.get_source_contents(
                self.get_source_files(basepath)
            )
        )

    def run(self, basepath):
        """
        Produce a diff of cleaning operation for all allowed files in given basepath.

        Diff output mentions file paths as relative to the basepath.

        Arguments:
            basepath (pathlib.Path): Base path where to search for sources.
        """
        cwd = Path.cwd()

        for filepath, from_source, to_source in self.apply_fixes(basepath):
            diff_lines = list(
                self.diff_source(filepath, from_source, to_source)
            )

            if len(diff_lines) > 0:
                self.echo("".join(diff_lines))
                self.echo()

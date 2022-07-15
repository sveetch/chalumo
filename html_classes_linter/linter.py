"""
HTML Attribute cleaner
======================

The cleaner class is on charge to find, open and lint files.

"""
import difflib
import os
import re

from sys import getsizeof
from pathlib import Path


class HtmlAttributeCleaner:
    """
    Search HTML attributes in files to clean their values.
    """
    # TODO: Build and compile regex from __init__ so we can target any other attribute
    # than only 'class'
    CLASS_REGEX = re.compile(r"class=\"(?:[^\"]*)(?![^\" ])[^\"]*\"")
    DIFF_CONTEXT_LINES = 4

    def __init__(self, lint_tag="{# djlint:on #}", file_search_pattern=None):
        # NOTE: Should be possible to disable watching for a tag and just collect every
        # found files
        self.lint_tag = lint_tag

        # NOTE: Nice but we should also have rules to ignore some files
        self.file_search_pattern = file_search_pattern or "**/*.html"

        # NOTE: We could set many patterns, each one processed with glob, agregate all
        # matching entry into a set() and use it by comparaison on found files from
        # file_search_pattern to remove file to ignore
        self.ignore_search_patterns = []

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

    def get_source_files(self, basepath):
        """
        Get source file paths into given base path.
        """
        return basepath.glob(self.file_search_pattern)

    def get_source_contents(self, sources):
        """
        Get content from allowed files (match the possible lint tag if any or all).
        """
        elligible_files = {}

        for source in sources:
            with source.open() as f:
                # If lint tag is enabled, sniff file start for tag. The tag must be
                # exactly at the very start, nothing before
                intro = None
                if self.lint_tag:
                    intro = os.pread(f.fileno(), len(self.lint_tag), 0)

                # Only collect source with the starting lint tag if any is defined,
                # else every source are collected
                if not intro or intro.decode("utf-8") == self.lint_tag:
                    elligible_files[source] = f.read()

        return elligible_files

    def cssclass_parser(self, matchobj):
        """
        Return replaced class attribute

        Replacement function for ``re.sub()``
        """
        start = 'class="'
        end = '"'

        # Failsafe for unexpected cases
        if(
            not matchobj.group(0) or
            not matchobj.group(0).startswith(start) or
            not matchobj.group(0).endswith(end)
        ):
            return matchobj.group(0)

        # Split classes in pieces which reduce whitespace dividers to exactly one
        classes = matchobj.group(0)[len(start):-len(end)].split()
        #print("- Found:", classes)

        # Remove duplicate classes and enforce natural order (since 'set' return items
        # in an arbitrary order)
        # TODO: This is wrong, order should not be altered, we need to rewrite
        # uniqueness without 'set' behavior
        classes = sorted(set(classes))

        # Finally join them
        classes = " ".join(classes)

        return start + classes + end

    def process_source(self, filepath, content):
        """
        Batch cleaning process on all given source contents.
        """
        print()
        print("🚀 Processing:", filepath)

        return (
            filepath,
            content,
            self.CLASS_REGEX.sub(self.cssclass_parser, content, 0)
        )

    def batch_sources(self, sources):
        """
        Batch cleaning process on all given source contents.
        """
        return [self.process_source(k, v) for k, v in sources.items()]

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

    def diff(self, basepath):
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

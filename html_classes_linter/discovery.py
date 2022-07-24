"""
HTML discovery
==============

The discovery will search for elligible HTML files.

"""
import os

from pathlib import Path

from .logger import BaseLogger


class HtmlFileDiscovery(BaseLogger):
    """
    Search for elligible files which match given rules.
    """
    #DEFAULT_PRAGMA_TAG = "{# djlint:on #}"
    DEFAULT_PRAGMA_TAG = None
    DEFAULT_FILE_SEARCH_PATTERN = "**/*.html"

    def __init__(self, *args, **kwargs):
        self.pragma_tag = self.DEFAULT_PRAGMA_TAG
        if "pragma_tag" in kwargs:
            self.pragma_tag = kwargs.pop("pragma_tag")

        self.file_search_pattern = (
            kwargs.pop("file_search_pattern", None) or self.DEFAULT_FILE_SEARCH_PATTERN
        )

        # TODO: We could set many patterns, each one processed with glob, agregate all
        # matching entry into a set() and use it by comparaison on found files from
        # file_search_pattern to remove file to ignore
        self.ignore_search_patterns = []

        super().__init__(*args, **kwargs)

    def get_source_files(self, basepath):
        """
        Get source file paths into given base path.
        """
        return basepath.glob(self.file_search_pattern)

    def get_source_contents(self, sources):
        """
        Get content from allowed files.

        Allowed files must match the possible lint tag if defined else all files are
        allowed.
        """
        elligible_files = {}

        for source in sources:
            with source.open() as f:
                # If lint tag is enabled we sniff the file start for expected tag. The
                # tag must be exactly at the very start of content, nothing before.
                intro = None
                if self.pragma_tag:
                    intro = os.pread(f.fileno(), len(self.pragma_tag), 0)

                # Only collect source with the starting lint tag if any is defined,
                # else every source are collected
                if not intro or intro.decode("utf-8") == self.pragma_tag:
                    elligible_files[source] = f.read()

        return elligible_files

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
    Implement the way to discover source files.
    """
    DEFAULT_PRAGMA_TAG = None
    DEFAULT_FILE_SEARCH_PATTERN = "**/*.html"

    def __init__(self, *args, **kwargs):
        self.pragma_tag = self.DEFAULT_PRAGMA_TAG
        if "pragma_tag" in kwargs:
            self.pragma_tag = kwargs.pop("pragma_tag")

        self.file_search_pattern = (
            kwargs.pop("file_search_pattern", None) or self.DEFAULT_FILE_SEARCH_PATTERN
        )

        super().__init__(*args, **kwargs)

    def get_source_files(self, basepath):
        """
        Get source file paths into given base path.

        Arguments:
            basepath (pathlib.Path): A Path object to get files. If it's a directory,
                the glob pattern will be used to discover files. If it's a file, the
                glob pattern is not used.

        Returns:
            list: List of found files.
        """
        if basepath.is_file():
            return [basepath]

        return basepath.glob(self.file_search_pattern)

    def get_source_contents(self, sources):
        """
        Get content from allowed files.

        If pragma tag have been given, only files starting with it are elligible. Else
        all given files are elligible.

        Allowed files must starts the possible pragma tag if defined else all given files
        are validated as elligible.

        Arguments:
            sources (list): A list of Path objects for files to validate eligibility.

        Returns:
            list: List of elligible files.
        """
        elligible_files = {}

        for source in sources:
            with source.open() as f:
                # If pragma tag is enabled we sniff the file start for expected tag. The
                # tag must be exactly at the very start of content, nothing before.
                intro = None
                if self.pragma_tag:
                    intro = os.pread(f.fileno(), len(self.pragma_tag), 0)

                # Only collect source with the starting pragma tag if any is defined,
                # else every source are collected
                if not intro or intro.decode("utf-8") == self.pragma_tag:
                    elligible_files[source] = f.read()

        return elligible_files

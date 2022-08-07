"""
Attribute parser
================

The parser will search in content for seeked HTML attribute. Even it does not change
anything in content, the parser contains everything to apply lint rules.

Parser always expect attribute to be quoted with ``"`` since it is the way.

"""
import re

from .exceptions import ParserError
from .logger import BaseLogger
from .processors import ProcessorManager


class HtmlAttributeParser(ProcessorManager, BaseLogger):
    """
    Parser to get attributes from HTML source and clean their values.

    Keyword Arguments:
        attribute_name (string): The attribute name to search for. Default to
            ``class``.
    """
    def __init__(self, *args, **kwargs):
        # Attribute name to search for in HTML, default to ``class``.
        self.attribute_name = kwargs.pop("attribute_name", None) or "class"

        # Build regex for targeted attribute
        self.attribute_pattern = r"{}=\"(?:[^\"]*)(?![^\" ])[^\"]*\"".format(
            self.attribute_name,
        )
        self.attribute_start = '{}="'.format(self.attribute_name)
        self.attribute_end = '"'

        # Compile attribute matching regex
        self.attribute_regex = re.compile(self.attribute_pattern)

        super().__init__(*args, **kwargs)

    def apply_default_split(self, content):
        """
        Opposed to Rule H050 this method split on whitespace but don't remove duplicate,
        leading and trailing whitespaces.

        This is a fallback when H050 is disabled since it is required to split classes
        for further rule operations.

        Arguments:
            content (string): Attribute value.

        Returns:
            list: List of splitted items from given content with all whitespace keeped
            in place.
        """
        return content.split(" ")

    def apply_rule_H050(self, content):
        """
        Rule H050: Only a single whitespace separator and no leading or trailing
        whitespace. Also whitespace separator is allways a single space, not a
        linebreak, tabulation or other ones.

        Arguments:
            content (string): Attribute value.

        Returns:
            list: List of splitted items from given content with all whitespaces
            removed.
        """
        return content.split()

    def apply_rule_H051(self, items):
        """
        Rule H051: No duplicate keyword is allowed. This rule does not apply on possible
        whitespaces which are keeped in place.

        Arguments:
            items (list): List of splitted items from attribute value.

        Returns:
            list: List of unique keywords.
        """
        value = []

        for item in items:
            # Only first occurence of same keyword, empty strings and whitespaces are
            # keeped.
            if item == "" or item.isspace() or item not in value:
                value.append(item)

        return value

    def get_attribute_value(self, matchobj):
        """
        Return attribute value.

        Arguments:
            matchobj (re.Match): The match object to get the attribute value.
                Expect a single match group, its content must starts and ends with
                expected attribute syntax.

        Returns:
            string: Attribute value without its leading and trailing syntax.
        """
        # Failsafe for unexpected cases
        if not matchobj.group(0):
            raise ParserError("There is a empty matched object")

        if (
            not matchobj.group(0).startswith(self.attribute_start) or
            not matchobj.group(0).endswith(self.attribute_end)
        ):
            raise ParserError(
                (
                    "Matched object does not starts or ends with expected "
                    "syntax: {}".format(matchobj.group(0))
                )
            )

        return matchobj.group(0)[len(self.attribute_start):-len(self.attribute_end)]

    def attribute_cleaner(self, matchobj):
        """
        Return HTML attribute composed from value surrounded by attribute syntax.

        This base method does not apply any rule on value.

        Arguments:
            matchobj (re.Match): The match object to get the attribute value.

        Returns:
            string: HTML attribute value surrounded by attribute syntax.
        """
        return (
            self.attribute_start +
            self.get_attribute_value(matchobj) +
            self.attribute_end
        )

    def process_source(self, filepath, source):
        """
        Parse a source for attribute value.

        Arguments:
            filepath (pathlib.Path): Source file path.
            source (string): Source content.

        Returns:
            tuple: A tuple for processed source where

            - First item is the source file path (``pathlib.Path``);
            - Second item is the original source content (``string``);
            - Third item is the result of processed content (``string``).

        """
        self.log.info("🚀 Processing: {}".format(filepath))

        return (
            filepath,
            source,
            self.post_processor.render(
                self.attribute_regex.sub(
                    self.attribute_cleaner,
                    self.pre_processor.render(source)
                ),
                self.pre_processor.payload
            )
        )

    def parse_sources(self, sources):
        """
        Batch cleaning process on all given source contents.

        Arguments:
            sources (list): List of tuple for source to parse. The first tuple item is
                the source filepath (``pathlib.Path``) and the second item is the source
                content (``string``).

        Returns:
            list: Parsed and processed contents.
        """
        return [self.process_source(k, v) for k, v in sources.items()]

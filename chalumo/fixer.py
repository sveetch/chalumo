"""
Fixer
=====

Implement application of rules on source contents.

"""
from .parser import HtmlAttributeParser


class SourceFixer(HtmlAttributeParser):
    """
    Apply the parser rules on source contents.

    Keyword Arguments:
        enabled_rules (list): List of parser rule names to enable for fixes. Default to
            all available parser rules.
    """
    DEFAULT_ENABLED_RULES = ("H050", "H051")

    def __init__(self, *args, **kwargs):
        self.enabled_rules = self.DEFAULT_ENABLED_RULES
        if "enabled_rules" in kwargs:
            self.enabled_rules = kwargs.pop("enabled_rules")

        super().__init__(*args, **kwargs)

    def get_attribute_value(self, matchobj):
        """
        Return attribute value with applyed enabled rule changes.

        Arguments:
            matchobj (re.MatchObject): The match object to get the attribute value.
                Expect a single match group, its content must starts and ends with
                expected attribute syntax.

        Returns:
            string: Attribute value without its leading and trailing syntax.
        """
        value = super().get_attribute_value(matchobj)

        if "H050" in self.enabled_rules:
            items = self.apply_rule_H050(value)
        else:
            items = self.apply_default_split(value)

        if "H051" in self.enabled_rules:
            items = self.apply_rule_H051(items)

        return " ".join(items)

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

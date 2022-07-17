"""
Reformat
========

Apply rules changes on HTML attributes.

"""
from .parser import HtmlAttributeParser


class HtmlAttributeFix(HtmlAttributeParser):
    """
    Implement the attribute value fixes for rules on contents.
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


class HtmlAttributeWriter(HtmlAttributeFix):
    """
    TODO: Should also inherit from discovery and implement everything to reformat files
    in place.
    """

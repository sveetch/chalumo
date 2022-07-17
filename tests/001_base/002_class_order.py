"""
Temporary shaming sample for class inheritage order

This is more a PoC of what to do, the code it was using have been corrected to work in
any order.
"""
import pytest

from html_classes_linter.logger import BaseLogger

# First because in its old form it did not used 'super().__init(*args, **kwargs)' and so
# when coming in last it was overriding every previous inheritance __init__() and lost
# their instance attribute required by their code.
# SO, it did must comes in FIRST position to avoid overriding others inheriter brothers.
from html_classes_linter.discovery import HtmlFileDiscovery as First

# Last or any other position, this one was correctly using
# 'super().__init(*args, **kwargs)'
from html_classes_linter.parser import HtmlAttributeParser as Last


class Child(Last, First):
    """
    Demonstrate that the last position is the first Class to be called, and first
    position will be the last one to be called.

    Read it as: ::
        Last class call <-- First class call
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def attribute_cleaner(self, matchobj):
        return (
            self.attribute_start +
            "[" +
            self.get_attribute_value(matchobj) +
            "]" +
            self.attribute_end
        )

@pytest.mark.skip("Not accurate anymore since user classes have evolved")
def test_foo():
    """
    H051 rule should remove duplicate keywords.
    """
    parser = Child()
    result = parser.process_source("/foo", '<p class="plip">Foo</p>')

    assert result == (
        "/foo",
        '<p class="plip">Foo</p>',
        '<p class="[plip]">Foo</p>',
    )

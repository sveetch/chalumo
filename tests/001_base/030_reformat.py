import json

from pathlib import Path

import pytest

from html_classes_linter.reformat import HtmlAttributeFix


class MatchObject:
    """
    A dummy MatchObject for test purposes.
    """
    def __init__(self, content):
        self.content = content

    def group(self, *args, **kwargs):
        """
        No matter of args or kwargs, the given 'content' attribute is always returned.
        """
        return self.content


@pytest.mark.parametrize("content, attribute_name, expected", [
    (
        'class="foo"',
        None,
        "foo",
    ),
])
def test_get_attribute_value(settings, content, attribute_name, expected):
    """
    TODO: Adapt to cover HtmlAttributeFix correctly
    """
    kwargs = {}
    if attribute_name:
        kwargs["attribute_name"] = attribute_name

    parser = HtmlAttributeFix(**kwargs)

    value = parser.get_attribute_value(MatchObject(content))

    assert value == expected

    assert 1 == 42

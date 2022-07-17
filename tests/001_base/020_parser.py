import json

from pathlib import Path

import pytest

from html_classes_linter.discovery import HtmlFileDiscovery
from html_classes_linter.parser import HtmlAttributeParser


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


class CustomCleaner(HtmlAttributeParser):
    """
    A dummy HtmlAttributeParser inheriter to override "attribute_cleaner" which will
    enclose attribute value in brackets just to test it's working.
    """
    def attribute_cleaner(self, matchobj):
        return (
            self.attribute_start +
            "[" +
            self.get_attribute_value(matchobj) +
            "]" +
            self.attribute_end
        )


@pytest.mark.parametrize("content, attribute_name, expected", [
    (
        'class="foo"',
        None,
        "foo",
    ),
    (
        'class="foo bar"',
        None,
        "foo bar",
    ),
    (
        'class=" foo bar "',
        None,
        " foo bar ",
    ),
    (
        'wrong',
        None,
        "wrong",
    ),
    (
        'data-plip-plop="foo"',
        "data-plip-plop",
        "foo",
    ),
])
def test_get_attribute_value(settings, content, attribute_name, expected):
    """
    Attribute parser should return only attribute value unaltered.
    """
    kwargs = {}
    if attribute_name:
        kwargs["attribute_name"] = attribute_name

    parser = HtmlAttributeParser(**kwargs)

    value = parser.get_attribute_value(MatchObject(content))

    assert value == expected


@pytest.mark.parametrize("content, expected", [
    (
        'class="foo"',
        'class="[foo]"',
    ),
    (
        '<p class="foo bar">Lorem ipsum</p>',
        '<p class="[foo bar]">Lorem ipsum</p>',
    ),
    (
        "<p class='foo bar'>Lorem ipsum</p>",
        "<p class='foo bar'>Lorem ipsum</p>",
    ),
    (
        '<p class="foo bar"">Lorem ipsum</p>',
        '<p class="[foo bar]"">Lorem ipsum</p>',
    ),
    (
        (
            '<p class="foo bar">'
            '<span id="id-foo" class=" foo  bar ">Lorem ipsum</span>'
            '</p>'
            '<h1 id="pang" class="ping" data-flip="flop">Pong</h1>'
        ),
        (
            '<p class="[foo bar]">'
            '<span id="id-foo" class="[ foo  bar ]">Lorem ipsum</span>'
            '</p>'
            '<h1 id="pang" class="[ping]" data-flip="flop">Pong</h1>'
        ),
    ),
    (
        '<div class="foo bar-{% cycle "1" "2" "3" %}">Lorem ipsum</div>',
        '<div class="[foo bar-{% cycle "1" "2" "3" %}]">Lorem ipsum</div>',
    ),
])
def test_process_source(content, expected):
    """
    Processed source should correctly reformat the attribute.
    """
    parser = CustomCleaner()

    filepath, source, modified = parser.process_source("/foo", content)

    assert filepath == "/foo"
    assert source == content
    assert modified == expected


@pytest.mark.parametrize("content, expected", [
    (
        "foo",
        ["foo"],
    ),
    (
        "foo bar",
        ["foo", "bar"],
    ),
    (
        "foo \nbar",
        ["foo", "\nbar"],
    ),
    (
        " foo  bar ping \n  pong ",
        ["", "foo", "", "bar", "ping", "\n", "", "pong", ""],
    ),
])
def test_apply_default_split(content, expected):
    """
    Default split method does not remove any duplicate, leading or trailing whitespaces.
    """
    parser = HtmlAttributeParser()

    result = parser.apply_default_split(content)

    assert result == expected


@pytest.mark.parametrize("content, expected", [
    (
        "foo",
        ["foo"],
    ),
    (
        "foo bar",
        ["foo", "bar"],
    ),
    (
        "foo \nbar",
        ["foo", "bar"],
    ),
    (
        " foo  bar ping \n  pong ",
        ["foo", "bar", "ping", "pong"],
    ),
])
def test_apply_rule_H050(content, expected):
    """
    H050 rule split classes and remove duplicate, leading and trailing whitespaces.
    """
    parser = HtmlAttributeParser()

    result = parser.apply_rule_H050(content)

    assert result == expected


@pytest.mark.parametrize("content, expected", [
    (
        "foo",
        ["foo"],
    ),
    (
        "foo bar",
        ["foo", "bar"],
    ),
    (
        "foo bar foo foo bar",
        ["foo", "bar"],
    ),
    (
        "foo \nbar",
        ["foo", "\nbar"],
    ),
    (
        " foo  bar ping \n  pong ",
        ["", "foo", "", "bar", "ping", "\n", "", "pong", ""],
    ),
])
def test_apply_rule_H051(content, expected):
    """
    H051 rule should remove duplicate keywords.
    """
    parser = HtmlAttributeParser()

    # Use conservative splitter to ensure both H050 and default split behavior
    splitted = parser.apply_default_split(content)

    result = parser.apply_rule_H051(splitted)

    assert result == expected

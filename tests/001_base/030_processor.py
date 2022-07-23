"""
Work In Progress

There is some R&D stuff to remove once finished.
"""
from pathlib import Path

import pytest

from html_classes_linter.parser import HtmlAttributeParser
from html_classes_linter.processor import DjangoPreProcessor, DjangoPostProcessor

from django.template.base import (
    Lexer, TokenType,
    BLOCK_TAG_START, BLOCK_TAG_END, VARIABLE_TAG_START, VARIABLE_TAG_END,
    COMMENT_TAG_START, COMMENT_TAG_END
)


class MockedHtmlAttributeParser(HtmlAttributeParser):
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


class MockedDjangoPreProcessor(DjangoPreProcessor):
    """
    Override the get_unique_key method to use dummy counter instead so it shoud be
    safe to test.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_key_counter = 0

    def _get_unique_key(self):
        self.test_key_counter += 1
        return str(self.test_key_counter).zfill(3)


def test_django_template_parser():
    """
    Basic demonstration of Django template lexer behavior
    """
    source = (
        '<div class="'
            'foo'
            '{% if foo == "" %}'
                ' plop'
                '{% if bar == "" %}'
                    ' plop'
                '{% endif %}'
            '{%else%}'
                ' {{ foo }} {{ bar }}'
                '{% include "something.html" %}'
                '{# nope #}'
            '{% endif %}'
        '">Lorem ipsum</div>'
    )
    tokens = Lexer(source).tokenize()

    print()
    print("Lexer return type:", type(tokens))
    print("Tokens:", len(tokens))
    print()
    for token in tokens:
        print(token, token.token_type, token.lineno, token.position, (token.token_type == TokenType.BLOCK))

    # Source template is correctly cutted in expected tokens types
    assert len([item for item in tokens if (item.token_type == TokenType.TEXT)]) == 6
    assert len([item for item in tokens if (item.token_type == TokenType.VAR)]) == 2
    assert len([item for item in tokens if (item.token_type == TokenType.BLOCK)]) == 6
    assert len([item for item in tokens if (item.token_type == TokenType.COMMENT)]) == 1


@pytest.mark.parametrize("source, expected, isolated", [
    (
        '<div class="foo bar-{% cycle "1" "2" "3" %}">Lorem ipsum</div>',
        '<div class="foo bar-⸦⸨⸠001⸡⸩⸧">Lorem ipsum</div>',
        {
            "001": '{% cycle "1" "2" "3" %}',
        }
    ),
    (
        '{% if foo %} bar{% endif %} {% if plip %} {{plip}}{% endif %} {{ ping }}',
        '⸦⸨⸠001⸡⸩⸧ bar⸦⸨⸠002⸡⸩⸧ ⸦⸨⸠003⸡⸩⸧ ⸦⸨⸠004⸡⸩⸧⸦⸨⸠005⸡⸩⸧ ⸦⸨⸠006⸡⸩⸧',
        {
            "001": "{% if foo %}",
            "002": "{% endif %}",
            "003": "{% if plip %}",
            "004": "{{ plip }}",
            "005": "{% endif %}",
            "006": "{{ ping }}",
        },
    ),
    (
        ' {% if foo %} bar {% endif %}  {% if plip %} {{plip }}{% endif %} {{ ping }}',
        ' ⸦⸨⸠001⸡⸩⸧ bar ⸦⸨⸠002⸡⸩⸧  ⸦⸨⸠003⸡⸩⸧ ⸦⸨⸠004⸡⸩⸧⸦⸨⸠005⸡⸩⸧ ⸦⸨⸠006⸡⸩⸧',
        {
            "001": "{% if foo %}",
            "002": "{% endif %}",
            "003": "{% if plip %}",
            "004": "{{ plip }}",
            "005": "{% endif %}",
            "006": "{{ ping }}",
        },
    ),
])
def test_django_preprocessor(source, expected, isolated):
    """
    Pre-processor should correctly isolate every non text part and store original
    references.
    """
    preprocessor = MockedDjangoPreProcessor(source)

    rendered = preprocessor.render()

    assert rendered == expected

    assert preprocessor.isolated_references == isolated


@pytest.mark.parametrize("source, expected", [
    (
        'foo bar-{% cycle "1" "2" "3" %}',
        'foo bar-⸦⸨⸠001⸡⸩⸧',
    ),
    (
        '<div class="foo bar-{% cycle "1" "2" "3" %}">Lorem ipsum</div>',
        '<div class="[foo bar-⸦⸨⸠001⸡⸩⸧]">Lorem ipsum</div>',
    ),
    (
        '<div {% if foo %}class="foo {% cycle "1" "2" "3" %}"{% else %} class="nope"{% endif %}>Lorem ipsum</div>',
        '<div ⸦⸨⸠001⸡⸩⸧class="[foo ⸦⸨⸠002⸡⸩⸧]"⸦⸨⸠003⸡⸩⸧ class="[nope]"⸦⸨⸠004⸡⸩⸧>Lorem ipsum</div>',
    ),
])
def test_preprocessed_parser(source, expected):
    """
    Check if pre processor technique does not break the parser.
    """
    parser = MockedHtmlAttributeParser()
    preprocessor = MockedDjangoPreProcessor(source)

    rendered = preprocessor.render()

    filepath, original, modified = parser.process_source("/foo", rendered)

    print(modified)

    assert filepath == "/foo"
    assert modified == expected


@pytest.mark.parametrize("source, expected, isolated", [
    (
        '<div class="foo bar-⸦⸨⸠001⸡⸩⸧">Lorem ipsum</div>',
        '<div class="foo bar-{% cycle "1" "2" "3" %}">Lorem ipsum</div>',
        {
            "001": '{% cycle "1" "2" "3" %}',
        }
    ),
    (
        '<div ⸦⸨⸠001⸡⸩⸧class="foo ⸦⸨⸠002⸡⸩⸧"\n⸦⸨⸠003⸡⸩⸧ \n    class="nope"⸦⸨⸠004⸡⸩⸧>Lorem ipsum</div>',
        '<div {% if foo %}class="foo {% cycle "1" "2" "3" %}"\n{% else %} \n    class="nope"{% endif %}>Lorem ipsum</div>',
        {
            "001": '{% if foo %}',
            "002": '{% cycle "1" "2" "3" %}',
            "003": '{% else %}',
            "004": '{% endif %}',
        }
    ),
])
def test_django_postprocessor(source, expected, isolated):
    """
    Post-processor should correctly restore isolated content in the right place.
    """
    postprocessor = DjangoPostProcessor(source, isolated, DjangoPreProcessor.REFERENCE_SYNTAX)

    rendered = postprocessor.render()

    assert rendered == expected


@pytest.mark.parametrize("source, expected", [
    (
        'foo bar-{% cycle "1" "2" "3" %}',
        'foo bar-{% cycle "1" "2" "3" %}',
    ),
    (
        '<div class="foo bar-{% cycle "1" "2" "3" %}">Lorem ipsum</div>',
        '<div class="[foo bar-{% cycle "1" "2" "3" %}]">Lorem ipsum</div>',
    ),
    (
        '<div {% if foo %}class="foo {% cycle "1" "2" "3" %}"{% else %} class="nope"{% endif %}>Lorem ipsum</div>',
        '<div {% if foo %}class="[foo {% cycle "1" "2" "3" %}]"{% else %} class="[nope]"{% endif %}>Lorem ipsum</div>',
    ),
    (
        '<div class="foo{% if foo == "" %} plop{% if bar == "" %} plop{% endif %}{%else%} {{ foo }} {{ bar }}{% include "something.html" %}{# nope #}{% endif %}">Lorem ipsum</div>',
        '<div class="[foo{% if foo == "" %} plop{% if bar == "" %} plop{% endif %}{% else %} {{ foo }} {{ bar }}{% include "something.html" %}{# nope #}{% endif %}]">Lorem ipsum</div>',
    ),
])
def test_postprocessed_parser(source, expected):
    """
    Check the full technique flow with pre processor, parser and post processor.
    """
    parser = MockedHtmlAttributeParser()

    preprocessor = DjangoPreProcessor(source)
    pre_rendered = preprocessor.render()

    filepath, original, modified = parser.process_source("/foo", pre_rendered)

    postprocessor = DjangoPostProcessor(modified, preprocessor.isolated_references, preprocessor.reference_syntax)
    post_rendered = postprocessor.render()

    assert filepath == "/foo"
    assert post_rendered == expected

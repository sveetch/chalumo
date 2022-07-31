import pytest

from chalumo.parser import HtmlAttributeParser
from chalumo.processors.django import (
    DjangoPreProcessor, DjangoPostProcessor,
)

from django.template.base import Lexer, TokenType


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
        print(
            token, token.token_type, token.lineno, token.position,
            (token.token_type == TokenType.BLOCK)
        )

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
    preprocessor = MockedDjangoPreProcessor()

    rendered = preprocessor.render(source)

    assert rendered == expected

    assert preprocessor.payload == isolated


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
        (
            '<div {% if foo %}class="foo {% cycle "1" "2" "3" %}"{% else %} '
            'class="nope"{% endif %}>Lorem ipsum</div>'
        ),
        (
            '<div ⸦⸨⸠001⸡⸩⸧class="[foo ⸦⸨⸠002⸡⸩⸧]"⸦⸨⸠003⸡⸩⸧ class="[nope]"⸦⸨⸠004⸡⸩⸧>'
            'Lorem ipsum</div>'
        ),
    ),
])
def test_django_preprocessed_parser(source, expected):
    """
    Check if pre processor technique does not break the parser.
    """
    preprocessor = MockedDjangoPreProcessor()
    rendered = preprocessor.render(source)

    parser = MockedHtmlAttributeParser()
    filepath, original, modified = parser.process_source("/foo", rendered)

    print(modified)

    assert filepath == "/foo"
    assert modified == expected


@pytest.mark.parametrize("source, expected, references", [
    (
        '<div class="foo bar-⸦⸨⸠001⸡⸩⸧">Lorem ipsum</div>',
        '<div class="foo bar-{% cycle "1" "2" "3" %}">Lorem ipsum</div>',
        {
            "001": '{% cycle "1" "2" "3" %}',
        }
    ),
    (
        (
            '<div ⸦⸨⸠001⸡⸩⸧class="foo ⸦⸨⸠002⸡⸩⸧"\n⸦⸨⸠003⸡⸩⸧ \n    '
            'class="nope"⸦⸨⸠004⸡⸩⸧>Lorem ipsum</div>'
        ),
        (
            '<div {% if foo %}class="foo {% cycle "1" "2" "3" %}"\n{% else %} \n    '
            'class="nope"{% endif %}>Lorem ipsum</div>'
        ),
        {
            "001": '{% if foo %}',
            "002": '{% cycle "1" "2" "3" %}',
            "003": '{% else %}',
            "004": '{% endif %}',
        }
    ),
])
def test_django_postprocessor(source, expected, references):
    """
    Post-processor should correctly restore isolated content in the right place.
    """
    postprocessor = DjangoPostProcessor(DjangoPreProcessor.REFERENCE_SYNTAX)

    rendered = postprocessor.render(source, references)

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
        (
            '<div {% if foo %}class="foo {% cycle "1" "2" "3" %}"{% else %} '
            'class="nope"{% endif %}>Lorem ipsum</div>'
        ),
        (
            '<div {% if foo %}class="[foo {% cycle "1" "2" "3" %}]"{% else %} '
            'class="[nope]"{% endif %}>Lorem ipsum</div>'
        ),
    ),
    (
        (
            '<div class="foo{% if foo == "" %} plop{% if bar == "" %} '
            'plop{% endif %}{%else%} {{ foo }} {{ bar }}{% include "something.html" %}'
            '{# nope #}{% endif %}">Lorem ipsum</div>'
        ),
        (
            '<div class="[foo{% if foo == "" %} plop{% if bar == "" %} plop{% endif %}'
            '{% else %} {{ foo }} {{ bar }}{% include "something.html" %}{# nope #}'
            '{% endif %}]">Lorem ipsum</div>'
        ),
    ),
])
def test_django_process_combination(source, expected):
    """
    Combine usage of pre processor, parser and post processor to check the full
    technique flow.
    """
    preprocessor = DjangoPreProcessor()
    pre_rendered = preprocessor.render(source)

    # Use the parser without Django compatibility enabled so we can manually use them
    parser = MockedHtmlAttributeParser()
    filepath, original, modified = parser.process_source("/foo", pre_rendered)

    postprocessor = DjangoPostProcessor(preprocessor.reference_syntax)
    post_rendered = postprocessor.render(modified, preprocessor.payload)

    assert filepath == "/foo"
    assert post_rendered == expected


@pytest.mark.parametrize("source, expected", [
    (
        (
            '<div {% if foo %}class="foo {% cycle "1" "2" "3" %}"{% else %} '
            'class="nope"{% endif %}>Lorem ipsum</div>'
        ),
        (
            '<div {% if foo %}class="[foo {% cycle "1" "2" "3" %}]"{% else %} '
            'class="[nope]"{% endif %}>Lorem ipsum</div>'
        ),
    ),
    (
        (
            '<i class="{{ sample_icon }} icon-{{ k }}"></i>'
        ),
        (
            '<i class="[{{ sample_icon }} icon-{{ k }}]"></i>'
        ),
    ),
    (
        (
            '<div class="swiper-slide product-{% cycle "1" "2" "3" %}">'
        ),
        (
            '<div class="[swiper-slide product-{% cycle "1" "2" "3" %}]">'
        ),
    ),
])
def test_django_full_process(source, expected):
    """
    Use the parser with processor management.
    """
    parser = MockedHtmlAttributeParser(compatibility="django")
    filepath, original, modified = parser.process_source("/foo", source)

    assert filepath == "/foo"
    assert modified == expected

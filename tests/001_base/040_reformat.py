import pytest

from html_classes_linter.reformat import SourceFixer


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


@pytest.mark.skip("TODO")
@pytest.mark.parametrize("content, attribute_name, expected", [
    (
        'class="foo"',
        None,
        "foo",
    ),
])
def test_get_attribute_value(settings, content, attribute_name, expected):
    """
    TODO: Dummy sample to adapt to fully cover SourceFixer
    """
    kwargs = {}
    if attribute_name:
        kwargs["attribute_name"] = attribute_name

    parser = SourceFixer(**kwargs)

    value = parser.get_attribute_value(MatchObject(content))

    assert value == expected

    assert 1 == 42

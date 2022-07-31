from pathlib import Path

import pytest

from chalumo.diff import SourceDiff


class MockedSourceDiff(SourceDiff):
    """
    Mocked version for test purpose
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store every echoed content in a list so we can easily check it
        self.mocked_output = []
        self.echo = self.store_output

    def store_output(self, content=""):
        # print(content)
        self.mocked_output.append(content)


@pytest.mark.parametrize(
    "filepath, from_source, to_source, expected_from, expected_to",
    [
        (
            Path("foo/bar/plip.html"),
            '<p class="foo">plop</p>',
            '<a class="foo">plop</a>',
            "--- foo/bar/plip.html\n",
            "+++ foo/bar/plip.html\n",
        ),
    ]
)
def test_diff_source(filepath, from_source, to_source, expected_from, expected_to):
    """
    Method diff_source should return a generator for diff output lines as expected.
    """
    differ = SourceDiff()

    result = list(
        differ.diff_source(filepath, from_source, to_source)
    )

    # We only check about the first diff lines with files
    assert result[0] == expected_from
    assert result[1] == expected_to


@pytest.mark.parametrize("sourcepath, expected", [
    (
        Path("sample_structure/subdir_1"),
        [
            '--- {FIXTURES}/sample_structure/subdir_1/ping.html',
            '+++ {FIXTURES}/sample_structure/subdir_1/ping.html',
            '@@ -1,7 +1,7 @@',
            ' {{# djlint:on #}}',
            ' {{% comment %}}A comment{{% endcomment %}}',
            '-<div class=" ping plip  plop ">',
            '-    <div class="envelope  foo   bar">',
            '+<div class="ping plip plop">',
            '+    <div class="envelope foo bar">',
            '         <h1>Ping world!</h1>',
            '     </div>',
            ' </div>',
            '',
            '--- {FIXTURES}/sample_structure/subdir_1/subdir_1_1/pong.html',
            '+++ {FIXTURES}/sample_structure/subdir_1/subdir_1_1/pong.html',
            '@@ -1,7 +1,7 @@',
            ' {{# djlint:on #}}',
            ' {{% comment %}}A comment{{% endcomment %}}',
            '-<div class=" pong plip  plop ">',
            '-    <div class="envelope  foo   bar">',
            '+<div class="pong plip plop">',
            '+    <div class="envelope foo bar">',
            '         <h1>Pong world!</h1>',
            '     </div>',
            ' </div>',
            '',
        ],
    ),
    (
        Path("sample_structure/subdir_1/ping.html"),
        [
            '--- {FIXTURES}/sample_structure/subdir_1/ping.html',
            '+++ {FIXTURES}/sample_structure/subdir_1/ping.html',
            '@@ -1,7 +1,7 @@',
            ' {{# djlint:on #}}',
            ' {{% comment %}}A comment{{% endcomment %}}',
            '-<div class=" ping plip  plop ">',
            '-    <div class="envelope  foo   bar">',
            '+<div class="ping plip plop">',
            '+    <div class="envelope foo bar">',
            '         <h1>Ping world!</h1>',
            '     </div>',
            ' </div>',
            '',
        ],
    ),
])
def test_diff_run(settings, sourcepath, expected):
    """
    Running diff on sources should output a correct unified diff for changes from
    rules applications.
    """
    # Use pragma tag to limit output
    differ = MockedSourceDiff(pragma_tag="{# djlint:on #}")

    basepath = settings.fixtures_path / sourcepath

    differ.run(basepath)

    # Rewrite content lines to insert fixtures path
    expected = [settings.format(item) for item in expected]

    # Break each source diff output on newline and merge all source output in a single
    # list
    output = []
    for item in differ.mocked_output:
        output.extend(item.split("\n"))

    assert output == expected

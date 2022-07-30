import shutil

from pathlib import Path

from html_classes_linter.reformat import SourceWriter


def test_reformat_run(settings, tmp_path):
    """
    SourceWriter should rewrite source content with applied rules fixes.
    """
    formatter = SourceWriter(pragma_tag="{# djlint:on #}")

    # Copy sources structure from data fixtures
    source_fixtures_path = settings.fixtures_path / Path("sample_structure/subdir_1")
    destination_fixtures_path = tmp_path / Path("subdir_1")
    basepath = shutil.copytree(source_fixtures_path, destination_fixtures_path)

    expected = {
        "notag_ping.html": (
            '{% comment %}A comment{% endcomment %}\n'
            '<div class=" nope-ping plip  plop ">\n'
            '    <div class="envelope  foo   bar">\n'
            '        <h1>Ping nope!</h1>\n'
            '    </div>\n'
            '</div>\n'
        ),
        "ping.html": (
            '{# djlint:on #}\n'
            '{% comment %}A comment{% endcomment %}\n'
            '<div class="ping plip plop">\n'
            '    <div class="envelope foo bar">\n'
            '        <h1>Ping world!</h1>\n'
            '    </div>\n'
            '</div>\n'
        ),
        "subdir_1_1/pong.html": (
            '{# djlint:on #}\n'
            '{% comment %}A comment{% endcomment %}\n'
            '<div class="pong plip plop">\n'
            '    <div class="envelope foo bar">\n'
            '        <h1>Pong world!</h1>\n'
            '    </div>\n'
            '</div>\n'
        ),
    }

    # Run source rewriting
    formatter.run(basepath)

    # Then check expected rewrited sources
    for name, content in expected.items():
        source = destination_fixtures_path / name
        print(source)
        assert source.read_text() == content

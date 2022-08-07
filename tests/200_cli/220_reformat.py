import logging
import shutil
from pathlib import Path

from click.testing import CliRunner

from chalumo.cli.entrypoint import cli_frontend


def test_reformat_missing_basepath(caplog):
    """
    Invoked without required 'basepath' argument the command should fails.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli_frontend, ["reformat"])

        assert result.exit_code == 2

        assert caplog.record_tuples == []


def test_reformat_basic(caplog, settings):
    """
    Command should succeed to rewrite every sources and output logs
    """
    sources_path = settings.fixtures_path / Path("sample_structure/subdir_1")
    print("sources_path:", sources_path)

    runner = CliRunner()
    with runner.isolated_filesystem():
        print("cwd:", Path.cwd())
        basepath = Path.cwd() / Path("subdir_1")
        shutil.copytree(sources_path, basepath)
        print("basepath:", basepath)

        result = runner.invoke(cli_frontend, ["reformat", str(basepath)])

        print()
        print(result.output)
        print()

        assert result.exit_code == 0

        assert caplog.record_tuples == [
            (
                "chalumo",
                logging.INFO,
                "📂 Opening base directory: {}".format(basepath)
            ),
            (
                "chalumo",
                logging.INFO,
                "🔧 Using pattern: **/*.html"
            ),
            (
                "chalumo",
                logging.INFO,
                "🔧 Profile: html"
            ),
            (
                "chalumo",
                logging.INFO,
                "🚀 Processing: {}/notag_ping.html".format(basepath)
            ),
            (
                "chalumo",
                logging.INFO,
                "🚀 Processing: {}/ping.html".format(basepath)
            ),
            (
                "chalumo",
                logging.INFO,
                "🚀 Processing: {}/subdir_1_1/pong.html".format(basepath)
            ),
        ]

        expected = {
            "notag_ping.html": (
                '{% comment %}A comment{% endcomment %}\n'
                '<div class="nope-ping plip plop">\n'
                '    <div class="envelope foo bar">\n'
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

        # Then check expected rewrited sources
        for name, content in expected.items():
            source = basepath / name
            print(source)
            assert source.read_text() == content

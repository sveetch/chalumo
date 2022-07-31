"""
NOTE:

The diff command is used to test the common shared options so that other commands
do no test them again.
"""
import logging
import shutil
from pathlib import Path

from click.testing import CliRunner

from chalumo.cli.entrypoint import cli_frontend


def test_diff_missing_basepath(caplog):
    """
    Invoked without required 'basepath' argument the command should fails.
    """
    runner = CliRunner()
    with runner.isolated_filesystem():
        test_cwd = Path.cwd()

        result = runner.invoke(cli_frontend, ["diff"])

        assert result.exit_code == 2

        assert caplog.record_tuples == []


def test_diff_basic_logs(caplog, settings):
    """
    Command should succeed and output logs
    """
    sources_path = settings.fixtures_path / Path("sample_structure/subdir_1")
    print("sources_path:", sources_path)

    runner = CliRunner()
    with runner.isolated_filesystem():
        print("cwd:", Path.cwd())
        basepath = Path.cwd() / Path("subdir_1")
        shutil.copytree(sources_path, basepath)
        print("basepath:", basepath)

        result = runner.invoke(cli_frontend, ["diff", str(basepath)])

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


def test_diff_basic_output(caplog, settings):
    """
    Command should succeed to rewrite every sources
    """
    sources_path = settings.fixtures_path / Path("sample_structure/subdir_1")
    print("sources_path:", sources_path)

    runner = CliRunner()
    with runner.isolated_filesystem():
        print("cwd:", Path.cwd())
        basepath = Path.cwd() / Path("subdir_1")
        shutil.copytree(sources_path, basepath)
        print("basepath:", basepath)

        result = runner.invoke(cli_frontend, [
            "--verbose", "0",
            "diff",
            str(basepath)
        ])

        print()
        print(result.output)
        print()

        assert result.exit_code == 0

        expected = [
            '--- {}/notag_ping.html',
            '+++ {}/notag_ping.html',
            '@@ -1,6 +1,6 @@',
            ' {{% comment %}}A comment{{% endcomment %}}',
            '-<div class=" nope-ping plip  plop ">',
            '-    <div class="envelope  foo   bar">',
            '+<div class="nope-ping plip plop">',
            '+    <div class="envelope foo bar">',
            '         <h1>Ping nope!</h1>',
            '     </div>',
            ' </div>',
            '',
            '--- {}/ping.html',
            '+++ {}/ping.html',
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
            '--- {}/subdir_1_1/pong.html',
            '+++ {}/subdir_1_1/pong.html',
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
            ''
        ]
        # Rewrite content lines to insert temporary basepath
        expected = [item.format(basepath) for item in expected]

        assert result.output == "\n".join(expected)


def test_diff_basic_pragma(caplog, settings):
    """
    Command should succeed to rewrite only sources which start with given tag.
    """
    sources_path = settings.fixtures_path / Path("sample_structure/subdir_1")
    print("sources_path:", sources_path)

    runner = CliRunner()
    with runner.isolated_filesystem():
        print("cwd:", Path.cwd())
        basepath = Path.cwd() / Path("subdir_1")
        shutil.copytree(sources_path, basepath)
        print("basepath:", basepath)

        result = runner.invoke(cli_frontend, [
            "--verbose", "0",
            "diff",
            "--require-pragma", "{# djlint:on #}",
            str(basepath)
        ])

        print()
        print(result.output)
        print()

        assert result.exit_code == 0

        expected = [
            '--- {}/ping.html',
            '+++ {}/ping.html',
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
            '--- {}/subdir_1_1/pong.html',
            '+++ {}/subdir_1_1/pong.html',
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
            ''
        ]
        # Rewrite content lines to insert temporary basepath
        expected = [item.format(basepath) for item in expected]

        assert result.output == "\n".join(expected)


def test_diff_basic_singlefile(caplog, settings):
    """
    Command should succeed to rewrite a single source filepath
    """
    sources_path = settings.fixtures_path / Path("sample_structure/subdir_1")
    print("sources_path:", sources_path)

    runner = CliRunner()
    with runner.isolated_filesystem():
        print("cwd:", Path.cwd())
        basepath = Path.cwd() / Path("subdir_1")
        shutil.copytree(sources_path, basepath)
        print("basepath:", basepath)

        result = runner.invoke(cli_frontend, [
            "--verbose", "0",
            "diff",
            str(basepath / "ping.html")
        ])

        print()
        print(result.output)
        print()

        assert result.exit_code == 0

        expected = [
            '--- {}/ping.html',
            '+++ {}/ping.html',
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
            '',
        ]
        # Rewrite content lines to insert temporary basepath
        expected = [item.format(basepath) for item in expected]

        assert result.output == "\n".join(expected)


def test_diff_basic_profile_django(caplog, settings):
    """
    Command should succeed to correctly rewrite a Django template source
    """
    sources_path = settings.fixtures_path / Path("sample_structure/subdir_2")
    print("sources_path:", sources_path)

    runner = CliRunner()
    with runner.isolated_filesystem():
        print("cwd:", Path.cwd())
        basepath = Path.cwd() / Path("subdir_2")
        shutil.copytree(sources_path, basepath)
        print("basepath:", basepath)

        result = runner.invoke(cli_frontend, [
            "--verbose", "0",
            "diff",
            str(basepath / "subdir_2_1/zap.html"),
            "--profile", "django",
        ])

        print()
        print(result.output)
        print()

        assert result.exit_code == 0

        expected = [
            '--- {}/subdir_2_1/zap.html',
            '+++ {}/subdir_2_1/zap.html',
            '@@ -1,7 +1,7 @@',
            ' {{# djlint:on #}}',
            ' {{% comment %}}A comment{{% endcomment %}}',
            '-<div class=" zap plip  {{% dummytag "meh" %}}  plop ">',
            '-    <div class="envelope  foo   bar">',
            '+<div class="zap plip {{% dummytag "meh" %}} plop">',
            '+    <div class="envelope foo bar">',
            '         <h1>Zap world!</h1>',
            '     </div>',
            ' </div>',
            '',
            '',
        ]
        # Rewrite content lines to insert temporary basepath
        expected = [item.format(basepath) for item in expected]

        assert result.output == "\n".join(expected)

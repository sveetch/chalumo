import json

import pytest

from html_classes_linter.discovery import HtmlFileDiscovery


def test_get_source_files(settings):
    """
    With default pattern to get only HTML files
    """
    discoverer = HtmlFileDiscovery()

    basepath = settings.fixtures_path / "sample_structure"

    sources = sorted([
        str(item.relative_to(basepath))
        for item in discoverer.get_source_files(basepath)
    ])

    #print(json.dumps(sources, indent=4))

    assert sources == [
        "basic.html",
        "empty.html",
        "no_content.html",
        "subdir_1/notag_ping.html",
        "subdir_1/ping.html",
        "subdir_1/subdir_1_1/pong.html",
        "subdir_2/notag_zip.html",
        "subdir_2/subdir_2_1/zap.html"
    ]


def test_get_source_files_pattern(settings):
    """
    With a pattern to match every files
    """
    discoverer = HtmlFileDiscovery(file_search_pattern="**/*.*")

    basepath = settings.fixtures_path / "sample_structure"

    sources = sorted([
        str(item.relative_to(basepath))
        for item in discoverer.get_source_files(basepath)
    ])

    #print(json.dumps(sources, indent=4))

    assert sources == [
        "basic.html",
        "empty.html",
        "no_content.html",
        "not_html.txt",
        "subdir_1/notag_ping.html",
        "subdir_1/ping.html",
        "subdir_1/subdir_1_1/pong.html",
        "subdir_2/not_html.txt",
        "subdir_2/notag_zip.html",
        "subdir_2/subdir_2_1/zap.html"
    ]


def test_get_source_contents_pragma(settings):
    """
    With a pragma tag, only files with content starting with the pragma tag are
    elligible.
    """
    discoverer = HtmlFileDiscovery(pragma_tag="{# djlint:on #}")

    basepath = settings.fixtures_path / "sample_structure"

    found = discoverer.get_source_files(basepath)

    sources = sorted([
        str(filepath.relative_to(basepath))
        for filepath, content in discoverer.get_source_contents(found).items()
    ])

    #print(json.dumps(sources, indent=4))

    assert sources == [
        "basic.html",
        "empty.html",
        "no_content.html",
        "subdir_1/ping.html",
        "subdir_1/subdir_1_1/pong.html",
        "subdir_2/subdir_2_1/zap.html"
    ]


def test_get_source_contents_nopragma(settings):
    """
    Without any pragma tag, every file matching pattern is elligible.
    """
    discoverer = HtmlFileDiscovery()

    basepath = settings.fixtures_path / "sample_structure"

    found = discoverer.get_source_files(basepath)

    sources = sorted([
        str(filepath.relative_to(basepath))
        for filepath, content in discoverer.get_source_contents(found).items()
    ])

    #print(json.dumps(sources, indent=4))

    assert sources == [
        "basic.html",
        "empty.html",
        "no_content.html",
        "subdir_1/notag_ping.html",
        "subdir_1/ping.html",
        "subdir_1/subdir_1_1/pong.html",
        "subdir_2/notag_zip.html",
        "subdir_2/subdir_2_1/zap.html"
    ]

from html_classes_linter.discovery import SourceDiscovery


def test_get_source_files(settings):
    """
    With default pattern to get only HTML files
    """
    discoverer = SourceDiscovery()

    basepath = settings.fixtures_path / "sample_structure"

    sources = sorted([
        str(item.relative_to(basepath))
        for item in discoverer.get_source_files(basepath)
    ])

    # print(json.dumps(sources, indent=4))

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


def test_get_source_files_pattern_all_files(settings):
    """
    With a pattern to match every files
    """
    discoverer = SourceDiscovery(file_search_pattern="**/*.*")

    basepath = settings.fixtures_path / "sample_structure"

    sources = sorted([
        str(item.relative_to(basepath))
        for item in discoverer.get_source_files(basepath)
    ])

    # print(json.dumps(sources, indent=4))

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


def test_get_source_files_single_file(settings):
    """
    Discovery should accept also a single file path instead of a directory base path,
    in this case it will disable the glob pattern.
    """
    # Use a pattern that won't match any template if glob pattern was enabled
    discoverer = SourceDiscovery(file_search_pattern="**/*.txt")

    basepath = settings.fixtures_path / "sample_structure" / "basic.html"

    # We don't use relative path since basepath is the file path and it would resume
    # to "."
    sources = [
        str(basepath.name)
        for item in discoverer.get_source_files(basepath)
    ]

    assert sources == ["basic.html"]


def test_get_source_contents_pragma(settings):
    """
    With a pragma tag, only files with content starting with the pragma tag are
    elligible.
    """
    discoverer = SourceDiscovery(pragma_tag="{# djlint:on #}")

    basepath = settings.fixtures_path / "sample_structure"

    found = discoverer.get_source_files(basepath)

    sources = sorted([
        str(filepath.relative_to(basepath))
        for filepath, content in discoverer.get_source_contents(found).items()
    ])

    # print(json.dumps(sources, indent=4))

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
    discoverer = SourceDiscovery()

    basepath = settings.fixtures_path / "sample_structure"

    found = discoverer.get_source_files(basepath)

    sources = sorted([
        str(filepath.relative_to(basepath))
        for filepath, content in discoverer.get_source_contents(found).items()
    ])

    # print(json.dumps(sources, indent=4))

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

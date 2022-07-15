"""
Main entrance to commandline actions

Since Click use function docstring to build its help content, no command
function are documented.
"""
from pathlib import Path

import click

from html_classes_linter import __version__

from html_classes_linter.logger import init_logger

from html_classes_linter.linter import HtmlAttributeCleaner


# Default logger conf
APP_LOGGER_CONF = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", None)


@click.command()
@click.argument(
    "basepath",
    type=click.Path(
        file_okay=False, dir_okay=True, writable=True, resolve_path=True,
        path_type=Path, exists=True,
    ),
    required=False,
)
@click.option(
    "--mode",
    metavar="STRING",
    prompt="Operation mode",
    type=click.Choice(["lint", "diff", "reformat"]),
    help=(
        "Operation mode to perform. "
        "'lint' will just perform parse and return problems."
    ),
    default="lint"
)
@click.option(
    '-v', '--verbose',
    type=click.IntRange(min=0, max=5),
    show_default=True,
    default=4,
    metavar='INTEGER',
    help=(
        "An integer between 0 and 5, where '0' make a totaly "
        "silent output and '5' set level to DEBUG (the most verbose "
        "level)."
    )
)
@click.option(
    "--version",
    "version_mode",
    is_flag=True,
    help="Output application version and exit. Other operation modes are ignored."
)
def cli_frontend(basepath, mode, verbose, version_mode):
    """
    Lint HTML files for messy 'class' attribute contents.
    """
    printout = True
    if verbose == 0:
        verbose = 1
        printout = False

    # Verbosity is the inverse of logging levels
    levels = [item for item in APP_LOGGER_CONF]
    levels.reverse()
    # Init the logger config
    logger = init_logger(
        "html-classes-linter",
        levels[verbose],
        printout=printout
    )

    # Version display mode only
    if version_mode:
        click.echo("html-classes-linter {}".format(__version__))
    # Other modes
    else:
        if not basepath:
            logger.critical("Argument 'basepath' is required.")
            raise click.Abort()

        logger.info("basepath: {}".format(basepath))
        logger.info("verbosity: {}".format(levels[verbose]))
        logger.info("mode: {}".format(mode))

    cleaner = HtmlAttributeCleaner()

    if mode == "lint":
        raise NotImplementedError()
    elif mode == "diff":
        print()
        print("📂 Opening base directory:", basepath)
        print("🔧 Using pattern:", cleaner.file_search_pattern)
        print("🔧 With starting lint tag:", cleaner.lint_tag)
        print()
    elif mode == "reformat":
        raise NotImplementedError()

    # TODO: Use accurate method following mode option
    cleaner.diff(basepath)

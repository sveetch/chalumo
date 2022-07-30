"""
Main entrance to commandline actions

Since Click use function docstring to build its help content, no command
function are documented.
"""
from pathlib import Path

import click

from .. import __pkgname__, __version__
from ..logger import init_logger
from ..diff import SourceDiff


# Available logging levels
APP_LOGGER_CONF = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
    None
)


@click.command()
@click.argument(
    "basepath",
    type=click.Path(
        file_okay=True, dir_okay=True, writable=True, resolve_path=False,
        path_type=Path, exists=True,
    ),
    required=False,
)
@click.option(
    "--mode",
    metavar="STRING",
    type=click.Choice(["lint", "diff", "reformat"]),
    show_default=True,
    help=(
        "Operation mode to perform. "
        "'lint' will just perform parsing and return problems. "
        "'diff' will output of diff changes for every files with lint issues. "
        "'reformat' will rewrite sources to fix lint issues."
    ),
    default="diff"
)
@click.option(
    "--require-pragma",
    metavar="STRING",
    show_default=True,
    help=(
        "Only the files starting with this exact string will be processed and others "
        "ones will be ignored. For compatibility with 'djLint' environment you should "
        "use '{# djlint:on #}'."
    ),
    default=""
)
@click.option(
    "--profile",
    metavar="STRING",
    type=click.Choice(["html", "django"]),
    show_default=True,
    help=(
        "Template profile to use to parse and lint sources. "
        "'html' (default) won't do anything special since HTML is the basic format. "
        "'django' enable Django template processors for a workaround with template "
        "tags. "
    ),
    default="html"
)
@click.option(
    "--pattern",
    metavar="STRING",
    show_default=True,
    help=(
        "Pattern to use for file discovery in given basepath. If given basepath is"
        "a single file path, the pattern is not used."
    ),
    default=""
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
def cli_frontend(basepath, mode, require_pragma, profile, pattern, verbose,
                 version_mode):
    """
    Diff, lint or reformat files for messy 'class' attribute contents from a given
    basepath. The basepath argument may be a directory to recursively search or a
    single file path.
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
        __pkgname__,
        levels[verbose],
        printout=printout
    )

    # Version display mode only
    if version_mode:
        click.echo("{} {}".format(
            __pkgname__,
            __version__
        ))
        return

    # Other modes
    else:
        if not basepath:
            logger.critical("Argument 'basepath' is required.")
            raise click.Abort()

        if mode == "lint":
            raise NotImplementedError()
        elif mode == "diff":
            cleaner = SourceDiff(
                pragma_tag=require_pragma,
                compatibility=profile
            )
        elif mode == "reformat":
            raise NotImplementedError()

        # TODO: Use accurate method following mode option
        if basepath.is_file():
            logger.info("📂 Opening single file: {}".format(basepath))
        else:
            logger.info("📂 Opening base directory: {}".format(basepath))
        logger.info("🔧 Using pattern: {}".format(cleaner.file_search_pattern))
        logger.info("🔧 Profile: {}".format(profile))
        if cleaner.pragma_tag:
            logger.info("🔧 Required pragma tag: {}".format(cleaner.pragma_tag))

        cleaner.run(basepath)

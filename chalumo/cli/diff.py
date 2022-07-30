# -*- coding: utf-8 -*-
import logging
from pathlib import Path

import click

from .. import __pkgname__, __version__
from ..logger import init_logger
from ..diff import SourceDiff


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
@click.pass_context
def diff_command(context, basepath, require_pragma, profile, pattern):
    """
    Apply rules fixes on discovered files then output a diff between original and fixed
    sources.

    The basepath argument may be a directory to recursively search or a single file
    path.
    """
    logger = logging.getLogger("chalumo")

    if not basepath:
        logger.critical("Argument 'basepath' is required.")
        raise click.Abort()

    cleaner = SourceDiff(
        pragma_tag=require_pragma,
        compatibility=profile
    )

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

# -*- coding: utf-8 -*-
import logging

import click

from ..reformat import SourceWriter

from .base import COMMON_ARGS, COMMON_OPTIONS


@click.command()
@click.argument("basepath", **COMMON_ARGS["basepath"]["kwargs"])
@click.option(
    *COMMON_OPTIONS["profile"]["args"],
    **COMMON_OPTIONS["profile"]["kwargs"]
)
@click.option(
    *COMMON_OPTIONS["require-pragma"]["args"],
    **COMMON_OPTIONS["require-pragma"]["kwargs"]
)
@click.option(
    *COMMON_OPTIONS["pattern"]["args"],
    **COMMON_OPTIONS["pattern"]["kwargs"]
)
@click.pass_context
def reformat_command(context, basepath, profile, require_pragma, pattern):
    """
    Rewrite sources with applied rules fixes on discovered files.

    The basepath argument may be a directory to recursively search or a single file
    path.
    """
    logger = logging.getLogger("chalumo")

    cleaner = SourceWriter(
        pragma_tag=require_pragma,
        compatibility=profile,
        file_search_pattern=pattern,
    )

    if basepath.is_file():
        logger.info("📂 Opening single file: {}".format(basepath))
    else:
        logger.info("📂 Opening base directory: {}".format(basepath))

    logger.info("🔧 Using pattern: {}".format(cleaner.file_search_pattern))

    logger.info("🔧 Profile: {}".format(profile))

    if cleaner.pragma_tag:
        logger.info("🔧 Required pragma tag: {}".format(cleaner.pragma_tag))

    cleaner.run(basepath)

# -*- coding: utf-8 -*-
import click

from .. import __version__


@click.command()
@click.pass_context
def version_command(context):
    """
    Print out version information.
    """
    click.echo("chalumo {}".format(__version__))

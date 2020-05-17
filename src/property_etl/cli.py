import click

from . import tcad

cli = click.Group()
cli.add_command(tcad.cli)

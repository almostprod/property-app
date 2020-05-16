import click

from . import tcad

cli = click.CommandCollection(sources=[tcad.cli])

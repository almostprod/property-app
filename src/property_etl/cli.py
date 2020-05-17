import click

from .config import get_config


from . import tcad


config = get_config()

cli = click.Group(name="property-etl")
config.init_app(cli)

cli.add_command(tcad.cli)

import click

from .config import get_config


from . import tcad
from . import openaddresses
from . import parcel


config = get_config()

cli = click.Group(name="property-etl")
config.init_app(cli)

cli.add_command(tcad.cli)
cli.add_command(openaddresses.cli)
cli.add_command(parcel.cli)

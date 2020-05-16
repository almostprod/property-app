import click

cli = click.Group()


@cli.command("tcad")
@click.option(
    "--export-type",
    default="db",
    type=click.Choice(["db", "jsonl"], case_sensitive=False),
)
def convert_access(export_type):
    """Convert TCAD access db to Postgres"""
    import pyodbc

    print([x for x in pyodbc.drivers() if x.startswith("Microsoft Access Driver")])

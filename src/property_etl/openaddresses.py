import io
import zipfile
import logging

import click
import numpy as np
import pandas as pd

from .config import get_config
from .database import get_db


config = get_config()

log = logging.getLogger("tcad")

cli = click.Group(name="openaddresses", help="openaddresses.io ETL")


def _normalize_csv_schema_columns(columns):
    return [col.strip().lower() for col in columns]


@cli.command("db")
@click.option("--table", type=str, required=True)
def export_to_db(table):
    load_csv_to_db(table)


def load_csv_to_db(
    table_name,
    filename=None,
    data_path="data/openaddresses",
    county="travis",
    chunksize=config.CSV_LOAD_CHUNKSIZE,
    schema="open_address",
):
    import pathlib
    import sqlalchemy as sa
    from rich.console import Console
    from rich.progress import track

    console = Console()

    if not filename:
        filename = f"{county}.zip"

    data_zip_path = pathlib.Path(data_path) / pathlib.Path(filename)

    db = get_db(schema=schema)

    with zipfile.ZipFile(data_zip_path, "r") as data_file, db as transaction:

        table = transaction.get_table(table_name.lower())

        table.delete()

        for csv_file in track(
            [f for f in data_file.namelist() if f.endswith(".csv")],
            description=f"Loading {table_name}...",
        ):
            with data_file.open(csv_file, "r") as table_csv:
                csv_io = io.TextIOWrapper(table_csv)

                for address_data in pd.read_csv(csv_io, dtype=str, chunksize=chunksize):
                    address_data.fillna("", inplace=True)

                    address_data.drop(columns=["ID"], inplace=True)
                    address_data.columns = [
                        col.strip().lower() for col in address_data.columns
                    ]

                    col_types = {
                        "hash": sa.Text,
                        "lat": sa.Float,
                        "lon": sa.Float,
                        "city": sa.Text,
                        "unit": sa.Text,
                        "number": sa.Text,
                        "region": sa.Text,
                        "street": sa.Text,
                        "district": sa.Text,
                        "postcode": sa.Text,
                    }

                    table.insert_many(
                        address_data.to_dict("records"), ensure=True, types=col_types,
                    )

                    transaction.commit()

    console.print(f"Load of {table_name} table complete! :tada:", emoji=True)


def _yield_rows(address_data, address_index):
    for index, values in address_data.iterrows():
        row = address_index.loc[index, :].to_dict()
        row["data"] = values.to_dict()
        yield row

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

cli = click.Group(name="tcad", help="TCAD ETL Helpers")


def _normalize_csv_schema_columns(columns):
    return [col.strip().lower() for col in columns]


@cli.command("json")
@click.option("--table", type=str, required=True)
@click.option("--out", type=str, default="data/out")
def convert_to_json(table, out):
    """Convert .mdb table export to json"""
    from rich.console import Console

    console = Console()

    table_schema_df = pd.read_csv(f"data/schema/{table}.csv", index_col=False)
    table_schema_df.columns = _normalize_csv_schema_columns(table_schema_df.columns)

    table_schema = table_schema_df.set_index("column_name")
    table_schema = table_schema[~table_schema.index.isin(["filler"])]

    def _column_type_map(column_type):
        column_type = column_type.strip()

        if column_type.startswith("char"):
            return str

        if column_type.startswith("int"):
            return int

        if column_type.startswith("numeric"):
            return str

        return str

    table_schema["column_type"] = table_schema["column_type"].map(_column_type_map)

    json_schema = table_schema[~table_schema.index.isin(["filler"])].to_dict(
        orient="index"
    )

    col_names = []
    col_spec = []
    dtypes = {}

    for col_name, spec in json_schema.items():
        col_names.append(col_name)
        col_spec.append((spec["offset_start"] - 1, spec["offset_end"]))

        dtypes[col_name] = spec["column_type"]

    tcad_data = pd.read_fwf(
        f"data/tcad/{table}.txt",
        names=col_names,
        colspecs=col_spec,
        dtype=dtypes,
        chunksize=config.CSV_LOAD_CHUNKSIZE,
        index_col=["prop_id", "prop_val_yr", "py_owner_id", "sup_num"],
    )

    export_archive = f"{out}/{table}.zip"
    with zipfile.ZipFile(export_archive, "w") as property_file:
        total_row_count = 0
        for idx, df in enumerate(tcad_data):

            json_filename = f"{table}.{idx}.json"
            with property_file.open(json_filename, "w") as property_json:
                row_count = df.shape[0]
                console.print(
                    f"Total Exported: {total_row_count} rows Current File: {json_filename}",  # noqa
                    end="\r",  # noqa
                )
                console.print("", end="\r")

                json_io = io.TextIOWrapper(property_json)
                df.to_json(json_io, orient="table")

                total_row_count += row_count

        console.print(
            f":white_check_mark: Exported: {total_row_count} rows", emoji=True
        )

        console.print(
            f"Export of {table} to {export_archive} complete! :tada:", emoji=True
        )


@cli.command("load_json")
@click.option("--table", type=str, required=True)
def load_json(table):
    """
    Import db table to db
    """
    from rich import print

    load_json_to_db(table)

    print(f"{table} import complete! :tada:")


def load_json_to_db(
    table_name,
    filename=None,
    data_path="data/out",
    chunksize=config.CSV_LOAD_CHUNKSIZE,
    schema="tcad",
):
    import pathlib
    import sqlalchemy as sa
    from rich.console import Console
    from rich.progress import track

    console = Console()

    if not filename:
        filename = f"{table_name}.zip"

    data_zip_path = pathlib.Path(data_path) / pathlib.Path(filename)

    db = get_db(schema=schema)

    with zipfile.ZipFile(data_zip_path, "r") as data_file, db as transaction:

        table = transaction.get_table(table_name.lower())

        table.delete()

        for json_file in track(
            [f for f in data_file.namelist() if f.endswith(".json")],
            description=f"Loading {table_name}...",
        ):
            with data_file.open(json_file, "r") as table_json:
                json_io = io.TextIOWrapper(table_json)

                tcad_data = pd.read_json(json_io, orient="table")
                tcad_index = tcad_data.index.to_frame()

                col_types = {}

                for col, dtype in tcad_index.dtypes.to_dict().items():
                    col_types[col] = sa.Text
                    if dtype == np.int64:
                        col_types[col] = sa.BigInteger

                col_types["data"] = sa.dialects.postgresql.JSONB

                table.insert_many(
                    list(_yield_rows(tcad_data, tcad_index)),
                    ensure=True,
                    types=col_types,
                )

    console.print(f"Load of {table_name} table complete! :tada:", emoji=True)


def _yield_rows(tcad_data, tcad_index):
    for index, values in tcad_data.iterrows():
        row = tcad_index.loc[index, :].to_dict()
        row["data"] = values.to_dict()
        yield row

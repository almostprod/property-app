import io
import subprocess
import zipfile

import click
import numpy as np
import pandas as pd

from tqdm.contrib import tenumerate

from .database import get_db


CSV_EXCLUDE_COLS = ["filler"]
CSV_LOAD_CHUNKSIZE = 1000

cli = click.Group(name="tcad", help="TCAD ETL Helpers")


@cli.command("csv")
@click.option("--table", type=str)
@click.option("--out", type=str, default="data/out")
def convert_to_csv(table, out):
    """Convert .mdb table export to csv"""

    table_schema = pd.read_csv(f"data/schema/{table}.csv", index_col=False)
    table_schema.columns = [col.strip() for col in table_schema.columns]

    tcad_data = pd.read_fwf(
        f"data/tcad/{table}.txt",
        widths=table_schema["length"].values,
        dtype=str,
        chunksize=CSV_LOAD_CHUNKSIZE,
    )

    cols = table_schema["column_name"].to_numpy()

    exluded_cols = []
    for col in CSV_EXCLUDE_COLS:
        exluded_cols.append(np.where(cols == col))

    filter_indexes = np.concatenate(exluded_cols, axis=None)

    with zipfile.ZipFile(f"{out}/{table}.zip", "w") as property_file:
        with property_file.open(f"{table}.csv", "w") as property_csv:
            csv_io = io.TextIOWrapper(property_csv)
            for idx, df in tenumerate(tcad_data):
                skip_header = idx != 0
                df.drop(df.columns[filter_indexes], axis=1, inplace=True)
                df.to_csv(
                    csv_io,
                    index=False,
                    header=skip_header
                    or [col for col in cols if col not in CSV_EXCLUDE_COLS],
                    encoding="utf-8",
                )


@cli.command("init_db")
@click.option("--mdb_file", type=str, default="data/tcad/TCAD_Roll.mdb")
@click.option("--out", type=str, default="data/out")
def init_db(mdb_file, out):
    """
    Inititialize db to .mdb schema
    """

    init_db_schema(mdb_file)


def list_tables(rdb_file):
    """
    :param rdb_file: The mdb file.
    :return: A list of the tables in a given database.
    """
    tables = subprocess.check_output(["mdb-tables", "-t", "table", rdb_file]).decode(
        "utf8"
    )
    return tables.strip().split(" ")


def export_mdb_schema(rdb_file, db="postgres"):
    """
    :param rdb_file: The MS Access mdb database file.
    :param db: Database SQL dialect to use for the schema definition.
    """
    output = subprocess.check_output(
        ["mdb-schema", "--no-indexes", "--no-relations", rdb_file, db]
    )

    create_schema_definition = output.decode(encoding="utf8")

    return create_schema_definition.replace(
        "CREATE TABLE", "CREATE TABLE IF NOT EXISTS"
    )


def init_db_schema(rdb_file):
    schema_definition = export_mdb_schema(rdb_file)
    schema_tables = list_tables(rdb_file)

    dataset = get_db(schema="tcad")

    with dataset as transaction:
        conn = transaction.executable()
        conn.execute(schema_definition)

    return schema_tables

# Borrowed a lot of this logic from
# https://github.com/jbn/pandas_access/blob/master/pandas_access/__init__.py

import re
import io
import subprocess
import zipfile
import itertools

import click
import numpy as np
import pandas as pd

from tqdm.contrib import tenumerate


TABLE_RE = re.compile(r"CREATE TABLE \[(\w+)\]\s+\((.*?\));", re.MULTILINE | re.DOTALL)
DEF_RE = re.compile(r"\s*\[(\w+)\]\s*(.*?),")
TEXT_RE = re.compile(r".*\((\d+)\)\s*")

CSV_EXCLUDE_COLS = ["filler"]
CSV_LOAD_CHUNKSIZE = 1000

cli = click.Group()


@cli.command("tcad")
@click.option("--table", type=str)
@click.option("--out", type=str, default="data/out")
def convert_access(table, out):
    """Convert TCAD access db to csv"""

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


def list_tables(rdb_file, encoding="latin-1"):
    """
    :param rdb_file: The MS Access database file.
    :param encoding: The content encoding of the output. I assume `latin-1`
        because so many of MS files have that encoding. But, MDBTools may
        actually be UTF-8.
    :return: A list of the tables in a given database.
    """
    tables = subprocess.check_output(["mdb-tables", rdb_file]).decode(encoding)
    return tables.strip().split(" ")


def _extract_defs(defs_str):
    defs = []
    current_col_start = 0
    current_col_end = 0
    lines = defs_str.splitlines()
    for line in lines:
        m = DEF_RE.match(line)
        if m:
            col_name = m.group(1)
            data_type_str = m.group(2).lower()
            num_chars = None

            data_type = str

            if data_type_str.startswith("integer"):
                data_type = str
                num_chars = 5

            elif data_type_str.startswith("long"):
                data_type = np.int
                num_chars = 12

            elif data_type_str.startswith("datetime"):
                data_type = str
                # 2020 / 05 / 20
                num_chars = 25

            elif data_type_str.startswith("memo"):
                data_type = str
                num_chars = 500

            else:
                bytes_match = TEXT_RE.match(data_type_str)
                if bytes_match:
                    num_bytes = bytes_match.group(1)
                    num_chars = int(num_bytes) // 2

            try:
                current_col_end = current_col_start + num_chars
            except Exception:
                raise ValueError(data_type_str)
            defs.append(
                (col_name, data_type_str, (current_col_start, current_col_end),)
            )
            current_col_start = current_col_end

    return defs


def read_schema(rdb_file, encoding="utf8"):
    """
    :param rdb_file: The MS Access database file.
    :param encoding: The schema encoding. I'm almost positive that MDBTools
        spits out UTF-8, exclusively.
    :return: a dictionary of table -> column -> access_data_type
    """
    output = subprocess.check_output(["mdb-schema", rdb_file])
    lines = output.decode(encoding).splitlines()
    schema_ddl = "\n".join(
        l for l in lines if l and not l.startswith("-")  # noqa: E741
    )

    schema = {}
    for table, defs in TABLE_RE.findall(schema_ddl):
        schema[table] = _extract_defs(defs)

    return schema

import dataset

import sqlalchemy as sa

from .config import get_config

config = get_config()


def get_db(schema=None):
    db_uri = config.DATABASE_URI

    db = dataset.connect(
        str(db_uri), schema=schema, engine_kwargs={"use_batch_mode": True}
    )
    db.query(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    return db


def upsert(table_name, row_ident, items, schema="public"):
    db = get_db(schema=schema)

    table = db.get_table(table_name)
    new_rows = [{row_ident: item[row_ident], "payload": item} for item in items]
    table.upsert_many(
        new_rows,
        keys=[row_ident],
        ensure=True,
        types={"payload": sa.dialects.postgresql.JSONB},
    )

    return new_rows

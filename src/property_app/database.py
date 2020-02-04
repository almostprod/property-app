from typing import Callable, List, Optional

import sqlalchemy as sa
from flask_sqlalchemy import SignallingSession, SQLAlchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB, insert
from sqlalchemy_utils import generic_repr, get_columns

meta = sa.MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


class AppSQLAlchemy(SQLAlchemy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session: SignallingSession = self.session

    def apply_driver_hacks(self, app, info, options):
        options["use_batch_mode"] = app.config["SQLALCHEMY_BATCH_MODE"]
        super().apply_driver_hacks(app, info, options)


db = AppSQLAlchemy(metadata=meta, session_options={"autoflush": False})


class ToDictMixin:
    __to_dict_ignore__ = ("id", "created_at", "updated_at")

    def to_dict(self, ignore_list=None):
        if ignore_list is None:
            ignore_list = self.__to_dict_ignore__

        columns = get_columns(self).keys()
        results = {column: getattr(self, column) for column in columns if column not in ignore_list}

        return results


@generic_repr
class AppBase(db.Model, ToDictMixin):
    __abstract__ = True

    id = sa.Column(sa.BigInteger, primary_key=True)

    created_at = sa.Column(sa.DateTime, server_default=sa.text("(now() at time zone 'utc')"))
    updated_at = sa.Column(sa.DateTime, server_default=sa.text("(now() at time zone 'utc')"))

    deleted_at = sa.Column(sa.DateTime)

    _extra = sa.Column(JSONB(none_as_null=True))

    @classmethod
    def upsert(
        cls,
        map_func: Callable,
        query_func: Optional[Callable] = None,
        index_elements: Optional[List] = None,
        unique_constraint: Optional[str] = None,
        **kwargs,
    ):
        if not index_elements:
            index_elements = [cls.id]

        item = map_func(kwargs, cls())

        values = item.to_dict()

        stmt = postgresql.insert(cls).values(**values)
        if index_elements:
            stmt = stmt.on_conflict_do_update(index_elements=index_elements, set_=values)
        elif unique_constraint:
            stmt = stmt.on_conflict_do_update(constraint=unique_constraint, set_=values)

        db.session.execute(stmt)

        return cls.query.filter(query_func(item)).first()


class CSVImportMixin:
    """Adds from_csv to a SQLAlchemy model class."""

    __tablename__ = None
    __upsert_keys__ = ("id",)

    @classmethod
    def _columns(cls):
        _columns = get_columns(cls)
        return [c for c in _columns]

    @classmethod
    def _csv_mapping(cls):
        return dict(((c.info["csv_column"], c.name) for c in cls._columns() if "csv_column" in c.info))

    @classmethod
    def from_csv(cls, filename, constraint=None, chunksize=None, null_mapper=None, session=None):
        import pandas as pd

        if null_mapper is None:
            null_mapper = dict()

        def handle_null(item):
            k, v = item
            if v is not None:
                return item

            return k, null_mapper.get(k)

        csv_data = pd.read_csv(filename)
        csv_data.rename(lambda c: cls._csv_mapping()[c.lower()], axis="columns", inplace=True)

        def upsert(_, engine, keys, data_iter):

            stmt = insert(cls.__table__, bind=engine)
            on_conflict = {"set_": {k: getattr(stmt.excluded, k) for k in iter(keys)}}
            if constraint:
                on_conflict["constraint"] = constraint
            else:
                on_conflict["index_elements"] = cls.__upsert_keys__

            stmt = stmt.on_conflict_do_update(**on_conflict)

            def rows():
                for row in data_iter:
                    yield dict(map(handle_null, zip(keys, row)))

            engine.execute(stmt.values(list(rows())))

        csv_data.to_sql(
            cls.__tablename__,
            if_exists="append",
            index=False,
            method=upsert,
            con=db.session.get_bind() if session is None else session,
            chunksize=chunksize,
        )

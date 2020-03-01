from datetime import datetime
import typing as t

import sqlalchemy as sa

from sqlalchemy.event import listens_for
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import as_declarative

from sqlalchemy_mixins import ActiveRecordMixin, ReprMixin, SmartQueryMixin
from sqlalchemy_utils.listeners import force_auto_coercion, force_instant_defaults


from .types import JSON, PendulumType

from .metadata import app_metadata


@as_declarative(metadata=app_metadata)
class AppBase(ActiveRecordMixin, ReprMixin, SmartQueryMixin):
    __abstract__ = True
    __to_dict_ignore__ = ("id", "created_at", "updated_at")

    id = sa.Column(sa.BigInteger, primary_key=True)

    created_at = sa.Column(
        PendulumType, server_default=sa.text("(now() at time zone 'utc')")
    )
    updated_at = sa.Column(
        PendulumType, server_default=sa.text("(now() at time zone 'utc')")
    )

    deleted_at = sa.Column(sa.DateTime)

    _extra = sa.Column("extra", JSON)

    @classmethod
    def upsert(
        cls,
        map_func: t.Callable,
        query_func: t.Callable = None,
        index_elements: t.Optional[t.List] = None,
        unique_constraint: t.Optional[str] = None,
        **kwargs,
    ):
        if not index_elements:
            index_elements = [cls.id]

        item = map_func(kwargs, cls())  # noqa

        values = item.to_dict()

        stmt = postgresql.insert(cls).values(**values)
        if index_elements:
            stmt = stmt.on_conflict_do_update(
                index_elements=index_elements, set_=values
            )
        elif unique_constraint:
            stmt = stmt.on_conflict_do_update(constraint=unique_constraint, set_=values)

        cls.session.execute(stmt)

        if query_func is None:
            query_func = lambda i: i  # noqa

        return cls.query.filter(query_func(item)).first()  # noqa

    def to_dict(self, ignore_cols: t.Optional[t.Sequence] = None):
        if ignore_cols is None:
            ignore_cols = ("id", "created_at", "updated_at")

        results = {
            column: getattr(self, column)
            for column in self.columns
            if column not in ignore_cols
        }

        return results


@listens_for(AppBase, "before_update", propagate=True)
def _receive_before_update(_mapper, _connection, target):
    target.updated_at = datetime.utcnow()


force_auto_coercion()
force_instant_defaults()

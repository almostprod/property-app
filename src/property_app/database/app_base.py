from datetime import datetime
from typing import Callable, List, Optional

import sqlalchemy as sa

from sqlalchemy.event import listens_for
from sqlalchemy.dialects import postgresql

from sqlalchemy_mixins import ActiveRecordMixin, ReprMixin, SmartQueryMixin
from sqlalchemy_utils.listeners import force_auto_coercion, force_instant_defaults


from .base import Base
from .types import JSON, PendulumType


class AppBase(Base, ActiveRecordMixin, ReprMixin, SmartQueryMixin):
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
        map_func: Callable,
        query_func: Optional[Callable] = None,
        index_elements: Optional[List] = None,
        unique_constraint: Optional[str] = None,
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

        return cls.query.filter(query_func(item)).first()  # noqa

    def to_dict(self, ignore_list=None):
        if ignore_list is None:
            ignore_list = self.__to_dict_ignore__

        results = {
            column: getattr(self, column)
            for column in self.columns
            if column not in ignore_list
        }

        return results


@listens_for(AppBase, "before_update", propagate=True)
def _receive_before_update(_mapper, _connection, target):
    target.updated_at = datetime.utcnow()


force_auto_coercion()
force_instant_defaults()

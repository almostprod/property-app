import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base

meta = sa.MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

default_session_options = {
    "autocommit": False,
    "autoflush": False,
}


def create_engine(data_base_uri):
    return sa.create_engine(data_base_uri, pool_pre_ping=True, use_batch_mode=True)


def create_session(engine=None, session_options=None) -> orm.scoped_session:
    if engine is None:
        engine = create_engine("")
    if session_options is None:
        session_options = dict()

    return orm.scoped_session(orm.sessionmaker(bind=engine, **session_options))


Base = declarative_base(metadata=meta)

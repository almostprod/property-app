import sqlalchemy as sa
from sqlalchemy import orm

from property_app.config import get_config
from property_app.middleware import get_request_id

app_metadata = sa.MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

_session_options = {
    "autocommit": False,
    "autoflush": False,
}

app_config = get_config()

engine = sa.create_engine(
    str(app_config.DATABASE_URI), pool_pre_ping=True, use_batch_mode=True
)
Session = orm.scoped_session(
    orm.sessionmaker(bind=engine, **_session_options), scopefunc=get_request_id
)

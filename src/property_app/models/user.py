import sqlalchemy as sa

from property_app.database import AppBase


class User(AppBase):
    __tablename__ = "user"

    username = sa.Column(sa.Text)
    password = sa.Column(sa.Text)

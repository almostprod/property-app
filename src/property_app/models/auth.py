import enum

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_utils import EmailType

from property_app.database import AppBase
from property_app.database.types import Enum


@enum.unique
class AppAuthCredentialType(enum.Enum):
    PASSWORD = "password"


class AppUser(AppBase):
    __tablename__ = "app_user"

    username = sa.Column(sa.Text, nullable=False)

    first_name = sa.Column(sa.Text, nullable=False, default="")
    last_name = sa.Column(sa.Text, nullable=False, default="")

    display_name = sa.Column(sa.Text)


class AppUserEmail(AppBase):
    __tablename__ = "app_user_email"

    user_id = sa.Column(
        sa.BigInteger, sa.ForeignKey("app_user.id"), index=True, nullable=False
    )
    user = orm.relationship(
        "AppUser",
        foreign_keys=[user_id],
        backref=orm.backref("user_emails", lazy="joined"),
        uselist=False,
    )

    email = sa.Column(EmailType, nullable=False)
    is_primary = sa.Column(sa.Boolean, nullable=False, default=True)


class AppAuthAccount(AppBase):
    __tablename__ = "app_auth_account"

    user_id = sa.Column(
        sa.BigInteger, sa.ForeignKey("app_user.id"), index=True, nullable=False
    )
    user = orm.relationship(
        "AppUser",
        foreign_keys=[user_id],
        backref=orm.backref("auth_accounts", lazy="joined"),
        uselist=False,
    )

    account_key = sa.Column(sa.Text, nullable=False, index=True)


class AppAuthCredential(AppBase):
    __tablename__ = "app_auth_credential"

    auth_account_id = sa.Column(
        sa.BigInteger, sa.ForeignKey("app_auth_account.id"), index=True, nullable=False
    )
    auth_account = orm.relationship(
        "AppAuthAccount",
        foreign_keys=[auth_account_id],
        backref=orm.backref("auth_credentials", lazy="joined"),
        uselist=False,
    )

    type = sa.Column(Enum(AppAuthCredentialType), nullable=False)

    credential = sa.Column(sa.Text, nullable=False)

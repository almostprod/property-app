import enum

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import EmailType

from property_app.database.app_base import AppBase
from property_app.database.types import Enum


@enum.unique
class AppAuthCredentialType(enum.Enum):
    PASSWORD = "password"


class AppUser(AppBase):
    __tablename__ = "app_user"

    display_name = sa.Column(sa.Text)

    @hybrid_property
    def scopes(self):
        if "auth_scopes" not in self._extra:
            return []

        return self._extra["auth_scopes"]

    @scopes.expression  # type: ignore
    def scopes(cls):
        return cls._extra["auth_scopes"]

    @scopes.setter  # type: ignore
    def scopes(self, value):
        if not self._extra or not self._extra["auth_scopes"]:
            self._extra = {}
            self._extra["auth_scopes"] = []

        self._extra["auth_scopes"] = value
        orm.attributes.flag_modified(self, "_extra")

    emails = orm.relationship("AppUserEmail", lazy="joined")

    credentials = orm.relationship("AppUserCredential")

    primary_email = orm.relationship(
        "AppUserEmail",
        uselist=False,
        viewonly=True,
        primaryjoin="and_(AppUser.id == AppUserEmail.user_id, AppUserEmail.is_primary.is_(True))",  # noqa: E501
    )

    @property
    def email(self):
        if not self.primary_email:
            return None

        return self.primary_email.email

    @property
    def name(self):
        if self.display_name:
            return self.display_name

        return self.email

    @property
    def is_authenticated(self):
        return True


class AppUserCredential(AppBase):
    __tablename__ = "app_user_credential"

    user_id = sa.Column(
        sa.BigInteger, sa.ForeignKey("app_user.id"), index=True, nullable=False
    )
    user = orm.relationship(
        "AppUser", foreign_keys=[user_id], uselist=True, back_populates="credentials"
    )

    credential_type = sa.Column(
        Enum(AppAuthCredentialType),
        nullable=False,
        default=AppAuthCredentialType.PASSWORD.value,
    )
    credential = sa.Column(sa.Text, nullable=False)


class AppUserEmail(AppBase):
    __tablename__ = "app_user_email"

    user_id = sa.Column(
        sa.BigInteger, sa.ForeignKey("app_user.id"), index=True, nullable=False
    )
    user = orm.relationship(
        "AppUser", foreign_keys=[user_id], uselist=False, back_populates="emails"
    )

    email = sa.Column(EmailType, nullable=False)
    is_primary = sa.Column(sa.Boolean, nullable=False, default=True)

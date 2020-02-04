import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_utils import EmailType

from property_app.database import AppBase, db
from flask_login import UserMixin


class AppUser(AppBase, UserMixin):
    __tablename__ = "app_user"

    email = sa.Column(EmailType)

    name = sa.Column(sa.UnicodeText)

    first_name = sa.Column(sa.UnicodeText)
    last_name = sa.Column(sa.UnicodeText)

    @staticmethod
    def query_by_email(email):
        return AppUser.query.filter(AppUser.email == email)

    @staticmethod
    def query_by_user_id(user_id):
        return AppUser.query.filter(AppUser.id == user_id)

    @staticmethod
    def query_by_slack_token_id(token_id):
        return AppUser.query.join(AppUserSlack, AppUser.id == AppUserSlack.app_user_id).filter(
            AppUserSlack.token_id == token_id
        )

    @classmethod
    def create_from_slack(cls, token):
        user = AppUser(email=token["user"]["email"], name=token["user"]["name"])
        slack = AppUserSlack(
            app_user=user, team_id=token["team"]["id"], token_id=token["user"]["id"], token_playload=token
        )

        db.session.add(user)
        db.session.add(slack)

        return user


class AppUserSlack(AppBase):
    __tablename__ = "app_user_slack"

    app_user_id = sa.Column(sa.ForeignKey("app_user.id"), index=True, nullable=False)
    app_user = orm.relationship(
        "AppUser", foreign_keys=[app_user_id], backref=orm.backref("slack", lazy="joined", uselist=False)
    )

    team_id = sa.Column(sa.UnicodeText, nullable=False)
    token_id = sa.Column(sa.UnicodeText, nullable=False)

    token_playload = sa.Column(JSONB(none_as_null=True))

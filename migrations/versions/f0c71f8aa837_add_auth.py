"""add_auth

Revision ID: f0c71f8aa837
Revises:
Create Date: 2020-03-01 12:30:20.717593

"""
from alembic import op
import sqlalchemy as sa

import sqlalchemy_utils

import property_app


revision = "f0c71f8aa837"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "app_user",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            property_app.database.types.PendulumType(timezone=True),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            property_app.database.types.PendulumType(timezone=True),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=True,
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("extra", property_app.database.types.JSON(none_as_null=True, astext_type=sa.Text()), nullable=True),
        sa.Column("username", sa.Text(), nullable=False),
        sa.Column("first_name", sa.Text(), nullable=False),
        sa.Column("last_name", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_user")),
    )

    op.create_table(
        "app_auth_account",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            property_app.database.types.PendulumType(timezone=True),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            property_app.database.types.PendulumType(timezone=True),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=True,
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("extra", property_app.database.types.JSON(none_as_null=True, astext_type=sa.Text()), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("account_key", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], name=op.f("fk_app_auth_account_user_id_app_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_auth_account")),
    )

    op.create_index(op.f("ix_app_auth_account_account_key"), "app_auth_account", ["account_key"], unique=False)
    op.create_index(op.f("ix_app_auth_account_user_id"), "app_auth_account", ["user_id"], unique=False)

    op.create_table(
        "app_user_email",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            property_app.database.types.PendulumType(timezone=True),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            property_app.database.types.PendulumType(timezone=True),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=True,
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("extra", property_app.database.types.JSON(none_as_null=True, astext_type=sa.Text()), nullable=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("email", sqlalchemy_utils.types.email.EmailType(length=255), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["app_user.id"], name=op.f("fk_app_user_email_user_id_app_user")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_user_email")),
    )

    op.create_index(op.f("ix_app_user_email_user_id"), "app_user_email", ["user_id"], unique=False)

    op.create_table(
        "app_auth_credential",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            property_app.database.types.PendulumType(timezone=True),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            property_app.database.types.PendulumType(timezone=True),
            server_default=sa.text("(now() at time zone 'utc')"),
            nullable=True,
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("extra", property_app.database.types.JSON(none_as_null=True, astext_type=sa.Text()), nullable=True),
        sa.Column("auth_account_id", sa.BigInteger(), nullable=False),
        sa.Column("type", property_app.database.types.Enum("PASSWORD"), nullable=False),
        sa.Column("credential", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["auth_account_id"],
            ["app_auth_account.id"],
            name=op.f("fk_app_auth_credential_auth_account_id_app_auth_account"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_auth_credential")),
    )

    op.create_index(
        op.f("ix_app_auth_credential_auth_account_id"), "app_auth_credential", ["auth_account_id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_app_auth_credential_auth_account_id"), table_name="app_auth_credential")
    op.drop_table("app_auth_credential")
    op.drop_index(op.f("ix_app_user_email_user_id"), table_name="app_user_email")
    op.drop_table("app_user_email")
    op.drop_index(op.f("ix_app_auth_account_user_id"), table_name="app_auth_account")
    op.drop_index(op.f("ix_app_auth_account_account_key"), table_name="app_auth_account")
    op.drop_table("app_auth_account")
    op.drop_table("app_user")

"""add_auth

Revision ID: 9f066f062d8e
Revises:
Create Date: 2020-05-13 23:09:05.067810

"""
import property_app
import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy import Text

revision = "9f066f062d8e"
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
        sa.Column(
            "extra",
            property_app.database.types.JSON(none_as_null=True, astext_type=Text()),
            nullable=True,
        ),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_user")),
    )

    op.create_table(
        "app_user_credential",
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
        sa.Column(
            "extra",
            property_app.database.types.JSON(none_as_null=True, astext_type=Text()),
            nullable=True,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "credential_type",
            property_app.database.types.Enum("PASSWORD"),
            nullable=False,
        ),
        sa.Column("credential", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["app_user.id"],
            name=op.f("fk_app_user_credential_user_id_app_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_user_credential")),
    )

    op.create_index(
        op.f("ix_app_user_credential_user_id"),
        "app_user_credential",
        ["user_id"],
        unique=False,
    )

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
        sa.Column(
            "extra",
            property_app.database.types.JSON(none_as_null=True, astext_type=Text()),
            nullable=True,
        ),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "email", sqlalchemy_utils.types.email.EmailType(length=255), nullable=False
        ),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["app_user.id"],
            name=op.f("fk_app_user_email_user_id_app_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_user_email")),
    )

    op.create_index(
        op.f("ix_app_user_email_user_id"), "app_user_email", ["user_id"], unique=False
    )


def downgrade():
    pass

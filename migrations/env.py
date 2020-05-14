import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from property_app.config import get_config

config = context.config

fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")


def exclude_schemas_from_config(config_):
    schemas_ = config_.get("schemas", None)
    schemas = []
    if schemas_ is not None:
        schemas = schemas_.split(",")
    return schemas


def exclude_tables_from_config(config_):
    tables_ = config_.get("tables", None)
    tables = []
    if tables_ is not None:
        tables = tables_.split(",")
    return tables


def exclude_foreign_keys_from_config(config_):
    fkeys_ = config_.get("foreign_keys", None)
    fkeys = []
    if fkeys_ is not None:
        fkeys = fkeys_.split(",")
    return fkeys


def exclude_indexes_from_config(config_):
    indexes_ = config_.get("indexes", None)
    indexes = []
    if indexes_ is not None:
        indexes = indexes_.split(",")
    return indexes


exclude_tables = exclude_tables_from_config(config.get_section("alembic:exclude"))
exclude_schemas = exclude_schemas_from_config(config.get_section("alembic:exclude"))
exclude_fkeys = exclude_foreign_keys_from_config(config.get_section("alembic:exclude"))
exclude_indexes = exclude_indexes_from_config(config.get_section("alembic:exclude"))


def include_object(object_, name, type_, _reflected, _compare_to):
    skip = object_.info.get("skip_autogenerate", False)
    if (
        type_ == "table"
        and (name in exclude_tables or object_.schema in exclude_schemas)
    ) or skip:
        return False
    elif type_ == "foreign_key_constraint" and name in exclude_fkeys:
        return False
    elif type_ == "index" and name in exclude_indexes:
        return False
    else:
        return True


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    from property_app.database.app_base import AppBase

    def process_revision_directives(_context, _revision, directives):
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info("No changes in schema detected.")

    app_config = get_config()
    config.set_main_option("sqlalchemy.url", str(app_config.DATABASE_URI))

    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    import warnings
    from sqlalchemy import exc as sa_exc

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=sa_exc.SAWarning,
            message="Skipped unsupported reflection of expression-based index*.",
        )

        connection = engine.connect()
        context.configure(
            connection=connection,
            target_metadata=AppBase.metadata,
            process_revision_directives=process_revision_directives,
            include_object=include_object,
            include_schemas=True,  # Added so alembic introspects all schemas on autogenerate.
        )

        try:
            with context.begin_transaction():
                context.run_migrations()
        except Exception as exception:
            logger.error(exception)
            raise exception
        finally:
            connection.close()


if context.is_offline_mode():
    raise NotImplementedError("Offline migrations are not supported.")
else:
    run_migrations_online()

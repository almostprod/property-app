import os

from invoke import task  # type: ignore
from dotenv import load_dotenv

load_dotenv()

env = os.environ


@task
def test(c):
    c.run("pytest", pty=True)


@task
def black(c):
    c.run("poetry run black .", pty=True)


@task
def type_check(c):
    c.run("poetry run mypy src/", pty=True)


@task(help={"message": "Description of the new migration."})
def db_migrate(c, message="replace this message"):
    """
    Create a new alembic migration.
    """
    c.run(f"poetry run alembic revision --autogenerate -m '{message}'", pty=True)


@task(help={"target": "Target alembic revision."})
def db_upgrade(c, target="head"):
    """
    Upgrade the db to the target alembic revision.
    """
    c.run(f"poetry run alembic upgrade {target}", pty=True)


@task
def dev_services(c):
    c.run("docker network create property-app-net || true", hide=True)
    c.run("docker-compose -f docker-compose.yml up -d", pty=True)
    c.run("pg_isready")


@task(dev_services)
def dev_app(c):
    c.run("poetry run property")


@task
def dev_client(c):
    c.run("cd src/property_client && yarn dev", pty=True)


@task
def pg_web(c):
    c.run(
        "pgweb --url=${DATABASE_URI} --listen=8081 --bind=0.0.0.0 --prefix=pgweb",
        env=env,
        pty=True,
    )

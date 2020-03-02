from invoke import task  # type: ignore


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
def dev(c):
    c.run("docker network create property-app-net || true", hide=True)
    c.run("yarn nf start --showenvs redis=0,db=1,web=1,proxy=1", pty=True)


@task
def pg_web(c):
    c.run("yarn nf start --showenvs pgweb=1", pty=True)

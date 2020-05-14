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
    c.run(
        f"poetry run alembic revision --autogenerate -m '{message}'", pty=True, env=env
    )


@task(help={"target": "Target alembic revision."})
def db_upgrade(c, target="head"):
    """
    Upgrade the db to the target alembic revision.
    """
    c.run(f"poetry run alembic upgrade {target}", pty=True, env=env)


@task
def dev_services(c):
    c.run("docker network create property-app-net || true", hide=True)
    c.run("docker-compose -f docker-compose.yml up -d", pty=True, env=env)
    c.run("pg_isready", env=env)


@task(dev_services)
def dev_app(c):
    c.run("poetry run property")


@task
def dev_client(c):
    c.run("yarn dev", pty=True)


@task
def pg_web(c):
    c.run(
        "pgweb --url=${DATABASE_URI} --listen=8081 --bind=0.0.0.0 --prefix=pgweb",
        env=env,
        pty=True,
    )


@task
def ssl_gen(c):
    certbot_opts = [
        "--manual",
        "--config-dir nginx/.letsencrypt/",
        "--work-dir nginx/.letsencrypt/work/",
        "--logs-dir nginx/.letsencrypt/logs/",
        "--preferred-challenges dns",
        "-m ssl@almostproductive.com",
        "--agree-tos",
        "-d *.local.almostproductive.com",
    ]

    c.run(f'certbot certonly {" ".join(certbot_opts)}')
    c.run("cp -r nginx/.letsencrypt/live/* nginx/")


@task
def ssl_renew(c):
    certbot_opts = [
        "--config-dir nginx/.letsencrypt/",
        "--work-dir nginx/.letsencrypt/work/",
        "--logs-dir nginx/.letsencrypt/logs/",
    ]

    c.run(f'certbot renew {" ".join(certbot_opts)}')
    c.run("cp nginx/.letsencrypt/live/**/*.pem nginx/")

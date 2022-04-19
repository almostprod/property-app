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
    c.run("black .", pty=True)


@task(help={"message": "Description of the new migration."})
def db_migrate(c, message="replace this message"):
    """
    Create a new alembic migration.
    """
    c.run(
        f"alembic revision --autogenerate -m '{message}'", pty=True, env=env
    )


@task(help={"target": "Target alembic revision."})
def db_upgrade(c, target="head"):
    """
    Upgrade the db to the target alembic revision.
    """
    c.run(f"alembic upgrade {target}", pty=True, env=env)


@task
def dev_services(c):
    c.run("docker network create property-app-net || true", hide=True)
    c.run("docker-compose -f docker-compose.yml up -d", pty=True, env=env)
    c.run("pg_isready", env=env)


@task(dev_services)
def dev_app(c):
    c.run("property", env=env, pty=True)


@task(dev_services)
def dev_shell(c):
    c.run("ipython", env=env, pty=True)


@task
def dev_client(c):
    c.run("npm run dev", pty=True)


@task
def dbt_run(c):
    c.run("dbt run --profiles-dir ./profiles", pty=True, env=env)


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

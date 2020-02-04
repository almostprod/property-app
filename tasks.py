import pathlib
from io import StringIO

from fabric import Connection
from invoke import task
from patchwork import files

AWS_PROFILE = "property-dev"
AWS_ACCOUNT_ID = "663370156182"
AWS_DATABASE_SECRET = "a-secret"
FLASK_DEV_PORT = 5000

APP_REPO = "prod-property-app"
PROXY_REPO = "prod-property-app-proxy"
AWS_ECR_BASE = f"{AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com"

PROD_HOST = "property.almostproductive.com"
APP_DIR = "/opt/property-app"
APP_SSH_KEY = "~/.ssh/property-app.pem"

NGROK_SUBDOMAIN = "property-app"
LOCAL_DEV_HOST = "property-local.almostproductive.com"


def ssh(host=PROD_HOST) -> Connection:
    return Connection(
        host=host,
        user="ubuntu",
        inline_ssh_env=True,
        connect_kwargs={"key_filename": [pathlib.Path(APP_SSH_KEY).expanduser().as_posix()]},
    )


def app_dir(conn, app_dir=APP_DIR):
    return conn.cd(app_dir)


def ensure_app_env(conn, remote_app_dir=APP_DIR, user="ubuntu"):
    files.directory(conn, remote_app_dir, user=user, sudo=True)
    conn.put(pathlib.Path("deploy/docker-compose.yml"), remote=remote_app_dir)
    docker_login_cmd = conn.run("aws --region us-east-1 ecr get-login --no-include-email", hide="stdout")
    conn.run(docker_login_cmd.stdout, hide="stderr")


def run_compose(conn, cmd, env=None):
    if env is None:
        env = {
            "PROXY_REPO": f"{AWS_ECR_BASE}/{PROXY_REPO}",
            "APP_REPO": f"{AWS_ECR_BASE}/{APP_REPO}",
            "LOG_MODE": "json",
            "LOG_LEVEL": "INFO",
            "APP_LOG_LEVEL": "INFO",
            "FLASK_APP": "property_app",
            "FLASK_ENV": "production",
            "DATABASE_SECRET": AWS_DATABASE_SECRET,
        }

    env_file = StringIO()

    for pair in env.items():
        env_file.write("=".join(pair))
        env_file.write("\n")

    env_file.seek(0)

    pwd = conn.run("pwd", hide="stdout").stdout.strip()
    env_path = f"{pwd}/.env"
    conn.put(env_file, env_path)

    conn.run(f"docker-compose {cmd}", pty=True)


@task
def docker_restart(c):
    with ssh(host=PROD_HOST) as prod:
        ensure_app_env(prod)
        with app_dir(prod):
            run_compose(prod, "restart")


@task
def docker_stop(c):
    with ssh(host=PROD_HOST) as prod:
        ensure_app_env(prod)
        with app_dir(prod):
            run_compose(prod, "down -v --remove-orphans")


@task
def status(c):
    with ssh(host=PROD_HOST) as prod:
        with app_dir(prod):
            run_compose(prod, "ps")


@task
def logs(c):
    with ssh(host=PROD_HOST) as prod:
        with app_dir(prod):
            run_compose(prod, "logs --tail=100 --follow")


@task
def test(c):
    c.run("docker-compose run --rm tests bash -c 'tox -e test'", pty=True)


@task
def app_shell(c):
    c.run("docker-compose run --rm app bash -c 'flask shell'", pty=True)


@task
def shell(c):
    with ssh(host=PROD_HOST) as prod:
        with app_dir(prod):
            prod.run("/bin/bash", pty=True)


@task
def ecr_login(c):
    login_result = c.run(f"aws --profile {AWS_PROFILE} ecr get-login --no-include-email", hide="stdout")
    if login_result:
        login_command = login_result.stdout
        c.run(login_command)


@task(ecr_login)
def docker_build(c):
    repos = {"PROXY_REPO": f"{AWS_ECR_BASE}/{PROXY_REPO}", "APP_REPO": f"{AWS_ECR_BASE}/{APP_REPO}"}
    base_cmd = "docker-compose -f docker-compose.yml -f docker-compose.build.yml"

    c.run(f"{base_cmd} build proxy app", env=repos)
    c.run(f"{base_cmd} push proxy app", env=repos)


@task
def docker_deploy(c):
    with ssh(host=PROD_HOST) as prod:
        ensure_app_env(prod)
        with app_dir(prod):
            run_compose(prod, "pull")
            run_compose(prod, "run --rm app /opt/venv/bin/flask db upgrade")
            run_compose(prod, "up -d --remove-orphans")
            prod.run("docker system prune -af")


@task
def docker_data(c):
    with ssh(host=PROD_HOST) as prod:
        ensure_app_env(prod)
        with app_dir(prod):
            run_compose(prod, "run --rm app /opt/venv/bin/flask data import_odb")


@task
def ngrok(c):
    c.run(f"ngrok http -subdomain={NGROK_SUBDOMAIN} https://{LOCAL_DEV_HOST}", pty=True)


@task
def format(c):  # noqa
    c.run("black .")


@task
def ssl_gen(c):
    certbot_opts = [
        "--manual",
        "--config-dir nginx/.letsencrypt/",
        "--work-dir nginx/.letsencrypt/work/",
        "--logs-dir nginx/.letsencrypt/logs/",
        "--preferred-challenges dns",
        "-m ssl@property.almostproductive.com",
        "--agree-tos",
        "-d almostproductive.com,*.almostproductive.com",
    ]

    c.run(f'certbot certonly {" ".join(certbot_opts)}')
    c.run("cp nginx/.letsencrypt/live/* nginx/")


@task
def ssl_renew(c):
    certbot_opts = [
        "--config-dir nginx/.letsencrypt/",
        "--work-dir nginx/.letsencrypt/work/",
        "--logs-dir nginx/.letsencrypt/logs/",
    ]

    c.run(f'certbot renew {" ".join(certbot_opts)}')
    c.run("cp nginx/.letsencrypt/live/**/*.pem nginx/")

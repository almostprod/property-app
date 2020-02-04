from flask.cli import AppGroup


data_cli = AppGroup("data", help="Perform data ops.")


def init_cli(app):
    app.cli.add_command(data_cli)

#!/usr/bin/env bash
pip install poetry
poetry install --no-dev 

poetry run alembic upgrade head

#!/usr/bin/env bash
pip install poetry
yarn build
poetry install --no-dev 

poetry run alembic upgrade head

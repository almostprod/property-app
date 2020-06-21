#!/usr/bin/env bash
pip install poetry
yarn install
yarn build
poetry install --no-dev 

poetry run alembic upgrade head

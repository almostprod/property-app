# Property Search

Beginings of a new app to sketch out how to structure a project based in Starlette and refine my understanding of ASGI. Currently this is mostly boilerplate but has:

- working alembic
- working sqlalchemy
- examples of custom ASGI middleware
- Basic integration with Intertia.js via `lib/inertia.py`

## To Fix

This is based on another project of mine based on flask so there may still be some random flask references that break things or haven't been updated yet.

- gunicorn config doesn't work yet. still setup for flask with gthread
- update to JWT-based session https://github.com/aogier/starlette-authlib
- replace dummy authentication with `passlib`
- add error tracking in production https://docs.sentry.io/platforms/python/asgi/

## Setup and Run Dev

```shell script
$ poetry install
$ poetry shell
$ inv dev-app
```

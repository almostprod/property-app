# Property Search

Beginings of a new app to sketch out how to structure a project based in Starlette and refine my understanding of ASGI. Currently this is mostly boilerplate but has:

- working alembic
- working sqlalchemy
- integration with structlog using contextvars
- example of a blueprint-like structure using a `Router` object.
- examples of custom ASGI middleware
- gunicorn config doesn't work yet. still setup for flask with gthread

## Setup and Run Dev
```shell script
$ poetry install
$ poetry shell
$ inv dev
```

This is based on another project of mine based on flask so there may still be some random flask references that break things or haven't been updated yet.

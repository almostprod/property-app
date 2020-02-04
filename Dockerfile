FROM lambci/lambda:build-python3.7 AS base

ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN mkdir -p /opt/venv \
    && mkdir -p /app/requirements \
    && python3 -m venv /opt/venv \
    && python3 -m venv /opt/tools

ENV PATH=/opt/venv/bin:/opt/tools/bin:${PATH}

ARG CONSTRAINTS="all.txt"
ARG APP_REQUIREMENTS_ENV="prod"

ADD ./requirements/ /app/requirements/

RUN cd /app \
    && /opt/tools/bin/pip install --no-cache-dir -c ./requirements/${CONSTRAINTS} -r ./requirements/tools.in

FROM base AS app

ARG CONSTRAINTS="all.txt"
ARG APP_REQUIREMENTS_ENV="prod"

RUN cd /app \
    && pip install --no-cache-dir -c ./requirements/${CONSTRAINTS} -r ./requirements/${APP_REQUIREMENTS_ENV}.in

ADD ./ /app/

RUN cd /app \
    && pip install -e .

EXPOSE 5000
WORKDIR /app

CMD ["bash"]

FROM base AS tests

ADD ./ /app/

RUN cd /app \
    && git init \
    && pre-commit install-hooks \
    && rm -rf .git

EXPOSE 5000
WORKDIR /app

CMD ["bash"]

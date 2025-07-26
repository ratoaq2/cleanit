FROM python:3.13-slim as builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=0

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY poetry.lock pyproject.toml README.md /app/
RUN poetry install --no-interaction --no-ansi --only main
COPY cleanit/ /app/cleanit/
RUN poetry build --no-interaction --no-ansi


FROM python:3.13-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

COPY --from=builder /app/dist /usr/src/dist

RUN pip install /usr/src/dist/cleanit-*.tar.gz

WORKDIR /

ENTRYPOINT ["cleanit"]
CMD ["--help"]

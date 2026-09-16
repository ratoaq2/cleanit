FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_NO_CACHE=1 \
    UV_LOCKED=1

WORKDIR /app
COPY uv.lock pyproject.toml README.md /app/
RUN uv sync --no-install-project --no-dev
COPY cleanit/ /app/cleanit/
RUN uv build


FROM python:3.14-slim

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

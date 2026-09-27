#!/bin/bash

set -ex

uv run ruff check .
uv run ruff format --check .
uv run mypy cleanit
uv run pytest --verbose --cov=cleanit --cov-report=term-missing --cov-report=xml tests/

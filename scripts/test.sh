#!/bin/bash

set -ex

uv run pytest --verbose --cov=cleanit --cov-report=term-missing --cov-report=xml tests/

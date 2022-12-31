#!/bin/bash

set -ex

flake8
pytest --verbose --cov=cleanit --cov-report=term-missing --cov-report=xml tests/
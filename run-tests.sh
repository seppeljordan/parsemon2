#!/usr/bin/env sh

set -e

isort parsemon/ tests/ -c
black --check .
flake8
mypy parsemon --ignore-missing-imports
pytest \
    --cov=parsemon/ \
    --cov-report=term \
    --cov-report=html \
    --benchmark-skip

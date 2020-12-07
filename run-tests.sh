#!/usr/bin/env sh

set -e

mypy parsemon --ignore-missing-imports
flake8
pytest \
    --cov=parsemon/ \
    --cov-report=term \
    --cov-report=html \
    --benchmark-skip
isort parsemon/ tests/ -c

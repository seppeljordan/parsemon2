#!/usr/bin/env sh

set -e

mypy src/ --ignore-missing-imports
flake8 src/ tests/
PYTHONPATH=src/:$PYTHONPATH pytest \
          --cov=src \
          --cov-report=term \
          --cov-report=html \
          --benchmark-skip
isort -rc src/ tests/ -c

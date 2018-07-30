#!/usr/bin/env sh

set -e

mypy src/
PYTHONPATH=src/:$PYTHONPATH pytest \
          --cov=src \
          --cov-report=term \
          --cov-report=html
flake8 src/

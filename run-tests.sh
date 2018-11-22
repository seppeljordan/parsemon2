#!/usr/bin/env sh

set -e

mypy src/ --ignore-missing-imports
PYTHONPATH=src/:$PYTHONPATH pytest \
          --cov=src \
          --cov-report=term \
          --cov-report=html \
          --benchmark-skip

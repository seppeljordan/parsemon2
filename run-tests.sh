#!/usr/bin/env sh

set -e

mypy src/
PYTHONPATH=src/:$PYTHONPATH pytest
flake8 src/

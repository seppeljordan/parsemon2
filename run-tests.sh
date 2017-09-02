#!/usr/bin/env sh

mypy src/
PYTHONPATH=src/:$PYTHONPATH pytest

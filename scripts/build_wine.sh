#!/usr/bin/env bash
cd /src
wine python -m pip install -e .
wine python -m pip install ".[dev]"
wine pyinstaller migrate.spec
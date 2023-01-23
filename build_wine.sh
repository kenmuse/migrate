#!/usr/bin/env bash
cd /src
wine pip install .
wine pip install .[dev]
wine pyinstaller migrate.spec
#!/usr/bin/env bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/usr/local/lib64
export PATH=$PATH:$HOME/.local/bin
python -m pip install -e .
python -m pip install ".[dev]"
pyinstaller migrate.spec
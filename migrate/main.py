"""
Main entrypoint
"""
import sys
from pathlib import Path
import click

# PEP 366 - Specify __package__ when running a module as a script
if __package__ is None:
    DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(DIR.parent))
    __package__ = DIR.name

from .common.options import CONTEXT_SETTINGS
from .handlers import repo, org, enterprise


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    """Provides support for migrating GitHub resources programmatically"""


cli.add_command(org)
cli.add_command(repo)
cli.add_command(enterprise)

if __name__ == "__main__":
    cli()

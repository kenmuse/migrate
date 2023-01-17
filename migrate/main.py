"""
Main entrypoint
"""

import click
from common.options import CONTEXT_SETTINGS
from handlers import repo, org


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Provides support for migrating GitHub resources programmatically"""


cli.add_command(org)
cli.add_command(repo)

if __name__ == "__main__":
    cli()

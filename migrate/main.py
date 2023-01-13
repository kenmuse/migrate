"""
Main entrypoint
"""

import click
from common.options import CONTEXT_SETTINGS
from handlers.repos import repos
from handlers.orgs import orgs


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Provides support for migrating GitHub resources programmatically"""


cli.add_command(orgs)
cli.add_command(repos)

if __name__ == "__main__":
    cli()

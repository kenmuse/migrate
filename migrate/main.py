"""
Main entrypoint
"""

import click
from common.options import CONTEXT_SETTINGS
from handlers import repo, org
from handlers.enterprise.enterprise import enterprise


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Provides support for migrating GitHub resources programmatically"""


cli.add_command(org)
cli.add_command(repo)
cli.add_command(enterprise)

if __name__ == "__main__":
    cli()

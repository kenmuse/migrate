"""
Secrets command implementation
"""

import click

from common.options import (
    CONTEXT_SETTINGS,
)
from .secrets import repo_secrets
from .settings import repo_settings


@click.group(context_settings=CONTEXT_SETTINGS)
def repo():
    """Provides commands for migrating repository resources"""


repo.add_command(repo_secrets)
repo.add_command(repo_settings)

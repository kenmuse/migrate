"""
Secrets command implementation
"""

import sys

import click
from ...common.api import create_client
from ...common.options import (
    CONTEXT_SETTINGS,
    TargetState,
    pass_targetstate,
    target_options,
)
from ...common.repos import set_repo_secret
from yaml import dump, load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group("secrets", context_settings=CONTEXT_SETTINGS)
def repo_secrets():
    """Repository secrets"""


@repo_secrets.command("load", no_args_is_help=True)
@click.argument("repo", required=True)
@click.option(
    "--settings",
    required=False,
    type=click.File("r"),
    default=sys.stdin,
    help="YAML file containing the secrets. If not provided, stdin is used.",
)
@target_options
@pass_targetstate
def load_secrets(ctx: TargetState, repo: str, settings: click.File):
    """Loads secrets from a YAML file provided as an argument or from stdin

    REPO: The name of the repository
    """
    config = load(settings.read(), Loader=Loader)
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    for name, value in config.items():
        click.echo(
            set_repo_secret(client=api, org=ctx.org, repo=repo, name=name, value=value)
        )

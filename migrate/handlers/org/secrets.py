"""
Org secrets command implementation
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
from ...common.orgs import OrgSecretVisibility, list_org_secrets, set_org_secret
from yaml import dump, load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group("secrets", context_settings=CONTEXT_SETTINGS)
def org_secrets():
    """Organization secrets"""


@org_secrets.command("list", no_args_is_help=True)
@target_options
@pass_targetstate
def list_secrets(ctx: TargetState):
    """Lists the organization secrets"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(list_org_secrets(api, ctx.org))


@org_secrets.command("set", no_args_is_help=True)
@click.argument("name", required=True)
@click.argument("value", required=True)
@target_options
@pass_targetstate
def set_secret(ctx: TargetState, name: str, value: str):
    """Creates a secret for an organization

    NAME: The name of the secret
    VALUE: The value of the secret
    """
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(set_org_secret(api, ctx.org, name, value, OrgSecretVisibility.ALL))


@org_secrets.command("load", no_args_is_help=True)
@click.argument("file", required=False, type=click.File("r"), default=sys.stdin)
@target_options
@pass_targetstate
def load_secrets(ctx: TargetState, file: click.File):
    """Loads secrets from a YAML file provided as an argument or from stdin

    FILE: YAML file containing the secrets. If not provided, stdin is used.
    """
    config = load(file.read(), Loader=Loader)
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    for name, value in config.items():
        click.echo(
            set_org_secret(api, ctx.org, name.upper(), value, OrgSecretVisibility.ALL)
        )

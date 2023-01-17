"""
Org settings command implementation
"""

import sys

import click
from common.api import create_client
from common.options import CONTEXT_SETTINGS, TargetState, pass_targetstate, target_options
from common.orgs import get_org_settings
from yaml import dump, load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group("settings", context_settings=CONTEXT_SETTINGS)
def org_settings():
    """Organization settings"""


@org_settings.command("list", no_args_is_help=True)
@click.option(
    "-f",
    "--output",
    type=click.File("w"),
    default=sys.stdout,
    help="Output file. If not provided, stdout is used.",
)
@click.option(
    "--compact",
    "-r",
    help="Use compact output when reporting to stdout (default: False)",
    is_flag=True,
    flag_value=True,
    default=False,
    required=False,
)
@target_options
@pass_targetstate
def list_settings(ctx: TargetState, output: click.File, compact: bool):
    """Lists the organization settings"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    settings = get_org_settings(client=api, org=ctx.org)
    if sys.stdout.isatty() and compact:
        click.echo(settings)
    else:
        dump(settings.to_dict(), output)

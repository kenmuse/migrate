"""
Org settings command implementation
"""

import sys

import click
from ...common.api import create_client
from ...common.options import (
    CONTEXT_SETTINGS,
    MigrationState,
    TargetState,
    migration_options,
    pass_migrationstate,
    pass_targetstate,
    target_options,
)
from ...common.orgs import get_org_settings, set_org_settings
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


@org_settings.command("copy", no_args_is_help=True)
@click.option(
    "-ghas",
    "--include-ghas",
    is_flag=True,
    help="Include GitHub Advanced Security settings (default:False)",
    default=False,
    flag_value=True,
    required=False,
)
@migration_options
@pass_migrationstate
def copy_settings(ctx: MigrationState):
    """Copies the settings from one organization to another"""
    src_client = create_client(hostname=ctx.src_hostname, token=ctx.src_token)
    dest_client = create_client(hostname=ctx.dest_hostname, token=ctx.dest_token)
    src_settings = get_org_settings(src_client, ctx.src_org)
    set_org_settings(dest_client, ctx.dest_org, src_settings)


@org_settings.command("load", no_args_is_help=True)
@click.option(
    "-f",
    "--settings",
    required=False,
    type=click.File("r"),
    default=sys.stdin,
    help="YAML file containing the settings. If not provided, stdin is used.",
)
@target_options
@pass_targetstate
def load_settings(ctx: TargetState, settings: click.File):
    """Updates the organization settings from a provided file"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    config = load(settings.read(), Loader=Loader)
    old_settings = get_org_settings(client=api, org=ctx.org)

    new_settings = old_settings.update(config)
    if new_settings != old_settings:
        new_settings = set_org_settings(client=api, org=ctx.org, settings=new_settings)

    click.echo(new_settings)

"""
Orgs command implementation
"""

import sys
import click
from common.options import (
    CONTEXT_SETTINGS,
    target_options,
    TargetState,
    pass_targetstate,
)
from common.api import create_client
from common.orgs import (
    list_org_secrets,
    set_org_secret,
    get_org_ip_allow_list,
    create_org_ip_allow_list_entry,
    delete_org_ip_allow_list_entry,
    get_org_settings,
    get_org_actions_permissions,
    set_org_actions_permissions,
    get_org_permissions_allowed_actions,
    OrgSecretVisibility,
)
from yaml import load, dump

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group(context_settings=CONTEXT_SETTINGS)
def orgs():
    """Provides commands for migrating organization resources"""


@orgs.command("show-secrets", no_args_is_help=True)
@target_options
@pass_targetstate
def show_secrets(ctx: TargetState):
    """Lists the organization secrets"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(list_org_secrets(api, ctx.org))


@orgs.command("set-secret", no_args_is_help=True)
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


@orgs.command("load-secrets", no_args_is_help=True)
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


@orgs.command("get-ipallow", no_args_is_help=True)
@target_options
@pass_targetstate
def get_ipallow(ctx: TargetState):
    """Lists the organization IP allow list"""
    result = get_org_ip_allow_list(endpoint=ctx.hostname, token=ctx.token, org=ctx.org)
    click.echo(result)


@orgs.command("delete-ipallow", no_args_is_help=True)
@click.argument("entry_id", required=True)
@target_options
@pass_targetstate
def delete_ipallow(ctx: TargetState, entry_id: str):
    """Deletes the organization IP allow list entry

    ENTRY_ID: The ID of the entry to delete
    """
    result = delete_org_ip_allow_list_entry(
        endpoint=ctx.hostname, token=ctx.token, entry_id=entry_id
    )
    click.echo(result)


@orgs.command("create-ipallow", no_args_is_help=True)
@click.option(
    "-ip", "--ip_address", required=True, help="IP address to allow (CIDR notation)"
)
@click.option(
    "--inactive",
    flag_value=True,
    default=False,
    help="Indicates whether the entry is active",
)
@click.option("-n", "--name", required=True, help="Name of the entry")
@target_options
@pass_targetstate
def create_ipallow(ctx: TargetState, ip_address: str, name: str, inactive: bool = False):
    """Creates an organization IP allow list entry"""
    result = create_org_ip_allow_list_entry(
        endpoint=ctx.hostname,
        token=ctx.token,
        org=ctx.org,
        ip_address=ip_address,
        name=name,
        is_active=not inactive,
    )
    click.echo(result)


@orgs.command("show-settings", no_args_is_help=True)
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
def show_settings(ctx: TargetState, output: click.File, compact: bool):
    """Lists the organization settings"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    settings = get_org_settings(client=api, org=ctx.org)
    if sys.stdout.isatty() and compact:
        click.echo(settings)
    else:
        dump(settings.to_dict(), output)


@orgs.command("show-actions-permissions", no_args_is_help=True)
@target_options
@pass_targetstate
def show_actions_permissions(ctx: TargetState):
    """Gets the organization actions permissions"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(get_org_actions_permissions(api, ctx.org))


@orgs.command("set-actions-permissions", no_args_is_help=True)
@click.option(
    "--allowed_repositories",
    "-r",
    type=click.Choice(["all", "selected", "none"]),
    help="Configures the allowed repositories",
)
@click.option(
    "--allowed_actions",
    "-a",
    type=click.Choice(["all", "selected", "local_only"]),
    help="Configures the allowed actions",
)
@target_options
@pass_targetstate
def show_actions_permissions(
    ctx: TargetState, allowed_repositories: str, allowed_actions: str
):
    """Gets the organization actions permissions"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(
        set_org_actions_permissions(
            client=api,
            org=ctx.org,
            allowed_repositories=allowed_repositories,
            allowed_actions=allowed_actions,
        )
    )


@orgs.command("show-actions-allowed", no_args_is_help=True)
@target_options
@pass_targetstate
def show_actions_allowed(ctx: TargetState):
    """Lists the organization allowed actions"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(get_org_permissions_allowed_actions(api, ctx.org))

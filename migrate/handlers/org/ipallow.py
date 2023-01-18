"""
Org IP-Allow command implementation
"""

import click
from ...common.api import create_client
from ...common.options import (
    CONTEXT_SETTINGS,
    TargetState,
    pass_targetstate,
    target_options,
)
from ...common.orgs import (
    create_org_ip_allow_list_entry,
    delete_org_ip_allow_list_entry,
    get_org_ip_allow_list,
)


@click.group("ipallow", context_settings=CONTEXT_SETTINGS)
def org_ipallow():
    """Organization allow lists"""


@org_ipallow.command("list", no_args_is_help=True)
@target_options
@pass_targetstate
def list_ipallow(ctx: TargetState):
    """Lists the organization IP allow list"""
    result = get_org_ip_allow_list(endpoint=ctx.hostname, token=ctx.token, org=ctx.org)
    click.echo(result)


@org_ipallow.command("delete", no_args_is_help=True)
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


@org_ipallow.command("create", no_args_is_help=True)
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

"""
Orgs actions command implementation
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
    OrgSecretVisibility,
    get_org_actions_permissions,
    get_org_permissions_allowed_actions,
    set_org_actions_permissions,
)


@click.group("actions", context_settings=CONTEXT_SETTINGS)
def org_actions():
    """Organization actions permissions"""


@org_actions.command("list", no_args_is_help=True)
@target_options
@pass_targetstate
def list_actions_permissions(ctx: TargetState):
    """Gets the organization actions permissions"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(get_org_actions_permissions(api, ctx.org))


@org_actions.command("set", no_args_is_help=True)
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
def set_actions_permissions(
    ctx: TargetState, allowed_repositories: str, allowed_actions: str
):
    """Sets the organization actions permissions"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(
        set_org_actions_permissions(
            client=api,
            org=ctx.org,
            allowed_repositories=allowed_repositories,
            allowed_actions=allowed_actions,
        )
    )


@org_actions.command("list-allowed-actions", no_args_is_help=True)
@target_options
@pass_targetstate
def show_actions_allowed(ctx: TargetState):
    """Lists the organization allowed actions"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(get_org_permissions_allowed_actions(api, ctx.org))

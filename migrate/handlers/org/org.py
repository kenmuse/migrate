"""
Orgs command implementation
"""

import sys
import click
import json
from common.options import (
    CONTEXT_SETTINGS,
    target_options,
    TargetState,
    pass_targetstate,
)
from common.api import create_client
from common.orgs import (
    get_org_settings,
    get_org_actions_permissions,
    set_org_actions_permissions,
    get_org_permissions_allowed_actions,
    list_organization_repositories,
    OrgRepoSort,
    OrgRepoType,
    OrgSecretVisibility,
)
from yaml import load, dump
from .secrets import org_secrets
from .ipallow import org_ipallow
from .settings import org_settings
from .actions import org_actions


try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group(context_settings=CONTEXT_SETTINGS)
def org():
    """Provides commands for migrating organization resources"""


@org.command("list", no_args_is_help=True)
@click.option(
    "--sort",
    "-s",
    type=click.Choice(["created", "updated", "pushed", "full_name"]),
    default="created",
)
@click.option(
    "--type",
    "-t",
    type=click.Choice(["all", "public", "private", "forks", "sources", "member"]),
    default="all",
)
@click.option(
    "--output",
    "-f",
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
@click.option(
    "--json/--yaml",
    "-j/-y",
    "is_json",
    help="Determines the output format (default: yaml)",
    is_flag=True,
    flag_value=True,
    default=False,
    required=False,
)
@target_options
@pass_targetstate
def list_repositories(
    ctx: TargetState,
    sort: OrgRepoSort,
    type: OrgRepoType,
    output: click.File,
    compact: bool,
    is_json: bool,
):
    """Lists the organizations"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    repositories = list_organization_repositories(
        client=api, org=ctx.org, sort=sort, type=type
    )
    if sys.stdout.isatty() and compact:
        click.echo(repositories)
    else:
        results = list(map(lambda r: r.to_dict(), repositories))
        if is_json:
            json.dump(results, output, indent=2 if sys.stdout.isatty() else None)
        else:
            dump(results, output)


org.add_command(org_secrets)
org.add_command(org_ipallow)
org.add_command(org_settings)
org.add_command(org_actions)

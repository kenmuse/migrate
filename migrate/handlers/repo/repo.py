"""
Secrets command implementation
"""

import sys
import click
import json
from yaml import dump
from common.options import CONTEXT_SETTINGS, pass_targetstate, target_options, TargetState
from common.api import create_client
from common.orgs import list_organization_repositories, OrgRepoSort, OrgRepoType
from .secrets import repo_secrets
from .settings import repo_settings
from .visibility import repo_visibility


@click.group(context_settings=CONTEXT_SETTINGS)
def repo():
    """Provides commands for migrating repository resources"""


@repo.command("list", no_args_is_help=True)
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
    """Lists the repositories in an organization"""
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


repo.add_command(repo_secrets)
repo.add_command(repo_settings)
repo.add_command(repo_visibility)

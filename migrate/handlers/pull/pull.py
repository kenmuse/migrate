import sys
import click
import json
from yaml import dump
from ...common.types import FastcoreJsonEncoder
from ...common.options import (
    CONTEXT_SETTINGS,
    pass_targetstate,
    target_options,
    TargetState,
)
from ...common.api import create_client
from ...common.pulls import (
    list_pull_requests,
    get_pull_request,
    list_commits_on_pull_request,
)


@click.group(context_settings=CONTEXT_SETTINGS)
def pull():
    """Provides commands for extracting pull request resources"""


@pull.command("list", no_args_is_help=True)
@click.option("--repo", "-r", required=True, help="The repository containing the PRs")
@click.option(
    "--sort",
    "-by",
    type=click.Choice(["created", "updated", "popularity", "long-running"]),
    default="created",
    help="The sort order for the results (default: created)",
)
@click.option(
    "--state",
    "-t",
    type=click.Choice(["open", "closed", "all"]),
    default="all",
    help="The state of the pull requests to return (default: all)",
)
@click.option(
    "--direction",
    "-order",
    type=click.Choice(["asc", "desc"]),
    default=None,
    help="The direction of the sort order (default: None)",
)
@click.option(
    "--output",
    "-f",
    type=click.File("w"),
    default=sys.stdout,
    help="Output file. If not provided, stdout is used.",
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
def list_pulls(
    ctx: TargetState,
    repo: str,
    sort: str,
    state: str,
    direction: str,
    output: click.File,
    is_json: bool,
):
    """Lists the pull requests in a repository"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    response = list_pull_requests(
        client=api, org=ctx.org, repo=repo, sort=sort, state=type, direction=direction
    )

    if is_json:
        json.dump(
            response,
            output,
            cls=FastcoreJsonEncoder,
            indent=2 if sys.stdout.isatty() else None,
        )
    else:
        dump(response, output)

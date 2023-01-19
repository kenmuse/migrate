"""Provides commands for checks resources"""

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
from ...common.checks import (
    list_check_runs_for_commit,
    list_check_suites_for_commit,
    list_check_runs_for_suite,
    get_check_run,
)


@click.group(context_settings=CONTEXT_SETTINGS)
def check():
    """Provides commands for extracting pull request resources"""


@check.command("runs", no_args_is_help=True)
@click.option("--repo", "-r", required=True, help="The repository containing the PRs")
@click.option("--ref", required=True, help="The branch name or SHA")
@click.option(
    "--name",
    "-n",
    help="Filters results to the specified check name",
)
@click.option(
    "--status",
    "-stat",
    type=click.Choice(["queued", "in_progress", "completed"]),
    default=None,
    help="Filters results to the specified check status (default: None)",
)
@click.option(
    "--filter",
    type=click.Choice(["latest", "all"]),
    default="latest",
    help="Filters results to the specified check status (default: latest)",
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
def list_runs(
    ctx: TargetState,
    repo: str,
    ref: str,
    name: str,
    status: str,
    filter: str,
    output: click.File,
    is_json: bool,
):
    """Lists the pull requests in a repository"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    response = list_check_runs_for_commit(
        client=api,
        org=ctx.org,
        repo=repo,
        ref=ref,
        filter=filter,
        name=name,
        status=status,
    )

    if is_json:
        json.dump(
            response,
            output,
            indent=2 if sys.stdout.isatty() else None,
            cls=FastcoreJsonEncoder,
        )
    else:
        dump(list(response), output)

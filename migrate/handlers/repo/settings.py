"""
Repo settings command implementation
"""

import sys

import click
from common.api import create_client
from common.options import (
    CONTEXT_SETTINGS,
    MigrationState,
    TargetState,
    migration_options,
    pass_migrationstate,
    pass_targetstate,
    target_options,
)
from common.repos import get_repo_settings, set_repo_settings
from yaml import dump, load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group("settings", context_settings=CONTEXT_SETTINGS)
def repo_settings():
    """Repository settings"""


@repo_settings.command("list", no_args_is_help=True)
@click.argument("repo")
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
def list_settings(ctx: TargetState, repo: str, output: click.File, compact: bool):
    """Lists the repo settings"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    settings = get_repo_settings(api, ctx.org, repo)
    if sys.stdout.isatty() and compact:
        click.echo(settings)
    else:
        dump(settings.to_dict(), output)


@repo_settings.command("copy", no_args_is_help=True)
@click.option("-sr", "--src", help="The source repository")
@click.option("-dr", "--dest", help="The destination repository")
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
def copy_settings(ctx: MigrationState, src, dest, include_ghas):
    """Copies the settings from one repository to another"""
    src_client = create_client(hostname=ctx.src_hostname, token=ctx.src_token)
    dest_client = create_client(hostname=ctx.dest_hostname, token=ctx.dest_token)
    src_settings = get_repo_settings(src_client, ctx.src_org, src, include_ghas)
    set_repo_settings(dest_client, ctx.dest_org, dest, src_settings)


@repo_settings.command("load", no_args_is_help=True)
@click.argument("repo")
@click.option(
    "-f",
    "--settings",
    required=False,
    type=click.File("r"),
    default=sys.stdin,
    help="YAML file containing the settings. If not provided, stdin is used.",
)
@click.option(
    "-ghas",
    "--include-ghas",
    is_flag=True,
    help="Include GitHub Advanced Security settings",
    default=False,
    required=False,
)
@target_options
@pass_targetstate
def loads_settings(ctx: TargetState, repo: str, settings: click.File, include_ghas: bool):
    """Updates the repo settings from a provided file

    REPO: The name of the repository
    """
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    config = load(settings.read(), Loader=Loader)
    repo_settings = get_repo_settings(
        client=api, org=ctx.org, repo=repo, include_ghas=include_ghas
    )

    settings = repo_settings.update(config)
    if settings != repo_settings:
        if not include_ghas:
            repo_settings.ghas = None
        repo_settings = set_repo_settings(
            client=api, org=ctx.org, repo=repo, settings=settings
        )

    click.echo(settings)

"""
Repo visibility command implementation
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
from common.repos import get_repo_visibility, set_repo_visibility, RepoVisibility
from yaml import dump, load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group("visibility", context_settings=CONTEXT_SETTINGS)
def repo_visibility():
    """Repository visibility"""


@repo_visibility.command("get", no_args_is_help=True)
@click.argument("repo")
@target_options
@pass_targetstate
def get_visibility(
    ctx: TargetState,
    repo: str,
):
    """Gets the repo visibility"""
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    click.echo(get_repo_visibility(api, ctx.org, repo))


@repo_visibility.command("copy", no_args_is_help=True)
@click.option("-sr", "--src", help="The source repository")
@click.option("-dr", "--dest", help="The destination repository")
@migration_options
@pass_migrationstate
def copy_visibility(ctx: MigrationState, src: str, dest: str):
    """Copies the visibility from one repository to another"""
    src_client = create_client(hostname=ctx.src_hostname, token=ctx.src_token)
    dest_client = create_client(hostname=ctx.dest_hostname, token=ctx.dest_token)
    visibility = get_repo_visibility(src_client, ctx.src_org, src)
    set_repo_visibility(dest_client, ctx.dest_org, dest, visibility)


@repo_visibility.command("set", no_args_is_help=True)
@click.argument("repo")
@click.argument("visibility", type=click.Choice(["public", "private", "internal"]))
@target_options
@pass_targetstate
def loads_settings(ctx: TargetState, repo: str, visibility: RepoVisibility):
    """Updates the repo visibility

    REPO: The name of the repository

    VISIBILITY: The visibility of the repository (public, private, internal)
    """
    api = create_client(hostname=ctx.hostname, token=ctx.token)
    set_repo_visibility(api, ctx.org, repo, visibility)

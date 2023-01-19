"""Methods for using the GitHub API for pull requests"""

from copy import copy
from dataclasses import dataclass, fields
from enum import Enum, unique, auto
from ghapi.all import GhApi
from .api import (
    GhPublicKey,
    encrypt_secret,
    paginated,
    rate_limited,
    call_with_exception_handler,
)
from .types import SerializedEnum, DictData, alternative_name


def list_pull_requests(
    client: GhApi,
    org: str,
    repo: str,
    state: str = "open",
    sort="created",
    direction="desc",
):
    """Retrieves the pull requests for the provided repo"""
    result = call_with_exception_handler(
        f"{org}/{repo}",
        client.pulls.list,
        owner=org,
        repo=repo,
        state=state,
        sort=sort,
        direction=direction,
    )
    return result


def get_pull_request(client: GhApi, org: str, repo: str, pr: int):
    """Retrieves the pull request for the provided repo"""
    result = call_with_exception_handler(
        f"{org}/{repo}", client.pulls.get, owner=org, repo=repo, pull_number=pr
    )
    return result


def list_commits_on_pull_request(
    client: GhApi, org: str, repo: str, pr: int, state: str = "open"
):
    """Retrieves the first 250 commits for the provided pull request"""
    result = call_with_exception_handler(
        f"{org}/{repo}",
        paginated,
        client.pulls.list_commits,
        owner=org,
        repo=repo,
        pull_number=pr,
        state=state,
    )
    return result

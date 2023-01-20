"""Methods for using the GitHub API for check runs"""

from copy import copy
from dataclasses import dataclass, fields
from enum import Enum, unique, auto
from ghapi.all import GhApi
from .api import (
    paginated,
    rate_limited,
    call_with_exception_handler,
)
from .types import SerializedEnum, DictData, alternative_name


def list_check_suites_for_commit(
    client: GhApi, org: str, repo: str, commit: str, state: str = "open"
):
    """Retrieves the check suites for the provided commit"""
    result = call_with_exception_handler(
        f"{org}/{repo}",
        paginated,
        client.checks.list_suites_for_ref,
        owner=org,
        repo=repo,
        ref=commit,
        state=state,
    )
    return result


def list_check_runs_for_suite(
    client: GhApi, org: str, repo: str, suite: int, state: str = "open"
):
    """Retrieves the check runs for the provided check suite"""
    result = call_with_exception_handler(
        f"{org}/{repo}",
        paginated,
        client.checks.list_for_suite,
        owner=org,
        repo=repo,
        check_suite_id=suite,
        status=state,
    )
    return result


def get_check_run(client: GhApi, org: str, repo: str, run: int):
    """Retrieves the check run for the provided run id"""
    result = call_with_exception_handler(
        f"{org}/{repo}",
        client.checks.get,
        owner=org,
        repo=repo,
        check_run_id=run,
    )
    return result


def get_check_run_annotations(client: GhApi, org: str, repo: str, run: int):
    """Retrieves the annotations for the provided run id"""
    result = call_with_exception_handler(
        f"{org}/{repo}",
        paginated,
        client.checks.list_annotations,
        owner=org,
        repo=repo,
        check_run_id=run,
    )
    return result


def list_check_runs_for_commit(
    client: GhApi,
    org: str,
    repo: str,
    ref: str,
    name: str = None,
    status: str = None,
    filter: str = None,
):
    """Retrieves the check runs for the provided commit"""
    result = call_with_exception_handler(
        f"{org}/{repo}",
        paginated,
        client.checks.list_for_ref,
        owner=org,
        repo=repo,
        check_name=name,
        ref=ref,
        status=status,
        filter=filter,
    )

    return [
        run
        for resp in result
        if result
        for run in resp["check_runs"]
        if "check_runs" in resp
    ]

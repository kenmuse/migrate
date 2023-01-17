"""
Supports accessing and using the GitHub API
"""

import functools
import json
import os
import re
import requests
import sys
import time
from base64 import b64encode
from dataclasses import dataclass
from enum import unique, auto
from common.types import DictData, SerializedEnum
from fastcore.net import HTTP4xxClientError
from ghapi.all import GhApi, print_summary
from nacl import encoding, public


@unique
class SortDirection(SerializedEnum):
    """Indicates the sort order for an ordered query"""

    ASC = auto()
    DESC = auto()


@dataclass
class GhPublicKey(DictData):
    """Represents a public key"""

    key: str
    id: str  # pylint: disable=invalid-name


# pylint: disable-next=two-few_public-methods
class rate_limited:  # pylint: disable=invalid-name
    """Decorator to implement a throttle for API write calls
    to limit them to one call per second.
    """

    _last_called = 0.0
    _interval = 1.0

    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __call__(self, *args, **kwargs):
        clock_time = rate_limited._get_time()
        if rate_limited._last_called > 0:
            elapsed = clock_time - rate_limited._last_called
            wait_time = rate_limited._interval - elapsed
            if not wait_time <= 0:
                time.sleep(wait_time)
        rate_limited._last_called = rate_limited._get_time()
        return self.func(*args, **kwargs)

    @staticmethod
    def _get_time():
        return time.clock_gettime(time.CLOCK_MONOTONIC)


def _resolve_api_service_endpoint(host: str, ghec_path: str, ghes_path: str):
    """Resolves a RESTful endpoint for a given GitHub environment

    Arguments:
    host: The hostname of the GitHub environment
    ghec_path: The path suffix for the REST API endpoint on GitHub Enterprise Cloud
    ghes_path: The path suffix for the REST API endpoint on GHES/GHAE
    """
    hostname = host.lower() if host is not None else None
    if (
        hostname is None
        or hostname == ""
        or hostname == "github.com"
        or hostname == "api.github.com"
        or hostname == "https://api.github.com"
    ):
        host = "https://api.github.com" + ghec_path
    elif hostname.startswith("https://"):
        host = hostname
    elif hostname.endswith(ghes_path):
        host = f"https://{hostname}"
    else:
        host = f"https://{hostname}" + ghes_path
    return host


def configure_proxy(http: str, https: str, disable_ssl: bool = False):
    from urllib.request import ProxyHandler, build_opener
    import fastcore.net
    import ssl

    if disable_ssl:
        ssl._create_default_https_context = ssl._create_unverified_context
    proxy = ProxyHandler({"http": http, "https": https})
    opener = build_opener(proxy)
    fastcore.net._opener = opener


def get_paged_data(client: GhApi, url: str, per_page=100, page=1):
    """Issues a GET query returning paged date from the REST API"""
    return client(url, "GET", query={"per_page": per_page, "page": page})


def is_ghec(host_or_uri: str):
    return "github.com" in host_or_uri.lower()


def is_ghae(host_or_uri: str):
    return "ghe.com" or "ghaekube.net" in host_or_uri.lower()


def is_ghes(host_or_uri: str):
    return not is_ghec(host_or_uri) and not is_ghae(host_or_uri)


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key"""
    public_key = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def resolve_rest_endpoint(hostname=None):
    """Resolves the REST API endpoint for a given hostname"""
    return _resolve_api_service_endpoint(hostname, "", "/api/v3")


def resolve_graphql_endpoint(hostname=None):
    """Resolves the GraphQL API endpoint for a given hostname"""
    return _resolve_api_service_endpoint(hostname, "/graphql", "/api/graphql")


def call_with_exception_handler(context, func, *args, **kwargs):
    """Calls the provided function and handles any exceptions"""

    def get_message(error: HTTP4xxClientError):
        return re.sub("^.+\r?\n====Error Body====\r?\n", "", error.msg)

    def write_error(status: str, context: str, error: HTTP4xxClientError):
        msg = json.loads(get_message(error))
        print(
            json.dumps(
                dict(code=error.code, status=status, context=context, details=msg),
                indent=2,
            ),
            file=sys.stderr,
        )

    try:
        return func(*args, **kwargs)
    except HTTP4xxClientError as ex:
        match ex.code:
            case 401:
                write_error(status="Bad credentials", context=context, error=ex)
            case 403:
                write_error(status="Forbidden", context=context, error=ex)
            case 404:  # Not found or no permissions
                write_error(status="Not Found", context=ex.url, error=ex)
            case 409:  # Validation or state conflict
                write_error(status="Conflict", context=context, error=ex)
            case 422:  # Validation failed
                write_error(status="Unprocessable Entity", context=context, error=ex)
            case _:
                raise
        sys.exit(1)


def create_client(
    token: str, hostname: str = "api.github.com", enable_debug: bool = False
):
    """Creates a client for API calls to a GitHub system"""

    host = resolve_rest_endpoint(hostname)
    api = GhApi(token=token, gh_host=host)
    if enable_debug or os.getenv("GITHUB_DEBUG"):
        api.debug = print_summary
    return api


def graphql_query(
    query: str,
    token: str,
    endpoint: str = "https://api.github.com",
    variables: dict = None,
):
    """Executes a GraphQL query"""

    headers = {"Authorization": f"Bearer {token}"}
    endpoint_uri = resolve_graphql_endpoint(endpoint)
    response = requests.post(
        endpoint_uri,
        json={"query": query, "variables": variables},
        headers=headers,
    )
    if response.status_code == 200:
        return response.json()
    else:
        data = response.json()
        error = {
            "status": response.status_code,
            "message": data.get("message", "Unknown error"),
        }
        raise SystemExit(error)


def paginated(operation, per_page=100, page=1, **kwargs):
    """Pagination helper method to workaround improper behaviors
    in GhApi.

     Parameters:
     operation: The GhApi function to execute
     per_page: The size of the page
     page: The starting page number

    Returns:
    AttrDict: results of the query
    """
    is_incomplete = True
    while is_incomplete:
        result = operation(**kwargs, per_page=per_page, page=page)
        is_incomplete = (
            False
            if not result
            or not "incomplete_results" in result
            or not "total_count" in result
            else result["incomplete_results"] and result["total_count"] == per_page
        )
        yield result
        page += 1

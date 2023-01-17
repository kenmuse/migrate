import json
import pytest
import requests
from click.testing import CliRunner
from collections import namedtuple
from migrate.common.api import resolve_rest_endpoint, resolve_graphql_endpoint
from migrate.main import cli
from pathlib import Path
from yaml import safe_load, load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

HttpErrorResponse = namedtuple("HttpErrorResponse", ["status_code", "json"])


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@pytest.fixture
def org_settings_response():
    fixtures = Path(__file__).parent.parent.joinpath("fixtures")
    return load_json(fixtures / "org_settings_01.json")


@pytest.fixture
def orgo_settings_yaml():
    fixtures = Path(__file__).parent.parent.joinpath("fixtures")
    return (fixtures / "org_settings_01.yml").read_text()


@pytest.fixture
def org_settings(orgo_settings_yaml):
    return safe_load(orgo_settings_yaml)


def load_json(path: str):
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def headers_std() -> dict:
    return {
        "X-GitHub-Media-Type": "github.v3; format=json",
        "X-RateLimit-Limit": 60,
        "X-RateLimit-Remaining": 59,
        "X-RateLimit-Reset": 1673633055,
        "X-RateLimit-Used": 1,
        "X-RateLimit-Resource": "core",
    }


@pytest.fixture
def response_org_settings_valid(monkeypatch, org_settings_response):
    def mock_urlread(*args, **kwargs):  # url, data=None, timeout=None):
        return (org_settings_response, dict())

    monkeypatch.setattr("fastcore.net.urlread", mock_urlread)


def patch_requests_post(monkeypatch, response: HttpErrorResponse):
    def mocked_post(uri, *args, **kwargs):
        mock = type("MockedResponse", (), {})()
        mock.status_code = response.status_code
        mock.json = lambda: response.json
        return mock

    monkeypatch.setattr(requests, "post", mocked_post)
    return response


@pytest.fixture(scope="module")
def error_status_response():
    errors = dict(
        forbidden=HttpErrorResponse(
            401,
            {
                "documentation_url": "https://docs.github.com/rest/reference/...",
                "message": "Must have admin rights to Repository.",
            },
        ),
        not_authorized=HttpErrorResponse(
            403,
            {
                "documentation_url": "https://docs.github.com/rest",
                "message": "Bad credentials",
            },
        ),
        not_found=HttpErrorResponse(
            404,
            {
                "documentation_url": "https://docs.github.com/rest/reference/...",
                "message": "Not Found",
            },
        ),
        conflict=HttpErrorResponse(
            409,
            {
                "documentation_url": "https://docs.github.com/rest/reference/....",
                "errors": "All actions and workflows are allowed on this organization",
                "message": "Conflict",
            },
        ),
    )
    return namedtuple("HttpErrorResponses", errors.keys())(*errors.values())


@pytest.fixture
def response_forbidden(monkeypatch, error_status_response):
    return patch_requests_post(
        monkeypatch=monkeypatch, response=error_status_response.forbidden
    )


@pytest.fixture
def response_not_authorized(monkeypatch, error_status_response):
    return patch_requests_post(
        monkeypatch=monkeypatch, response=error_status_response.not_authorized
    )


@pytest.fixture
def response_not_found(monkeypatch, error_status_response):
    return patch_requests_post(
        monkeypatch=monkeypatch, response=error_status_response.not_found
    )


@pytest.fixture
def target_settings():
    return ["-o", "test-org", "-h", "api.github.com", "-t", "test-token"]


def expected_HttpErrorResponse(response: HttpErrorResponse):
    code = response.status_code
    message = response.json["message"]
    return f"{{'status': {code}, 'message': '{message}'}}\n"


def test_orgs_get_ipallow_not_authenticated(response_forbidden, target_settings, runner):
    result = runner.invoke(
        cli,
        ["org", "ipallow", "list", *target_settings],
        catch_exceptions=False,
    )
    assert result.output == expected_HttpErrorResponse(response_forbidden)
    assert result.exit_code == 1


def test_orgs_get_ipallow_not_authorized(response_not_found, target_settings, runner):
    result = runner.invoke(
        cli,
        ["org", "ipallow", "list", *target_settings],
        catch_exceptions=False,
    )
    assert result.output == expected_HttpErrorResponse(response_not_found)
    assert result.exit_code == 1


def test_org_show_settings(
    monkeypatch,
    target_settings,
    response_org_settings_valid,
    org_settings,
    tmp_path,
    runner,
):
    file_path = tmp_path / "settings.yml"
    result = runner.invoke(
        cli,
        ["org", "settings", "list", "-f", file_path, *target_settings],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    data = load(file_path.read_text(), Loader=Loader)

    assert data == org_settings

import pytest
from click.testing import CliRunner
from migrate.common.api import (
    resolve_rest_endpoint,
    resolve_graphql_endpoint,
    create_client,
)
from migrate.common.repos import get_repo_settings


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_resolve_rest_default():
    assert resolve_rest_endpoint() == "https://api.github.com"


def test_resolve_rest_empty():
    assert resolve_rest_endpoint("") == "https://api.github.com"


def test_resolve_rest_no_protocol():
    assert resolve_rest_endpoint("api.github.com") == "https://api.github.com"


def test_resolve_rest_full_path():
    assert resolve_rest_endpoint("https://api.github.com") == "https://api.github.com"


def test_resolve_rest_server_fqdn():
    assert resolve_rest_endpoint("myserver.test") == "https://myserver.test/api/v3"


def test_resolve_rest_server_full():
    assert (
        resolve_rest_endpoint("https://myserver.test/api/v3")
        == "https://myserver.test/api/v3"
    )


def test_resolve_graphql_default():
    assert resolve_graphql_endpoint() == "https://api.github.com/graphql"


def test_resolve_graphql_empty():
    assert resolve_graphql_endpoint("") == "https://api.github.com/graphql"


def test_resolve_graphql_no_protocol():
    assert resolve_graphql_endpoint("api.github.com") == "https://api.github.com/graphql"


def test_resolve_graphql_full_path():
    assert (
        resolve_graphql_endpoint("https://api.github.com/graphql")
        == "https://api.github.com/graphql"
    )


def test_resolve_graphql_server_fqdn():
    assert (
        resolve_graphql_endpoint("myserver.test") == "https://myserver.test/api/graphql"
    )


def test_resolve_graphql_server_full():
    assert (
        resolve_graphql_endpoint("https://myserver.test/api/graphql")
        == "https://myserver.test/api/graphql"
    )


def repo_response():
    return {
        "id": 123456,
        "node_id": "R_abcdefg",
        "name": "test-repo",
        "full_name": "test-org/test-repo",
        "private": True,
        "owner": {
            "login": "test-org",
            "id": 23456,
            "node_id": "O_abcdefg",
            "type": "Organization",
        },
        "description": None,
        "fork": False,
        "language": None,
        "has_issues": True,
        "has_projects": True,
        "has_downloads": True,
        "has_wiki": True,
        "has_pages": False,
        "has_discussions": False,
        "mirror_url": None,
        "archived": False,
        "disabled": False,
        "license": None,
        "allow_forking": False,
        "is_template": False,
        "web_commit_signoff_required": False,
        "topics": [],
        "visibility": "internal",
        "default_branch": "main",
        "allow_squash_merge": False,
        "allow_merge_commit": True,
        "allow_rebase_merge": False,
        "allow_auto_merge": True,
        "delete_branch_on_merge": True,
        "allow_update_branch": False,
        "use_squash_pr_title_as_default": False,
        "squash_merge_commit_message": "COMMIT_MESSAGES",
        "squash_merge_commit_title": "COMMIT_OR_PR_TITLE",
        "merge_commit_message": "PR_TITLE",
        "merge_commit_title": "MERGE_MESSAGE",
        "organization": {
            "login": "test-org",
            "id": 23456,
            "node_id": "O_abcdefg",
            "type": "Organization",
        },
        "security_and_analysis": {
            "advanced_security": {"status": "disabled"},
            "secret_scanning": {"status": "disabled"},
            "secret_scanning_push_protection": {"status": "disabled"},
        },
    }


@pytest.fixture
def mock_url_repo_settings(monkeypatch):
    monkeypatch.setattr(
        "fastcore.net.urlread", lambda *args, **kwargs: (repo_response(), dict())
    )
    monkeypatch.setattr(
        "fastcore.net.urlsend", lambda *args, **kwargs: (repo_response(), dict())
    )


@pytest.fixture(scope="module")
def ghapi_client():
    return create_client(token="test-token")


def test_repos_get_settings(mock_url_repo_settings, ghapi_client):
    settings = get_repo_settings(ghapi_client, org="test-org", repo="test-repo")
    assert settings.allow_merge_commit
    assert settings.allow_auto_merge
    assert not settings.allow_squash_merge
    assert settings.ghas is not None

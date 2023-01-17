import json
import pytest
from click.testing import CliRunner
from ghapi.all import GhApi
from migrate.main import cli
from pathlib import Path
from yaml import safe_load, load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


@pytest.fixture
def repo_settings_response():
    fixtures = Path(__file__).parent.parent.joinpath("fixtures")
    return load_json(fixtures / "repo_settings_01.json")


@pytest.fixture
def repo_settings_yaml():
    # return "advanced_security: false\nallow_auto_merge: true\nallow_merge_commit: true\nallow_rebase_merge: false\nallow_squash_merge: false\nallow_update_branch: false\ndefault_branch: main\ndelete_branch_on_merge: true\nsecret_scanning: false\nsecret_scanning_push_protection: false\nvisibility: internal\n"
    fixtures = Path(__file__).parent.parent.joinpath("fixtures")
    return (fixtures / "repo_settings_01.yml").read_text()


@pytest.fixture
def repo_settings(repo_settings_yaml):
    return safe_load(repo_settings_yaml)


def load_json(path: str):
    with open(path) as f:
        return json.load(f)


@pytest.fixture
def target_settings():
    return ["-o", "test-org", "-h", "api.github.com", "-t", "test-token"]


@pytest.fixture
def urlread_settings_response(monkeypatch, repo_settings_response):
    def mock_urlread(*args, **kwargs):  # url, data=None, timeout=None):
        return (repo_settings_response, dict())

    monkeypatch.setattr("fastcore.net.urlread", mock_urlread)


def test_repos_get_settings(target_settings, urlread_settings_response, runner):

    result = runner.invoke(
        cli,
        [
            "repo",
            "settings",
            "list",
            *target_settings,
            "test-repo",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_repos_show_settings(
    monkeypatch,
    target_settings,
    urlread_settings_response,
    repo_settings,
    tmp_path,
    runner,
):
    file_path = tmp_path / "settings.yml"
    result = runner.invoke(
        cli,
        [
            "repo",
            "settings",
            "list",
            "-f",
            file_path,
            *target_settings,
            "test-repo",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    data = load(file_path.read_text(), Loader=Loader)

    assert data == repo_settings

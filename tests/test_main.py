import pytest
from click.testing import CliRunner
from migrate.main import cli


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_help(runner):
    result = runner.invoke(cli, ["--help"], catch_exceptions=False)
    assert result.exit_code == 0


def test_orgs_command(runner):
    result = runner.invoke(cli, ["org"], catch_exceptions=False)
    assert result.exit_code == 0


def test_repos_comment(runner):
    result = runner.invoke(cli, ["repo"], catch_exceptions=False)
    assert result.exit_code == 0

import pytest
from migrate.common.orgs import OrgSettings
from migrate.common.repos import RepoSettings


def test_OrgSettings_can_deserialize():
    data = dict(
        advanced_security_enabled_for_new_repositories=False,
        blog=None,
        company=None,
        default_repository_permission="read",
        dependabot_alerts_enabled_for_new_repositories=False,
        dependabot_security_updates_enabled_for_new_repositories=False,
        dependency_graph_enabled_for_new_repositories=False,
        description=None,
        email=None,
        has_organization_projects=True,
        has_repository_projects=True,
        location=None,
        members_can_create_internal_repositories=True,
        members_can_create_private_repositories=True,
        members_can_create_public_repositories=True,
        members_can_create_repositories=True,
        members_can_fork_private_repositories=False,
        name=None,
        secret_scanning_enabled_for_new_repositories=False,
        secret_scanning_push_protection_custom_link=False,
        secret_scanning_push_protection_custom_link_enabled=False,
        secret_scanning_push_protection_enabled_for_new_repositories=False,
        twitter_username=None,
        two_factor_requirement_enabled=False,
        web_commit_signoff_required=False,
        members_can_create_private_pages=False,
        members_can_create_public_pages=False,
    )
    org_settings = OrgSettings.from_dict(data)
    assert org_settings is not None
    assert org_settings.to_dict() == data


@pytest.mark.parametrize("setting", [True, False])
def test_OrgSettings_deserialize_members_can_create_pages(setting):
    data = dict(members_can_create_pages=setting)
    org_settings = OrgSettings.from_dict(data)
    assert org_settings.members_can_create_public_pages == setting
    assert org_settings.members_can_create_private_pages == setting


def test_OrgSettings_can_update():
    data = dict(members_can_create_pages=False, name="test")
    org_settings = OrgSettings.from_dict(data)
    final = org_settings.update(
        dict(
            name=org_settings.name + "_X",
            description="test2desc",
            members_can_create_private_pages=True,
        )
    )
    assert final.name == "test_X"
    assert final.description == "test2desc"
    assert final.members_can_create_public_pages == False
    assert final.members_can_create_private_pages == True


def test_RepoSettings_can_deserialize():
    data = dict(
        allow_squash_merge=False,
        allow_merge_commit=True,
        allow_rebase_merge=False,
        allow_auto_merge=True,
        delete_branch_on_merge=False,
        allow_update_branch=True,
        default_branch="main",
        visibility="public",
    )
    repo_settings = RepoSettings.from_dict(data)
    assert repo_settings is not None
    converted = repo_settings.to_dict()
    assert converted == data


def test_RepoSettings_can_deserialize_with_ghas():
    data = dict(
        allow_squash_merge=False,
        allow_merge_commit=True,
        allow_rebase_merge=False,
        allow_auto_merge=True,
        delete_branch_on_merge=False,
        allow_update_branch=True,
        default_branch="main",
        visibility="public",
        advanced_security=True,
        secret_scanning=True,
        secret_scanning_push_protection=False,
    )
    repo_settings = RepoSettings.from_dict(data)
    assert repo_settings is not None
    converted = repo_settings.to_dict()
    assert converted == data

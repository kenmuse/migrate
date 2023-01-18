"""Methods for using the GitHub API for organizations"""

import sys
from dataclasses import dataclass, field
from enum import Enum, unique, auto
from ghapi.all import GhApi
from .api import (
    GhPublicKey,
    is_ghec,
    create_client,
    resolve_graphql_endpoint,
    encrypt_secret,
    rate_limited,
    call_with_exception_handler,
    get_paged_data,
    paginated,
    graphql_query,
)
from .repos import Repo
from .types import SerializedEnum, DictData, alternative_name


@unique
class OrgRepoSort(SerializedEnum):
    """Indicates the sort order for a repository list"""

    CREATED = auto()
    UPDATED = auto()
    PUSHED = auto()
    FULL_NAME = auto()


@unique
class OrgRepoType(SerializedEnum):
    """Indicates the type of repositories to list"""

    ALL = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    FORKS = auto()
    SOURCES = auto()
    MEMBER = auto()


@unique
class OrgSecretVisibility(SerializedEnum):
    """Indicates the visibility for an organization secret"""

    SELECTED = auto()
    ALL = auto()
    PRIVATE = auto()


@unique
class OrgRepoPermissions(SerializedEnum):
    """Indicates the permission levels for organization repositories"""

    READ = auto()
    WRITE = auto()
    ADMIN = auto()
    NONE = auto()


@unique
class OrgActionsEnabledRepositories(SerializedEnum):
    """The Actions permission policy that controls the repositories allowed to run Actions"""

    ALL = auto()
    NONE = auto()
    SELECTED = auto()


@unique
class OrgAllowedActions(SerializedEnum):
    """The permissions policy that controls the Actions and reusable workflows allowed to run"""

    ALL = auto()
    LOCAL_ONLY = auto()
    SELECTED = auto()


@dataclass(frozen=True)
class Organization(DictData):
    node_id: str
    url: str
    name: str
    description: str


@dataclass(frozen=True)
class OrgActionsPermissions(DictData):
    enabled_repositories: OrgActionsEnabledRepositories
    allowed_actions: OrgAllowedActions


@dataclass(frozen=True)
class OrgSelectedActions(DictData):
    github_owned_allowed: bool
    verified_allowed: bool
    patterns_allowed: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class IpAllowListEntry(DictData):
    allow_list_value: str
    is_active: bool
    name: str
    id: str


@dataclass(frozen=True)
class OrgSettings(DictData):
    company: str = field(default=None)
    email: str = field(default=None)
    twitter_username: str = field(default=None)
    location: str = field(default=None)
    name: str = field(default=None, metadata=alternative_name("login"))
    description: str = field(default=None)
    blog: str = field(default=None)
    web_commit_signoff_required: bool = field(default=False)
    has_organization_projects: bool = field(default=False)
    has_repository_projects: bool = field(default=False)
    default_repository_permission: OrgRepoPermissions = field(
        default=OrgRepoPermissions.READ
    )
    members_can_create_repositories: bool = field(default=False)
    two_factor_requirement_enabled: bool = field(default=False)
    members_can_create_public_repositories: bool = field(
        default=False,
        metadata=alternative_name(
            "members_allowed_repository_creation_type",
            converter=lambda value: value == "all",
        ),
    )
    members_can_create_private_repositories: bool = field(
        default=False,
        metadata=alternative_name(
            "members_allowed_repository_creation_type",
            converter=lambda value: value != "none",
        ),
    )
    members_can_create_internal_repositories: bool = field(
        default=False,
        metadata=alternative_name(
            "members_allowed_repository_creation_type",
            converter=lambda value: value != "none",
        ),
    )
    members_can_create_private_pages: bool = field(
        default=False, metadata=alternative_name("members_can_create_pages")
    )
    members_can_create_public_pages: bool = field(
        default=False, metadata=alternative_name("members_can_create_pages")
    )
    members_can_fork_private_repositories: bool = field(default=False)
    advanced_security_enabled_for_new_repositories: bool = field(default=False)
    dependabot_alerts_enabled_for_new_repositories: bool = field(default=False)
    dependabot_security_updates_enabled_for_new_repositories: bool = field(default=False)
    dependency_graph_enabled_for_new_repositories: bool = field(default=False)
    secret_scanning_enabled_for_new_repositories: bool = field(default=False)
    secret_scanning_push_protection_enabled_for_new_repositories: bool = field(
        default=False
    )
    secret_scanning_push_protection_custom_link_enabled: bool = field(default=False)
    secret_scanning_push_protection_custom_link: str = field(default=False)


@dataclass(frozen=True)
class OrgSecret:
    """Represents an organization-level stored secret"""

    name: str
    visibility: OrgSecretVisibility
    selected_repositories_url: str

    @staticmethod
    def deserialize(secret):
        return OrgSecret(
            name=secret.name,
            visibility=OrgSecretVisibility.from_str(secret.visibility),
            selected_repositories_url=None
            if not secret or not "selected_repositories_url" in secret
            else secret.selected_repositories_url,
        )


def get_org_public_key(client: GhApi, org: str):
    """Retrieves the public key for the organization"""
    result = call_with_exception_handler(org, client.actions.get_org_public_key, org=org)
    return GhPublicKey(result.key, result.key_id)


def list_org_secrets(client: GhApi, org: str):
    """Retrieves a list of secrets from the organization"""
    results = call_with_exception_handler(
        org, paginated, client.actions.list_org_secrets, org=org
    )
    return [
        OrgSecret.deserialize(secret)
        for result in results
        for secret in result.secrets
        if result.total_count > 0
    ]


@rate_limited
def set_org_secret(
    client: GhApi,
    org: str,
    name: str,
    value: str,
    visibility: OrgSecretVisibility,
    selected_repository_ids: list[int] | None = None,
):
    """Configures an organization-level secret"""
    key = get_org_public_key(client, org)
    encv = encrypt_secret(key.key, value)
    results = call_with_exception_handler(
        org,
        client.actions.create_or_update_org_secret,
        org=org,
        secret_name=name,
        encrypted_value=encv,
        key_id=key.id,
        visibility=str(visibility),
        selected_repository_ids=selected_repository_ids,
    )
    return results


def get_org_settings(client: GhApi, org: str):
    """Retrieves the organization details"""
    result = client.orgs.get(org)
    return OrgSettings.from_dict(result)


def get_org_id(endpoint: str, token: str, org: str):
    """Retrieves the organization ID for the specified organization"""
    query = """
    query($org: String!) {
        organization(login: $org) {
            id
        }
    }
    """

    result = graphql_query(
        query,
        token,
        endpoint=endpoint,
        variables={"org": org},
    )
    return result["data"]["organization"]["id"]


def get_org_ip_allow_list(endpoint: str, token: str, org: str):
    """Retrieves the organization IP allow list"""
    query = """
    query($org: String!, $endCursor: String) {
        organization(login: $org) {
            ipAllowListEntries(first: 100, after: $endCursor) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    allowListValue
                    isActive
                    name
                    owner {
                        ... on Organization {
                        id
                        }
                    }
                }
            }
        }
    }
    """

    has_next_page = True
    end_cursor = None
    values = []
    while has_next_page:
        result = graphql_query(
            query,
            token,
            endpoint=endpoint,
            variables={"org": org, "endCursor": end_cursor},
        )
        entries = result["data"]["organization"]["ipAllowListEntries"]
        for item in entries["nodes"]:
            values.append(
                IpAllowListEntry(
                    allow_list_value=item["allowListValue"],
                    is_active=item["isActive"],
                    id=item["id"],
                    name=item["name"],
                )
            )
        has_next_page = entries["pageInfo"]["hasNextPage"]
        end_cursor = entries["pageInfo"]["endCursor"]

    return values


def list_org_selected_repos_for_secret(client: GhApi, url: str):
    """Retrieves a list of the selected Repos from the provided URL"""
    results = call_with_exception_handler(
        url, paginated, get_paged_data, client=client, url=url
    )
    return (
        []
        if results is None
        else [
            Repo.deserialize(repo)
            for result in results
            for repo in result.repositories
            if result is not None
            if repo is not None
        ]
    )


def list_org_permissions_actions_allowed_repos(client: GhApi, org: str):
    """Retrieves a list of the selected Repos enabled for GitHub Actions in the specified org"""
    results = call_with_exception_handler(
        org,
        paginated,
        client.actions.llist_selected_respositories_enabled_github_actions_organization,
        org=org,
    )
    return (
        []
        if results is None
        else [
            Repo.deserialize(repo)
            for result in results
            for repo in result.repositories
            if result is not None
            if repo is not None
        ]
    )


def get_org_actions_permissions(client: GhApi, org: str):
    results = call_with_exception_handler(
        org, client.actions.get_github_actions_permissions_organization, org=org
    )
    return OrgActionsPermissions.from_dict(results)


def set_org_actions_permissions(
    client: GhApi,
    org: str,
    allowed_repositories: OrgActionsEnabledRepositories,
    allowed_actions: OrgAllowedActions,
):
    # results will always be empty
    call_with_exception_handler(
        org,
        client.actions.set_github_actions_permissions_organization,
        org=org,
        enabled_repositories=str(allowed_repositories),
        allowed_actions=str(allowed_actions),
    )


def get_org_permissions_allowed_actions(client: GhApi, org: str):
    results = call_with_exception_handler(
        org, client.actions.get_allowed_actions_organization, org=org
    )
    return OrgAllowedActions.from_dict(results)


def create_org_ip_allow_list_entry(
    endpoint: str, token: str, org: str, ip_address: str, name: str, is_active: str
):
    mutation = """
    mutation($ownerId: ID!, $ip_address: String!, $name: String, $is_active: Boolean!) {
      createIpAllowListEntry(
        input: {
          ownerId: $ownerId
          allowListValue: $ip_address
          name: $name
          isActive: $is_active
        }
      ) {
        ipAllowListEntry {
          id
          name
          allowListValue
          createdAt
          updatedAt
          owner {
                ... on Organization {
                id
                }
            }
        }
      }
    }
    """
    org_id = get_org_id(endpoint, token, org)
    result = graphql_query(
        mutation,
        token,
        endpoint=endpoint,
        variables={
            "ownerId": org_id,
            "ip_address": ip_address,
            "name": name,
            "is_active": is_active,
        },
    )
    return result


def delete_org_ip_allow_list_entry(endpoint: str, token: str, entry_id: str):
    mutation = """
    mutation($entry_id: ID!) {
      deleteIpAllowListEntry(
        input: {
          ipAllowListEntryId: $entry_id
        }
      ) {
        ipAllowListEntry {
          id
          name
          allowListValue
          createdAt
          updatedAt
          owner {
                ... on Organization {
                id
                }
            }
        }
      }
    }
    """

    result = graphql_query(
        mutation,
        token,
        endpoint=endpoint,
        variables={"entry_id": entry_id},
    )
    return result


def list_organization_repositories(
    client: GhApi,
    org: str,
    sort: OrgRepoSort = OrgRepoSort.FULL_NAME,
    type: OrgRepoType = OrgRepoType.ALL,
) -> list[Repo]:
    """Lists the repositories in a specified organization"""

    def convert(repo):
        return Repo.deserialize(repo)

    result = call_with_exception_handler(
        paginated, client.repos.list_for_org, org=org, sort=str(sort), type=str(type)
    )
    return list(map(convert, result))


def get_organizations_in_enterprise(hostname: str, token: str, enterprise: str):
    """Retrieves the list of organizations in an enterprise"""

    def convert(org):
        return Organization(
            node_id=org.node_id, url=org.url, name=org.login, description=org.description
        )

    if is_ghec(hostname):
        return get_organizations_in_cloud_enterprise(
            resolve_graphql_endpoint(hostname=hostname),
            token=token,
            enterprise=enterprise,
        )
    else:
        client = create_client(hostname=hostname, token=token)
        result = call_with_exception_handler(paginated, client.orgs.list)
        return list(
            filter(
                lambda e: e.name != "actions" and e.name != "github", map(convert, result)
            )
        )


def get_organizations_in_cloud_enterprise(endpoint: str, token: str, enterprise: str):
    """Retrieves the list of organizations in a GHEC enterprise"""
    query = """
    query($slug: String!, $endCursor: String) {
        enterprise(slug: $slug) {
            organizations(first: 100, after: $endCursor) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                nodes {
                    id
                    login
                    description
                    url
                }
            }
        }
    }
    """

    has_next_page = True
    end_cursor = None
    values = []
    while has_next_page:
        result = graphql_query(
            query,
            token,
            endpoint=endpoint,
            variables={"slug": enterprise, "endCursor": end_cursor},
        )

        if (
            result is None
            or result["data"] is None
            or result["data"]["enterprise"] is None
        ):
            if "errors" in result:
                print(
                    f"Error retrieving organizations from '{enterprise}': {result['errors']}",
                    file=sys.stderr,
                )
            else:
                print(
                    f"No organizations found in '{enterprise}'. Token requires read:enterprise permissions",
                    file=sys.stderr,
                )
            sys.exit(1)
        entries = result["data"]["enterprise"]["organizations"]
        for item in entries["nodes"]:
            values.append(
                Organization(
                    description=item["description"],
                    node_id=item["id"],
                    name=item["login"],
                    url=item["url"],
                )
            )
        has_next_page = entries["pageInfo"]["hasNextPage"]
        end_cursor = entries["pageInfo"]["endCursor"]

    return values

"""Methods for using the GitHub API for organizations"""

from copy import copy
from dataclasses import dataclass, fields
from enum import Enum, unique, auto
from ghapi.all import GhApi
from common.api import (
    GhPublicKey,
    encrypt_secret,
    rate_limited,
    call_with_exception_handler,
)
from common.types import SerializedEnum, DictData, alternative_name


@unique
class RepoVisibility(SerializedEnum):
    """Indicates the visibility for a repository"""

    PRIVATE = auto()
    INTERNAL = auto()
    PUBLIC = auto()


@dataclass(frozen=True)
class Repo(DictData):
    """Summary details for a repository"""

    name: str
    id: int  # pylint: disable=invalid-name
    owner: str
    full_name: str
    url: str
    is_private: bool

    @staticmethod
    def deserialize(repo):
        return Repo(
            name=repo.name,
            owner=repo.owner.login,
            full_name=repo.full_name,
            id=repo.id,
            url=repo.url,
            is_private=repo.private,
        )


@dataclass(frozen=True)
class GhasSettings(DictData):
    """Settings for GitHub Advanced Security"""

    advanced_security: bool = False
    secret_scanning: bool = False
    secret_scanning_push_protection: bool = False

    def serialize(self) -> dict:
        """Converts the settings to a dict for JSON/REST serialization"""
        return {
            "advanced_security": {
                "status": "enabled" if self.advanced_security else "disabled"
            },
            "secret_scanning": {
                "status": "enabled" if self.secret_scanning else "disabled"
            },
            "secret_scanning_push_proection": {
                "status": "enabled"
                if self.secret_scanning_push_protection
                else "disabled"
            },
        }

    @staticmethod
    def deserialize(settings):
        """Converts the settings from a dict for JSON/REST deserialization"""
        return (
            GhasSettings(
                advanced_security=settings.advanced_security.status == "enabled",
                secret_scanning=settings.secret_scanning.status == "enabled",
                secret_scanning_push_protection=hasattr(
                    settings, "secret_scanning_push_protection"
                )
                and settings.secret_scanning_push_protection.status == "enabled",
            )
            if settings is not None
            else None
        )


@dataclass(frozen=True)
class RepoSettings(DictData):
    """Settings for a repository"""

    allow_squash_merge: bool = True
    allow_merge_commit: bool = True
    allow_rebase_merge: bool = True
    allow_auto_merge: bool = False
    delete_branch_on_merge: bool = False
    allow_update_branch: bool = False
    default_branch: str = "main"
    visibility: RepoVisibility = RepoVisibility.PRIVATE
    ghas: GhasSettings = None

    def __dict__(self):
        return self.to_dict()

    def to_dict(self):
        """Converts the settings to a dict for serialization"""
        settings = super().to_dict()
        settings.pop("ghas")
        if self.ghas is not None:
            settings.update(self.ghas.to_dict())
        return settings

    @classmethod
    def from_dict(cls, settings: dict):
        ghas_settings = [f.name for f in fields(GhasSettings) if f.init]
        has_values = any([k in settings for k in ghas_settings])
        if has_values:
            settings = copy(settings)
            ghas = GhasSettings.from_dict(settings)
            settings["ghas"] = ghas
        result = super().from_dict(settings)
        return result

    @staticmethod
    def deserialize(settings, include_ghas: bool):
        """Converts the settings from a dict for deserialization"""
        ghas = (
            GhasSettings.deserialize(settings.security_and_analysis)
            if include_ghas and hasattr(settings, "security_and_analysis")
            else None
        )
        return RepoSettings(ghas=ghas).update(settings)


def get_repository_id(client: GhApi, org: str, repo: str):
    """Retrieves the repository id for the provided repo"""
    result = call_with_exception_handler(org, client.repos.get, owner=org, repo=repo)
    return result.id


def get_repo_public_key(client: GhApi, org: str, repo: str):
    """Retrieves the public key for the organization"""
    result = call_with_exception_handler(
        org, client.actions.get_repo_public_key, org=org, repo=repo
    )
    return GhPublicKey(result.key, result.key_id)


@rate_limited
def set_repo_secret(client: GhApi, org: str, repo: str, name: str, value: str):
    """Configures a repository-level secret"""
    key = get_repo_public_key(client, org, repo)
    encv = encrypt_secret(key.key, value)
    results = call_with_exception_handler(
        org,
        client.actions.create_or_update_repo_secret,
        owner=org,
        repo=repo,
        secret_name=name,
        encrypted_value=encv,
        key_id=key.id,
    )
    return results


def get_repo_settings(
    client: GhApi, org: str, repo: str, include_ghas=True
) -> RepoSettings:
    """Gets the repository settings"""
    result = call_with_exception_handler(
        f"{org}/{repo}", client.repos.get, owner=org, repo=repo
    )
    return RepoSettings.deserialize(result, include_ghas=include_ghas)


@rate_limited
def set_repo_settings(client: GhApi, org: str, repo: str, settings: RepoSettings):
    """Configures the repository using the provided settings"""

    result = call_with_exception_handler(
        f"{org}/{repo}",
        client.repos.update,
        owner=org,
        repo=repo,
        allow_squash_merge=settings.allow_squash_merge,
        allow_merge_commit=settings.allow_merge_commit,
        allow_rebase_merge=settings.allow_rebase_merge,
        allow_auto_merge=settings.allow_auto_merge,
        delete_branch_on_merge=settings.delete_branch_on_merge,
        default_branch=settings.default_branch,
        allow_update_branch=settings.allow_update_branch,
        visibility=settings.visibility,
    )

    return (
        RepoSettings.deserialize(result, include_ghas=False)
        if settings.ghas is None
        else set_repo_ghas_settings(client, org, repo, settings.ghas)
    )


@rate_limited
def set_repo_ghas_settings(client: GhApi, org: str, repo: str, settings: GhasSettings):
    """Configures the repository GHAS settings using the provided settings"""
    result = call_with_exception_handler(
        f"{org}/{repo}",
        client.repos.update,
        owner=org,
        repo=repo,
        security_and_analysis=settings.serialize(),
    )
    return RepoSettings.deserialize(result, include_ghas=True)

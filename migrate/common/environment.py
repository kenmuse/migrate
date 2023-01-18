from ghapi.all import GhApi
from .api import (
    GhPublicKey,
    encrypt_secret,
    rate_limited,
    call_with_exception_handler,
)
from .repos import get_repository_id


def get_environment_public_key(client: GhApi, org: str, repo: str, environment: str):
    """Retrieves the public key for the organization"""
    repo_id = get_repository_id(client, org, repo)
    result = call_with_exception_handler(
        org,
        client.actions.get_org_public_key,
        org=org,
        repository_id=repo_id,
        emvironment_name=environment,
    )
    return GhPublicKey(result.key, result.key_id)


@rate_limited
def set_environment_secret(
    client: GhApi, org: str, repo: str, environment: str, name: str, value: str
):
    """Configures an environment-level secret"""
    repo_id = get_repository_id(client, org, repo)
    key = get_environment_public_key(client, org, repo_id, environment)
    encv = encrypt_secret(key.key, value)
    results = call_with_exception_handler(
        org,
        client.actions.create_or_update_repo_secret,
        owner=org,
        repository_id=repo_id,
        environment_name=environment,
        secret_name=name,
        encrypted_value=encv,
        key_id=key.id,
    )
    return results

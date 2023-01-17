"""
Orgs command implementation
"""

import sys
import click
from common.options import (
    CONTEXT_SETTINGS,
    target_options,
    TargetState,
    pass_targetstate,
)
from common.api import create_client
from common.orgs import (
    get_org_settings,
    get_org_actions_permissions,
    set_org_actions_permissions,
    get_org_permissions_allowed_actions,
    OrgSecretVisibility,
)
from yaml import load, dump
from .secrets import org_secrets
from .ipallow import org_ipallow
from .settings import org_settings
from .actions import org_actions


try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


@click.group(context_settings=CONTEXT_SETTINGS)
def org():
    """Provides commands for migrating organization resources"""


org.add_command(org_secrets)
org.add_command(org_ipallow)
org.add_command(org_settings)
org.add_command(org_actions)

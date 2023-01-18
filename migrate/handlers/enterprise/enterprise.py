"""
Enterprise command implementation
"""

import sys
import click
import json
from ...common.options import (
    CONTEXT_SETTINGS,
    target_options,
    TargetState,
    pass_targetstate,
)
from ...common.api import is_ghec
from ...common.orgs import get_organizations_in_enterprise, Organization
from .org import enterprise_org


@click.group(context_settings=CONTEXT_SETTINGS)
def enterprise():
    """Provides commands for migrating enterprise resources"""


enterprise.add_command(enterprise_org)

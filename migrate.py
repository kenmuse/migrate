"""
Entrypoiny for standalone executable version of migrate
"""

from migrate.common.options import CONTEXT_SETTINGS
from migrate.handlers.enterprise.enterprise import enterprise
from migrate.handlers.org.org import org
from migrate.handlers.repo.repo import repo
from migrate.main import cli

if __name__ == "__main__":
    cli()

"""
Common command line settings and options
"""

import os
import click
from yaml import load, dump

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class BaseState:
    """Base class for state objects"""

    def read_config(self, ctx, filename):
        """
        Loads the state data from the specified filename and context, preserving
        any values assigned from the command line or environment
        """
        key_prefix = None if not hasattr(self, "prefix") else self.prefix
        if filename and os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as file:
                config = load(file.read(), Loader=Loader)
            if key_prefix is None:
                ctx.default_map = config
            else:
                ctx.default_map = {}
                for key in (key for key in config if key.startswith(f"{key_prefix}_")):
                    attr = key[len(key_prefix) + 1 :]
                    ctx.default_map[attr] = config[key]

    def write_config(self, filename):
        """Writes the state to a config file"""
        with open(filename, "w", encoding="utf-8") as file:
            dump(self, file)


class TargetState(BaseState):
    """Reference to a particular GitHub host environment"""

    def __init__(self):
        self.hostname = None
        self.token = None
        self.org = None
        self.prefix = None


class MigrationState(BaseState):
    """Common state used for all commands"""

    def __init__(self):
        self.src_token = None
        self.dest_token = None
        self.src_hostname = None
        self.dest_hostname = None
        self.src_org = None
        self.dest_org = None


CONTEXT_SETTINGS = dict(
    token_normalize_func=lambda x: x.lower(),
    auto_envvar_prefix=None,
    ignore_unknown_options=False,
)

pass_migrationstate = click.make_pass_decorator(MigrationState, ensure=True)
"""Passes the MigrationState class as a context variable"""

pass_targetstate = click.make_pass_decorator(TargetState, ensure=True)
"""Passes the TargetState class as a context variable"""


def _option_src_token(fxn):
    """Creates the --src_token option"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(MigrationState)
        state.src_token = value
        return value

    return click.option(
        "-st",
        "--src_token",
        required=True,
        expose_value=False,
        envvar="SRC_TOKEN",
        help="The GHAE access PAT",
        callback=callback,
    )(fxn)


def _option_src_hostname(fxn):
    """Creates the --src_hostname option"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(MigrationState)
        state.src_hostname = value
        return value

    return click.option(
        "-h",
        "--src_hostname",
        required=True,
        default="api.github.com",
        expose_value=False,
        envvar="SRC_HOSTNAME",
        help="The GHAE instance hostname",
        callback=callback,
    )(fxn)


def _option_dest_token(fxn):
    """Creates the --dest_token option"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(MigrationState)
        state.dest_token = value
        return value

    return click.option(
        "-dt",
        "--dest_token",
        required=False,
        expose_value=False,
        envvar="DEST_TOKEN",
        help="The GHEC access PAT",
        callback=callback,
    )(fxn)


def _option_src_org(fxn):
    """Creates the --src_org option"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(MigrationState)
        state.src_org = value
        return value

    return click.option(
        "-so",
        "--src_org",
        expose_value=False,
        envvar="SRC_ORG",
        help="The source organization",
        callback=callback,
    )(fxn)


def _option_dest_org(fxn):
    """Creates the --dest_org option"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(MigrationState)
        state.dest_org = value
        return value

    return click.option(
        "-do",
        "--dest_org",
        expose_value=False,
        envvar="DEST_ORG",
        help="The destination organization",
        callback=callback,
    )(fxn)


def _option_target_config_prefix(fxn):
    """Creates the --prefix option for loading state from a file"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(TargetState)
        state.prefix = value
        return value

    return click.option(
        "-p",
        "--prefix",
        expose_value=False,
        required=False,
        callback=callback,
        help="Load configuration settings with <PREFIX>_",
    )(fxn)


def _option_target_config(fxn):
    """Creates the --config option for loading settings for a single target from a file"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(TargetState)
        state.read_config(ctx, value)
        return value

    return click.option(
        "-c",
        "--config",
        expose_value=False,
        help="Load settings from specified configuration file",
        callback=callback,
    )(fxn)


def _option_target_org(fxn):
    """Creates the --org option"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(TargetState)
        state.org = value
        return value

    return click.option(
        "-o",
        "--org",
        expose_value=False,
        envvar="GH_ORG",
        required=True,
        help="The organization/owner name",
        callback=callback,
    )(fxn)


def _option_migration_config(fxn):
    """Creates the --config option for loading migration settings from a file"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(MigrationState)
        state.read_config(ctx, value)
        return value

    return click.option(
        "-c",
        "--config",
        expose_value=False,
        help="Load settings from specified configuration file",
        callback=callback,
    )(fxn)


def _option_target_token(fxn):
    """Creates the --token option"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(TargetState)
        state.token = value
        return value

    return click.option(
        "-t",
        "--token",
        required=True,
        expose_value=False,
        envvar="GH_TOKEN",
        help="The GitHub access PAT",
        callback=callback,
    )(fxn)


def _option_target_hostname(fxn):
    """Creates the --hostname option"""

    def callback(ctx, _param, value):
        state = ctx.ensure_object(TargetState)
        state.hostname = value
        return value

    return click.option(
        "-h",
        "--hostname",
        required=True,
        default="api.github.com",
        expose_value=False,
        envvar="GH_HOSTNAME",
        help="The GH instance hostname (ex: api.github.com, server.ghe.com)",
        callback=callback,
    )(fxn)


def migration_options(fxn):
    """Decorator to configure the common command line options for migrating between GitHub instances"""
    fxn = _option_src_token(fxn)
    fxn = _option_src_hostname(fxn)
    fxn = _option_dest_token(fxn)
    fxn = _option_src_org(fxn)
    fxn = _option_dest_org(fxn)
    fxn = _option_migration_config(fxn)
    return fxn


def target_options(fxn):
    """Decorator to configure the common command line options for a single GitHub target"""
    fxn = _option_target_token(fxn)
    fxn = _option_target_hostname(fxn)
    fxn = _option_target_org(fxn)
    fxn = _option_target_config_prefix(fxn)
    fxn = _option_target_config(fxn)
    return fxn

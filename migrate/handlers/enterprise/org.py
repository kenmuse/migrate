"""
Enterprise org command implementation
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
from yaml import dump


class RequiredIfGhec(click.Option):
    """Implements logic to require field if the target is GHEC"""

    def __init__(self, *args, **kwargs):
        kwargs["help"] = (
            kwargs.get("help", "")
            + " NOTE: This argument is required when targeting GHEC."
        ).strip()
        super(RequiredIfGhec, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        field_is_present = self.name in opts
        hostname = "api.github.com"
        if "hostname" in opts:
            hostname = opts["hostname"]
        elif ctx.default_map is not None and "hostname" in ctx.default_map:
            hostname = ctx.default_map["hostname"]

        target_is_ghec = is_ghec(hostname)

        if field_is_present and not target_is_ghec:
            click.echo(
                "The field '%s' is not required and will be ignored" % self.name,
                file=sys.stderr,
            )

        if not field_is_present and target_is_ghec:
            raise click.UsageError(
                "The field '%s' is required when targeting GHEC" % self.name
            )

        self.prompt = None

        return super(RequiredIfGhec, self).handle_parse_result(ctx, opts, args)


@click.group("org", context_settings=CONTEXT_SETTINGS)
def enterprise_org():
    """Enterprise-level organization commands"""


@enterprise_org.command("list", no_args_is_help=True)
@click.option(
    "--enterprise",
    "-e",
    required=False,
    cls=RequiredIfGhec,
    default=None,
    help="The slug for the enterprise",
)
@click.option(
    "--output",
    "-f",
    type=click.File("w"),
    default=sys.stdout,
    help="Output file. If not provided, stdout is used.",
)
@click.option(
    "--compact",
    "-r",
    help="Use compact output when reporting to stdout (default: False)",
    is_flag=True,
    flag_value=True,
    default=False,
    required=False,
)
@click.option(
    "--json/--yaml",
    "-j/-y",
    "is_json",
    help="Determines the output format (default: yaml)",
    is_flag=True,
    flag_value=True,
    default=False,
    required=False,
)
@target_options
@pass_targetstate
def list_enterprise_orgs(
    ctx: TargetState,
    enterprise: str,
    output: click.File,
    compact: bool,
    is_json: bool,
):
    """Lists the organizations in the enterprise"""
    if (is_ghec(ctx.hostname)) and (enterprise is None):
        click.echo("Enterprise slug is required for GHEC")
        sys.exit(1)

    organizations = get_organizations_in_enterprise(
        hostname=ctx.hostname, enterprise=enterprise, token=ctx.token
    )
    if sys.stdout.isatty() and compact:
        click.echo(organizations)
    else:
        results = list(map(lambda r: r.to_dict(), organizations))
        if is_json:
            json.dump(results, output, indent=2 if sys.stdout.isatty() else None)
        else:
            dump(results, output)

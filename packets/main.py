"""The Command Line Interface for the packets sub-package"""
# from pypi
import click

# this project
from .get import (
    GetDefaults,
    GetPackets,
    )

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def main(context):
    """A Packet (pcap) command-line utility"""
    return

@main.command(context_settings=CONTEXT_SETTINGS, short_help="Get packet files and merge them.")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target")
@click.option("--start", default=GetDefaults.start,
              metavar="<date-time>",
              help="Earliest packet time to get.")
@click.option("--end", default=GetDefaults.end,
              metavar="<date-time>",
              help="Latest packet time to get.")
@click.option("--compression",
              default=GetDefaults.compression,
              type=click.Choice(GetPackets.compressions))
def get(source, target, start, end, compression):
    """Collects the Packets for the user"""
    collector = GetPackets(source=source, target=target, start=start, end=end)
    collector()
    return

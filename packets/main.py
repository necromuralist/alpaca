"""The Command Line Interface for the packets sub-package"""
# from pypi
import click

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def main(context):
    """A Packet (pcap) command-line utility"""
    return

@main.command(context_settings=CONTEXT_SETTINGS, short_help="Get packet files and merge them.")
def get():
    return

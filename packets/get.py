"""Get the packets"""
# python standard library
import os

# this project
from .base import AlpacaBase


class GetDefaults:
    """Default Values when getting packets"""
    start = None
    end = None
    compression="gzip"


class GetPackets(AlpacaBase):
    """Packet retriever

    This gets the packets and assembles them into a single file

    Args:
     source: path to the directory with the PCAP files
     target: path to where you want to keep the files
     start: date/time for the earliest packet
     end: date/time for the latest packets you want
    """
    compressions=["bz2", "gzip", "zip"]
    def __init__(self, source, target, *args, **kwargs):
        self.source = source
        self.target = target
        return

    def __call__(self):
        """Merges the packet files and saves them"""
        return

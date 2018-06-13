"""Get the packets"""
# this project
from .base import AlpacaBase


class GetDefaults:
    """Default Values when getting packets"""
    start = None
    end = None


class GetPackets(AlpacaBase):
    """Packet retriever"""

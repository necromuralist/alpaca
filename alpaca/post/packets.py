"""Code to help with parsing the packets"""

# python standard library
import logging
import os

# from pypi
from scapy.sendrecv import sniff

LOG_FORMAT = "%(asctime)s: %(levelname)s: (%(module)s %(funcName)s): %(message)s"

def traverse(source):
    """Generates whatever is in the source

    This is intended to help pick a spot because scapy doesn't seem to support slicing

    Args:
     source: iterable to traverse

    Yields:
     next item in the source
    """
    for item in source:
        yield item
    return


class ConfigurationError(Exception):
    """an error indicating we think something was wrong with the setup"""


class SubType:
    """Holds the frame sub-type encodings"""
    association_request = 0
    association_response = 1
    reassociation_request = 2
    reassociation_respones = 3
    probe_request = 4
    probe_response = 5
    beacon = 8
    atim = 9
    disassocaite = 10
    authentication = 11
    deauthentication = 12

    
class FrameType:
    """Holds the frame-type encodings
    
    .. note:: See `this page <https://community.cisco.com/t5/wireless-mobility-documents/802-11-frames-a-starter-guide-to-learn-wireless-sniffer-traces/ta-p/3110019>`__ for more info
    """
    management = 0
    control = 1
    data = 2
    subtype = SubType


class Handshake:
    """Constants for the 4-way handshake"""
    not_started = 0
    authentication_nonce = 1
    supplicant_nonce = 2
    group_temporal_key = 3
    acknowledgement = 4

    
class BaseThing:
    """A base-class to add common values

    Args:
     log_level: level for the logger
     log_format: string to format log messages
    """
    def __init__(self, log_level=logging.DEBUG, log_format=LOG_FORMAT):
        self.log_level = log_level
        self.log_format = log_format
        self._logger = None
        return

    @property
    def logger(self):
        "Python logger"
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(self.log_format)
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(self.log_level)            
        return self._logger


class EventTimestamp(BaseThing):
    """Event Timestamp extractor

    Args:
     client_mac: MAC-address of the client
     ap_mac: MAC-address of the access-point
     ssid: Identifier for the access-point
     log: Path to the log to parse
     last: If true, use the last instance of the packet seen
    """
    def __init__(self, client_mac, ap_mac, ssid, log, last=True, *args, **kwargs):
        super(EventTimestamp, self).__init__(*args, **kwargs)
        self.client_mac = client_mac
        self.ap_mac = ap_mac
        self.ssid = ssid
        self._log = None
        self.log = log
        self.last = last
        self._packets = None
        self._probe_request = None
        self._probe_response = None
        self._authentication_request = None
        self._authentication_response = None
        self._association_request = None
        self._association_response = None
        self._authentication_nonce = None
        self._supplicant_nonce = None
        self._group_temporal_key = None
        self._acknowledgement = None
        self.handshake_step = Handshake.not_started
        self.last_event_index = 0
        return

    @property
    def log(self):
        """The log-file path

        Returns:
         string: the path to the pcap log file
        """
        return self._log

    @log.setter
    def log(self, path):
        """Sets the log, expanding any '~/' given

        Raises:
         ConfigurationError: path to file doesn't exist
        """
        self._log = os.path.expanduser(path)
        self.logger.debug("log path: %s", self._log)
        if not os.path.isfile(self._log):
            raise ConfigurationError("{} is not a file".format(self._log))
        return

    @property
    def packets(self):
        """the packet-list

        This list is 0-indexed, but pcap is 1-indexed so they will be off by 1

        Returns:
         scapy.plist.PacketList: list-like object with packets
        """
        if self._packets is None:
            self._packets = sniff(offline=self.log)            
        return self._packets

    @property
    def probe_request(self):
        """The probe request from the client to the AP

        Returns:
         scapy.layers.dot11.RadioTap: Probe Request packet
        """
        if self._probe_request is None:
            self.logger.debug("looking for the probe request")
            for packet in self.packets:
                if all((
                        packet.addr2 == self.client_mac,
                        packet.type == FrameType.management,
                        packet.subtype == FrameType.subtype.probe_request,
                        packet.info == self.ssid,
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._probe_request = packet
                    if not self.last:
                        self.logger.debug("breaking on first packet")
                        break
        return self._probe_request

    @property
    def probe_response(self):
        """The probe response to the client
        
        Returns:
         scapy.layers.dot11.RadioTap: Probe Respones packet
        """        
        if self._probe_response is None:
            self.logger.debug("Looking for the probe response")
            for packet in self.packets:
                if all((
                        packet.addr2 == self.ap_mac,
                        packet.addr1 == self.client_mac,
                        packet.type == FrameType.management,
                        packet.subtype == FrameType.subtype.probe_response,
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._probe_response = packet
                    if not self.last:
                        self.logger.debug("Breaking on first packet")
                        break
        return self._probe_response
                
    @property
    def authentication_request(self):
        """the authentication request from the client to the AP

        Returns:
         scapy.layers.dot11.RadioTap: Authentication Request packet
        """
        if self._authentication_request is None:
            self.logger.debug("Looking for the authentication request")
            for packet in self.packets:
                if all((
                        packet.addr2 == self.client_mac,
                        packet.addr1 == self.ap_mac,
                        packet.type == FrameType.management,
                        packet.subtype == FrameType.subtype.authentication,
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._authentication_request = packet
                    if not self.last:
                        self.logger.debug("Breaking on first packet")
                        break
        return self._authentication_request

    @property
    def authentication_response(self):
        """Authentication response from the AP to the client

        Returns:
         scapy.layers.dot11.RadioTap: Authentication Response packet
        """
        if self._authentication_response is None:
            self.logger.debug("Looking for the authentication response")
            for packet in self.packets:
                if all((
                        packet.addr2 == self.ap_mac,
                        packet.addr1 == self.client_mac,
                        packet.type == FrameType.management,
                        packet.subtype == FrameType.subtype.authentication,
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._authentication_response = packet
                    if not self.last:
                        self.logger.debug("Breaking on first packet")
                        break
        return self._authentication_response

    @property
    def association_request(self):
        """Association Request from the client to the AP

        Returns:
         scapy.layers.dot11.RadioTap: Association Request packet
        """
        if self._association_request is None:
            self.logger.debug("Looking for the association request")
            for packet in self.packets:
                if all((
                        packet.addr2 == self.client_mac,
                        packet.addr1 == self.ap_mac,
                        packet.type == FrameType.management,
                        packet.subtype == FrameType.subtype.association_request,
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._association_request = packet
                    if not self.last:
                        self.logger.debug("Breaking in first packet")
                        break
        return self._association_request

    @property
    def association_response(self):
        """Association Respones for the AP to the client


        Returns:
         scapy.layers.dot11.RadioTap: Association Response packet
        """
        if self._association_response is None:
            self.logger.debug("Looking for the association response")
            for packet in self.packets:
                if all((
                        packet.addr2 == self.ap_mac,
                        packet.addr1 == self.client_mac,
                        packet.type == FrameType.management,
                        packet.subtype == FrameType.subtype.association_response,                      
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._association_response = packet
                    if not self.last:
                        self.logger.debug("Breaking on the first packet")
                        break
        return self._association_response

    @property
    def authentication_nonce(self):
        """First step in the Four-way handshake

        Returns:
         scapy.layers.dot11.RadioTap: Authentication Nonce packet
        """
        if self._authentication_nonce is None:
            self.logger.debug("Looking for the anonce packet")
            for index, packet in enumerate(self.packets):
                if all((
                        packet.addr2 == self.ap_mac,
                        packet.addr1 == self.client_mac,
                        packet.type == FrameType.control,
                        packet.subtype == FrameType.subtype.authentication,
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._authentication_nonce = packet
                    self.handshake_step = Handshake.authentication_nonce
                    self.last_event_index = index
                    break
        return self._authentication_nonce

    @property
    def supplicant_nonce(self):
        """Client's response to the authentication nonce

        Returns:
         scapy.layers.dot11.RadioTap: Supplicant Nonce Packet
        """
        if self._supplicant_nonce is None:
            self.logger.debug("Looking for the supplicant packet")
            packets = traverse(self.packets)
            for packet in range(self.last_event_index):
                _ = packets.__next__()
            for index, packet in enumerate(packets):
                if all((
                        packet.addr2 == self.client_mac,
                        packet.addr1 == self.ap_mac,
                        packet.type == FrameType.control,
                        packet.subtype == FrameType.subtype.authentication,
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._supplicant_nonce = packet
                    self.handshake_step = Handshake.supplicant_nonce
                    self.last_event_index += index + 1
                    break
        return self._supplicant_nonce

    @property
    def group_temporal_key(self):
        """AP's response to the supplicant nonce
        
        Returns:
         scapy.layers.dot11.RadioTap: Group Temporal Key
        """
        if self._group_temporal_key is None:
            self.logger.debug("Looking for the GTK")
            packets = traverse(self.packets)
            for packet in range(self.last_event_index):
                _ = packets.__next__()
            for index, packet in enumerate(packets):
                if all((
                        packet.addr2 == self.ap_mac,
                        packet.addr1 == self.client_mac,
                        packet.type == FrameType.control,
                        packet.subtype == FrameType.subtype.authentication,                        
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._group_temporal_key = packet
                    self.handshake_step = Handshake.group_temporal_key
                    self.last_event_index += index + 1
                    break
        return self._group_temporal_key

    @property
    def acknowledgement(self):
        """client acknowledgement for the gtk"""
        if self._acknowledgement is None:
            self.logger.debug("Looking for the acknowledgement")
            packets = traverse(self.packets)
            for packet in range(self.last_event_index):
                _ = packets.__next__()

            for index, packet in enumerate(packets):
                if all((
                        packet.addr2 == self.client_mac,
                        packet.addr1 == self.ap_mac,
                        packet.type == FrameType.control,
                        packet.subtype == FrameType.subtype.authentication,
                )):
                    self.logger.debug("found packet: %s", packet)
                    self._acknowledgement = packet
                    self.handshake_step += 1
                    self.last_event_index += index + 1
                    break
        return self._acknowledgement

    def __call__(self):
        """sets up the attributes

        This is meant to set the attributes in order. The reason for this
        is the four-way handshake is relying on the previous step setting the
        index for the packet it grabbed, since scapy doesn't seem
        to identify the steps in the handshake (from what I've found so far)

        It traverses the packets each time so it is inefficient
        Fix it later
        """
        self.probe_request
        self.probe_response
        self.authentication_request
        self.authentication_response
        self.association_request
        self.association_response
        self.authentication_nonce
        self.supplicant_nonce
        self.group_temporal_key
        return

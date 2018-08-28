# python standard library
import os
import re
import shlex
import subprocess

import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

# from pypi
import pandas
from pathlib import PurePath

class Data:
    """Holds folder and file strings for the data

    Args:
     data_path (str): Path to the pcap directory
     device_under_test: Identifier in the pcap file for the device of interest (client)
     access_point: Identifier in the pcap file for the access point
     tshark_command: command to convert the pcaps to text
     log_extension: just something to put at the end of the log files
     pcap_extension: file-extension to identify the capture files
    """
    def __init__(self, data_path, device_under_test, access_point,
                 tshark_command="tshark -r {}", log_extension=".log",
                 pcap_extension=".pcapng"):
        self.data_path = data_path
        self.device_under_test = device_under_test
        self.access_point = access_point
        self.log_extension = log_extension
        self._source_directory = None
        self._human_log = None
        self.pcap_extension = pcap_extension
        return

    @property
    def source_directory(self):
        """path to the pcap files"""
        return self._source_directory

    @source_directory.setter
    def source_directory(self, path):
        """sets the path after expanding the user-folder

        Args:
         path (str): path to pcap directory with ~/<path>
        """
        self._source_directory = os.path.expanduser(path)
        return

    @property
    def human_log(self):
        """base-string for the parsed logs"""
        if self._human_log is None:
            self._human_log = os.path.join(self.source_directory,
                                           (self.device_under_test
                                            + "_{:02d}"
                                            + log_extension))
        return self._human_log

class OatBran:
    """help with regular expressions"""
    zero_or_more = '*'
    one_or_more = '+'

    alternatively = "|"

    anything = '.'
    everything = anything + zero_or_more
    space = r'\s'
    spaces = space + one_or_more
    digit = r'\d'
    integer = digit + one_or_more
    decimal_point = r'\.'
    float = integer + decimal_point + integer
    group = "({})"
    named_group = '(?P<{}>{})'

INDEX = 'index'
TIMESTAMP = 'timestamp'


class Timestamp:
    """expressions to tokenize the packets
    
    Args:
     device_under_test: MAC-identifier to match the client
     access_point: MAC-identifier to match the access point
     ssid: SSID for the access point (for broadcast packets)
     index_key: Key for the named-group with the packet index
     timestamp_key: key for the named-group with the timestamp
    """
    def __init__(self, device_under_test, access_point, ssid, index_key=INDEX,
                 timestamp_key=TIMESTAMP):
        self.device_under_test = device_under_test
        self.access_point = access_point
        self.ssid = ssid
        self.index_key = index_key
        self.timestamp_key = timestamp_key
        self._count_and_timestamp = None
        self._probe_request = None
        self._association_request = None
        self._association_response = None
        self._authentication_request = None
        self._authentication_response = None
        self._eapol_message = None
        return

    @property
    def count_and_timestamp(self):
        """get the packet count and timestamp"""
        if self._count_and_timestamp is None:
            self._count_and_timestamp = (
                OatBran.named_group.format(self.index_key, OatBran.integer)
                + OatBran.space
                + OatBran.named_group.format(self.timestamp_key, OatBran.float)
                + OatBran.spaces
            )
        return self._count_and_timestamp

    @property
    def probe_request(self):
        """Regex to match probe requests from the DUT to the AP"""
        if self._probe_request is None:
            self._probe_request = re.compile(
                self.count_and_timestamp
                + OatBran.group.format(
                OatBran.group.format(
                self.device_under_test
                + OatBran.everything
                + self.access_point
                + OatBran.everything
                + "Probe Request"
                )
                + OatBran.alternatively
                + OatBran.group.format(
                self.device_under_test
                + OatBran.everything
                + "Probe Request"
                + OatBran.everything
                + "SSID={}".format(self.ssid)
                ))
            )
        return self._probe_request

    @property
    def association_request(self):
        """Regex to match the assoociation request from the DUT"""
        if self._association_request is None:
            self._association_request = re.compile(
                self.count_and_timestamp
                + self.device_under_test
                + OatBran.everything
                + self.access_point
                + OatBran.everything
                + "Association Request")
        return self._association_request

    @property
    def association_response(self):
        """Regex to match the association response from the AP"""
        if self._association_response is None:
            self._association_response = re.compile(
                self.count_and_timestamp
                + self.access_point
                + OatBran.everything
                + self.device_under_test
                + OatBran.everything
                + "Association Response")
        return self._association_response

    @property
    def authentication_request(self):
        """Regex to match the authentication request from the DUT"""
        if self._authentication_request is None:
            self._authentication_request = re.compile(
                self.count_and_timestamp
                + self.device_under_test
                + OatBran.everything
                + self.access_point
                + OatBran.everything
                + "Authentication"
            )
        return self._authentication_request

    @property
    def authentication_response(self):
        """Regex to match the authentication response from the AP"""
        if self._authentication_response is None:
            self._authentication_response = re.compile(
                self.count_and_timestamp
                + self.access_point
                + OatBran.everything
                + self.device_under_test
                + OatBran.everything
                + "Authentication"
            )
        return self._authentication_response

    @property
    def eapol_message(self):
        """Regex to match an EAPOL message"""
        if self._eapol_message is None:
            self._eapol_message = re.compile(
                self.count_and_timestamp
            )
        return self._eapol_message

class PcapToHuman:
    """converts the pcap files to something the regular expressions can read
    
    Args:
     data: a Data object with file information
    """
    def __init__(self, data):
        self.data = data
        return

    def __call__(self):
        """Parses the data files"""
        pcaps = sorted(name for name in os.listdir(self.data.source_directory)
                       if name.endswith(self.data.pcap_extension))

    for index, pcap in enumerate(pcaps):
        source = PurePath(os.path.join(self.data.source_directory, pcap))

        target = PurePath(os.path.join(self.data.source_directory,
                                       self.data.human_log.format(index + 1)))
        if not os.path.isfile(target):
            command = shlex.split(self.data.tshark_command.format(source))
            outcome = subprocess.run(command, check=True, stdout=subprocess.PIPE,
                                     universal_newlines=True)
            with open(target, "w") as writer:
                writer.write(outcome.stdout)

class EventTimes:
    """Grabs the times from the first probe request

    Args:
     timestamp: timestamp object setup with the MAC addressess and SSID
     log: path to the log file to grab the values from
    """
    columns=["ProbeRequest",
    "AssociationRequest",
    "AssociationResponse",
    "AuthenticationRequest",
    "AuthenticationResponse"]

    def __init__(self, timestamp, log):
        self.timestamp = timestamp
        self.log = log
        self._probe_request = None
        self._association_request = None
        self._association_response = None
        self._authentication_request = None
        self._authentication_response = None
        return

    @property
    def probe_request(self):
        return self._probe_request

    @probe_request.setter
    def probe_request(self, line):
        """parses the line and sets the probe request if it matches"""
        self._probe_request = self.check_line(line,
                                              self.timestamp.probe_request,
                                              self._probe_request)
        return

    @property
    def association_request(self):
        return self._association_request

    @association_request.setter
    def association_request(self, line):
        self._association_request = self.check_line(line,
                                                    self.timestamp.association_request,
                                                    self._association_request)
        return

    @property
    def association_response(self):
        return self._association_response

    @association_response.setter
    def association_response(self, line):
        self._association_response = self.check_line(line,
                                                     self.timestamp.association_response,
                                                     self._association_response)
        return

    @property
    def authentication_request(self):
        return self._authentication_request

    @authentication_request.setter
    def authentication_request(self, line):
        self._authentication_request = self.check_line(line,
                                                       self.timestamp.authentication_request,
                                                       self._authentication_request)
        return

    @property
    def authentication_response(self):
        return self._authentication_response

    @authentication_response.setter
    def authentication_response(self, line):
        self._authentication_response = self.check_line(line,
                                                        self.timestamp.authentication_response,
                                                        self._authentication_response)
        return

    @property
    def time_to_association_request(self):
        return self.subtract_probe(self.association_request)

    @property
    def time_to_association_response(self):
        return self.subtract_probe(self.association_response)

    @property
    def time_to_authentication_request(self):
        return self.subtract_probe(self.authentication_request)

    @property
    def time_to_authentication_response(self):
        return self.subtract_probe(self.authentication_response)

    @property
    def all_matched(self):
        """checks if all the properties are set"""
        return all((self.probe_request is not None,
                    self.association_request is not None,
                    self.association_response is not None,
                    self.authentication_request is not None,
                    self.authentication_response is not None))

    def subtract_probe(self, minuend):
        """returns minuend - probe-request time"""
        try:
            return minuend - self.probe_request
        except TypeError:
            pass
    

    def check_line(self, line, regex, default=None):
        """try to parse the timestamp

        Args:
         line (str): line to parse
         regex (Re): compiled regular expression
         default: what to return if it doesn't match

        Returns:
         float or None: timestamp if found otherwise None
        """
        match = regex.search(line)
        if match:
            return float(match.group(Timestamp.key))
        return default

    def set(self, line):
        """tries to set the line to all the attributes"""
        self.probe_request = line
        self.association_request = line
        self.association_response = line
        self.authentication_request = line
        self.authentication_response = line
        return

    def __call__(self):
        """Process the lines in the log

        Returns:
         list: list with the processed columns
        """
        with open(self.log) as lines:
            for line in lines:
                self.set(line)
                if self..all_matched:
                    break
        return [
            self.probe_request,
            self.time_to_association_request,
            self.time_to_association_response,
            self.time_to_authentication_request,
            self.time_to_authentication_response]

class LogProcessor:
    """Get the event times for the human-readable logs

    Args:
     data: data object that has the strings for the files
     timestamp: Timestamp object to parse the lines

    Returns:
     DataFrame: Pandas DataFrame with event times
    """
    def __init__(self, data, timestamp):
        self.data = data
        self.timestamp = timestamp
        self._parsed = None
        self._data_frame = None
        return

    @property
    def parsed(self):
        """the list of times
        
        Returns:
         list: lists of time information
        """
        if self._parsed is None:
            logs = sorted(name for name in os.listdir(
                self.data.source_directory) 
                          if name.endswith(self.data.log_extension))

            self._parsed = []
            for log in logs:
                events = EventTimes(self.timestamp, log)
                self._parsed.append(events())
        return self._parsed

    @property
    def data_frame(self):
        """DataFrame with the parsed lines"""
        if self._data_frame is None:
            self._data_frame = pandas.DataFrame(self.parsed,
                                                EventTimes.colmuns)
        return self._data_frame

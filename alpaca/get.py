"""Get the packets"""
# python standard library
from pathlib import Path
import os
import re
import shlex
import subprocess

# pypi
import dateparser

# this project
from .base import AlpacaBase
from .errors import ConfigurationError


class GetDefaults:
    """Default Values when getting packets"""
    start = '0'
    end = '9999'
    compression = "gzip"
    glob = "*"
    info_command = "capinfos -ae"

class GetPackets(AlpacaBase):
    """Packet retriever

    This gets the packets and assembles them into a single file

    Args:
     source: path to the directory with the PCAP files
     target: name of file to store the packets
     start: date/time for the earliest packet
     end: date/time for the latest packets you want
     source_glob: file-glob to match files in source directory

    Raises:
     ConfigurationError: any of the arguments are invalid
    """
    compressions=["bz2", "gzip", "zip"]
    def __init__(self, source, target,
                 start=GetDefaults.start,
                 end=GetDefaults.end,
                 source_glob=GetDefaults.glob,
                 *args, **kwargs):
        super(GetPackets, self).__init__(*args, **kwargs)
        self._source = None
        self.source = source
        self._target = None
        self.target = target
        self._start = None
        self.start = start
        self._end = None
        self.end = end
        self.source_glob = source_glob
        self._filterer = None
        self._merger = None
        return

    @property
    def start(self):
        """the start time

        Returns:
         datetime: the start datetime
        """
        return self._start

    @start.setter
    def start(self, timestamp):
        """converts the timestamp to a datetime

        Args:
         timestamp (str): time-stamp of starting packets

        Raises:
         ConfigurationError: Unable to parse the source
        """
        self._start = timestamp
        if self._start is not None:
            try:
                self._start = dateparser.parse(self._start)
            except TypeError as error:
                message = "Non-string start time: {}".format(timestamp)
                self.logger.error(error)
                self.logger.error(message)
                raise ConfigurationError(message)
            if self._start is None:
                message = "Un-parseable start time: %s".format(timestamp)
                self.logger.error(message)
                raise ConfigurationError(message)
        self.logger.debug("Start Time: %s", self._start)            
        return

    @property
    def end(self):
        """Time of last packets to get

        Returns:
         datetime: the end datetime
        """
        return self._end

    @end.setter
    def end(self, timestamp):
        """Sets the end time

        .. warning:: dateparser sometimes converts three-letter strings to 
           date-times, don't rely on it to detect garbage all the time

        Args:
         timestamp (str): time to parse (or None)

        Raises:
         ConfiguarationError: bad end source
        """
        self._end = timestamp
        if self._end is not None:
            try:
                self._end = dateparser.parse(self._end)
            except TypeError as error:
                message = "Non-String end-time: {}".format(timestamp)
                self.logger.error(error)
                self.logger.error(message)
                raise ConfigurationError(message)
            if self._end is None:
                message = "Un-parseable end: {}".format(self._end)
                self.logger.error(message)
                raise ConfigurationError(message)
        self.logger.debug("End Time: %s", timestamp)
        return

    @property
    def filterer(self):
        """File filterer for the packets"""
        if self._filterer is None:
            self._filterer = FileFilterer(self.source, self.source_glob,
                                          self.start,
                                          self.end)
        return self._filterer

    @property
    def merger(self):
        """File Merger"""
        if self._merger is None:
            self._merger = Merger(self.filterer.file_names,
                                  self.target)
        return self._merger

    def __call__(self):
        """Merges the packet files and saves them"""
        self.merger()
        return

    def check_rep(self):
        """checks the arguments passed in

        Raises: 
         AssertionError: some argument was funky
        """
        return


class FileFilterer(AlpacaBase):
    """Filters out the file names by time

    Args:
     path (directory): directory where the files are stored
     glob (str): file-glob to match the files
     start (DateTime): start time to filter out early packets
     end (DateTime): end time to filter out later packets
    """
    def __init__(self, path, glob, start=None, end=None,
                 *args, **kwargs):
        super(FileFilterer, self).__init__(*args, **kwargs)
        self._path = None        
        self.path = path
        self.glob = glob
        self.start = start
        self.end = end
        self._file_names = None
        return

    @property
    def path(self):
        """Path object"""
        return self._path

    @path.setter
    def path(self, directory):
        """Sets the source path object
        
        Args:
         directory (str): directory path

        Raises:
         ConfigurationError: invalid source directory
        """
        try:
            self._path = Path(directory)
        except TypeError as error:
            self.logger.error(error)
            message = "Source Directory not a string: {}".format(directory)
            self.logger.error(message)
            raise ConfigurationError(message)
        if not self._path.exists():
            raise ConfigurationError("Source Directory doesn't exist: {}".format(directory))
        if not self._path.is_dir():
            raise ConfigurationError("Source isn't a directory: {}".format(directory))
        return

    @property
    def all_files(self):
        """All the files in the directory

        Returns:
         iter: iterable of CaptureInfo files that match the glob in the path
        """
        return (CaptureInfo(str(path)) for path in self.path.glob(self.glob))

    @property
    def file_names(self):
        """list of file-names to use

        Returns:
         list: file-names within the time-span
        """
        if self._file_names is None:
            captures = self.all_files
            if self.start is not None:
                captures = (capture for capture in captures if capture >= self.start)
            if self.end is not None:
                captures = (capture for capture in captures if capture <= self.end)
            self._file_names = [capture.path for capture in captures]
        return self._file_names


    def check_rep(self):
        """checks that the arguments passed in are okay

        Raises:
         AssertionError: some argument was invalid
        """
        return

class Info:
    first_key = 'first'
    last_key = 'last'
    first_regex = "First packet time:\s+(?P<{}>.+)".format(first_key)
    last_regex = "Last packet time:\s+(?P<{}>.+)".format(last_key)
    
class CaptureInfo(AlpacaBase):
    """Holds the basic info for a PCAP file

    Args:
     path (str): path to file
     command (str): command to get the info
    """
    first_key = "first"
    last_key = "last"
    def __init__(self, path, command=GetDefaults.info_command, *args, **kwargs):
        super(CaptureInfo, self).__init__(*args, **kwargs)
        self.path = path
        self.command = command
        self._first = None
        self._last = None
        self._first_regex = None
        self._last_regex = None
        self._output = None
        return

    @property
    def output(self):
        """output of the command

        .. warning:: this runs the command in a sub-process

        Raises:
         subprocess.CalledProcessError: command exited abnormally
        """
        if self._output is None:
            command = "{} {}".format(self.command, self.path)
            self.logger.debug("Running: '%s'", command)
            outcome = subprocess.run(shlex.split(command),
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     universal_newlines=True,
            )
            self._output = outcome.stdout
            self.logger.debug(self._output)
        return self._output

    @property
    def first_regex(self):
        """Regular expression to get the first packet time"""
        if self._first_regex is None:
            self._first_regex = re.compile(Info.first_regex)
        return self._first_regex

    @property
    def last_regex(self):
        """regular expression to get the last packet time"""
        if self._last_regex is None:
            self._last_regex = re.compile(Info.last_regex)
        return self._last_regex

    
    @property
    def first(self):
        """Datetime for the first packet"""
        if self._first is None:
            match = self.first_regex.search(self.output)
            if match is None:
                raise RuntimeError(
                    "{} didn't match the first timestamp".format(self.command))
            self._first = dateparser.parse(match.groupdict()[Info.first_key])
        return self._first

    @property
    def last(self):
        """datetime for the last packet"""
        if self._last is None:
            match = self.last_regex.search(self.output)
            if match is None:
                raise RuntimeError(
                    "{} didn't match the last timestamp".format(self.command))
            self._last = dateparser.parse(match.groupdict()[Info.last_key])
        return self._last

    def __lt__(self, other):
        """less than comparison

        Args:
         other (DateTime): time to compare to last timestamp

        Returns:
         bool: True if self.last < other
        """
        return self.last < other

    def __le__(self, other):
        """<= comparison

        Args:
         other (DateTime): time to compare to last timestamp
        Returns:
         bool: True if self.last <= other
        """
        return self.last <= other

    def __gt__(self, other):
        """> comparison

        Args:
         other (DateTime): time to compare to first timestamp

        Returns:
         bool: True if self.first > other
        """
        return self.first > other

    def __ge__(self, other):
        """>= comparison

        Args:
         other (DateTime): time to compare to first timestamp

        Returns:
         bool: True if self.first >= other
        """
        return self.first >= other

    def check_rep(self):
        """Checks that the arguments passed in are okay

        Raises:
         AssertionError: some argument was wrong
        """
        return


class Merger(AlpacaBase):
    """Merge the packets

    Args:
     files (list): list of packet files
     target (str): place to store the files
    """
    def __init__(self, files, target, *args, **kwargs):
        super(Merger, self).__init__(*args, **kwargs)
        self.files = files
        self._target = None
        self.target = target
        self._command = None
        return

    @property
    def command(self):
        """merge command"""
        if self._command is None:
            self._command = shlex.split("mergecap -w {} {}".format(
                self.target,
                " ".join(self.files)))
        return self._command

    @property
    def target(self):
        """name of file to save the merged packets in"""
        return self._target

    @target.setter
    def target(self, file_name):
        """sets the target file name

        Args:
         file_name(str): path to target file
        """
        path = Path(file_name)
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        self._target = path
        return

    def check_rep(self):
        """Checks the arguments

        Raises:
         AssertionError: some argument doesn't smell right
        """
        return

    def __call__(self):
        output = subprocess.run(self.command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        self.logger.debug(output.stdout)
        return



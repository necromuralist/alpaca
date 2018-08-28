"""Base classes for project ALPaca"""

# python standard library
from abc import (
    ABC,
    abstractmethod,
    )
from logging.config import dictConfig
import logging

class AlpacaBase(ABC):
    """Base class for most things ALPaCa"""
    def __init__(self):
        self._logging_configuration = None
        self._logger = None
        return

    @property
    def logging_configuration(self):
        """dictionary of logging values"""
        if self._logging_configuration is None:
            self._logging_configuration = dict(
                version = 1,
                formatters = {
                    'f': {'format':
                          '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
                },
                handlers = {
                    'h': {'class': 'logging.StreamHandler',
                          'formatter': 'f',
                          'level': logging.DEBUG}
                },
                root = {
                    'handlers': ['h'],
                    'level': logging.DEBUG,
                },
            )
        return self._logging_configuration

    @property
    def logger(self):
        """a python logger"""
        if self._logger is None:
            dictConfig(self.logging_configuration)
            self._logger = logging.getLogger()
        return self._logger

    @abstractmethod
    def check_rep(self):
        """Checks that the attributes are set correctly

        Raises:
         AssertionError: Something is set wrong
        """
        return

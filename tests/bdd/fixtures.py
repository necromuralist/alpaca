# from pypi
from pytest import fixture

class Katamari:
    """Something to stick objects into"""


@fixture
def katamari():
    """creates and returns the katamari object"""
    k = Katamari()
    return k

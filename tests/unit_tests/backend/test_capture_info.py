# coding=utf-8
"""Capture Info helper feature tests."""
# python standard library
from functools import partial

# from pypi
from expects import (
    equal,
    expect,
)
from pytest_bdd import (
    given,
    then,
    when,
)
import pytest_bdd
import dateparser

# for testing
from ..fixtures import katamari

from .samples import (
    OUTPUT,
    FIRST_TIME,
    LAST_TIME,
)

# software under test
from packets.get import CaptureInfo

scenario = partial(pytest_bdd.scenario, '../../features/backend/capture_info.feature')


def build_arguments(path="/tmp"):
    """builds the arguments for the CaptureInfo

    Args:
     path (str): path to the file
    
    Returns:
     dict: arguments to build the Capture Info
    """
    return dict(path=path)

# ******************** constructor ******************** #

@scenario('The CaptureInfo is built')
def test_given_the_captureinfo_is_built():
    return


@given('The CaptureInfo is built')
def test_the_captureinfo_is_built(katamari):
    katamari.arguments = build_arguments()
    katamari.expected = list(katamari.arguments.values())
    katamari.info = CaptureInfo(**katamari.arguments)
    return


@when('the attributes are checked')
def the_attributes_are_checked(katamari):
    katamari.attributes = [getattr(katamari.info, attribute) for attribute in katamari.arguments]


@then('they are the expected attributes')
def they_are_the_expected_attributes(katamari):
    expect(katamari.attributes).to(equal(katamari.expected))
    return

# ******************** first Timestamp ******************** #


@scenario("The first timestamp is grabbed")
def test_first_timestamp():
    return

#  Given The CaptureInfo is built


@when("the first timestamp is grabbed")
def get_first_timestamp(katamari):
    katamari.info._output = OUTPUT
    katamari.actual = katamari.info.first
    katamari.expected = dateparser.parse(FIRST_TIME)
    return


@then("it is the correct timestamp")
def check_timestamp(katamari):
    expect(katamari.actual).to(equal(katamari.expected))
    return

# ******************** last timestamp ******************** #


@scenario("The last timestamp is grabbed")
def test_last_timestamp():
    return

#  Given The CaptureInfo is built

@when("the last timestamp is grabbed")
def get_last_timestamp(katamari):
    katamari.info._output = OUTPUT
    katamari.actual = katamari.info.last
    katamari.expected = dateparser.parse(LAST_TIME)
    return
#  Then it is the correct timestamp

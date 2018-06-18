# coding=utf-8
"""A packet retriever feature tests."""
# python standard library
from datetime import datetime
from functools import partial
from pathlib import Path
import random

# from pypi
import dateparser

from expects import (
    be_a,
    equal,
    expect,
    raise_error,
)
from pytest_bdd import (
    given,
    then,
    when,
)
import pytest_bdd

# test-help
from ..fixtures import katamari

# software under test
from packets.get import GetPackets
from packets.errors import ConfigurationError

And = when
scenario = partial(pytest_bdd.scenario, '../../features/backend/get_packets.feature')

def base_arguments(source="/tmp", target="/tmp", start=None, end=None, glob="*"):
    """Builds the base arguments dictionary

    Args:
     source (str): the source directory of the packets
     target (str): the target directory for the output
     start (str): the time for the earliest packets
     end (str): the time for the latest packets
     glob (str): file-glob for the source files

    Returns:
     dict: arguments for the GetPackets Constructor
    """    
    return dict(source=source,
                target=target,
                start=start,
                end=end,
                source_glob=glob)
    
# ******************** constructor ******************** #
@scenario('The user builds a GetPackets object')
def test_the_user_builds_a_getpackets_object():
    return


@given('valid arguments')
def valid_arguments(katamari):
    katamari.arguments = base_arguments()
    return


@when('the user builds the GetPackets object')
def the_user_build_the_getpackets_object(katamari, faker, mocker):
    katamari.getter = GetPackets(**katamari.arguments)
    return


@then('the Get Packets object has the expected attributes')
def the_get_packets_object_has_the_expected_attributes(katamari):
    expect(katamari.getter.source).to(equal(katamari.arguments["source"]))
    expect(katamari.getter.target).to(equal(katamari.arguments["target"]))
    return


# ******************** call ******************** #


@scenario("The user calls the GetPackets object")
def test_call():
    return

#  Given valid arguments
#  When the user builds the GetPackets object

@And("calls the GetPackets object")
def call_get_packets(katamari, mocker):
    katamari.merger = mocker.MagicMock()
    katamari.getter._merger = katamari.merger
    katamari.getter()
    return


@then("the GetPackets object performs the expected steps")
def check_call(katamari):
    katamari.merger.assert_called_once_with()
    return

# ******************** start time ******************** #


@scenario("The user passes in the start time")
def test_start_time():
    return


@given("arguments with the start time")
def set_start_time(katamari,faker):
    days_ago = random.randint(1, 99)
    katamari.start = faker.past_datetime(start_date="-{}d".format(days_ago))
    katamari.arguments = base_arguments(start=str(katamari.start))
    return

#  When the user builds the GetPackets object


@then("the GetPackets object has the correct start time")
def check_start_time(katamari):
    expect(katamari.getter.start).to(be_a(datetime))
    expect(katamari.getter.start).to(equal(katamari.start))
    return

# ********** bad start time ********** #


@scenario("The user passes in an invalid start time")
def test_bad_start():
    return


@given("arguments with a bad start time")
def set_bad_start(katamari):
    katamari.arguments = base_arguments(start="aoeu")
    return


@when("the user builds the bad GetPackets object")
def build_bad_object(katamari):
    def bad_call():
        GetPackets(**katamari.arguments)
        return
    katamari.bad_call = bad_call
    return


@then("a ConfigurationError is raised")
def check_error(katamari):
    expect(katamari.bad_call).to(raise_error(ConfigurationError))
    return

# ********** non-string ********** #


@scenario("The user passes in a non-string start time")
def test_non_string_start():
    return
        

@given("arguments with a non-string start time")
def setup_non_string_start(katamari):
    katamari.arguments = base_arguments(start=random.randint(1, 99))
    return

#  When the user builds the bad GetPackets object
#  Then a ConfigurationError is raised

# ******************** end time ******************** #


@scenario("The user passes in the end time")
def test_end_time():
    return


@given("arguments with the end time")
def set_end_time(katamari, faker):
    days_ago = random.randint(1, 99)
    katamari.end = faker.past_datetime(start_date="-{}d".format(days_ago))
    katamari.arguments = base_arguments(end=str(katamari.end))
    return

#  When the user builds the GetPackets object

@then("the GetPackets object has the correct end time")
def check_end_time(katamari):
    expect(katamari.getter.end).to(equal(katamari.end))
    return

# ********** un-parseable ********** #


@scenario("The user passes in an invalid end time")
def test_bad_end():
    return


@given("arguments with a bad end time")
def setup_bad_end(katamari, faker):
    katamari.arguments = base_arguments(end=faker.text())
    return

#  When the user builds the bad GetPackets object
#  Then a ConfigurationError is raised

# ********** non-string ********** #

@scenario("The user passes in a non-string end time")
def test_non_string_end():
    return


@given("arguments with a non-string end time")
def setup_non_string_end(katamari):
    katamari.arguments = base_arguments(end=random.randrange(55))
    return

#  When the user builds the bad GetPackets object
#  Then a ConfigurationError is raised

# ******************** path glob ******************** #


@scenario("The user passes in a glob")
def test_source_glob():
    return
          

@given("arguments with a source glob")
def setup_source_glob(katamari, faker):
    katamari.glob = "{}*".format(faker.word())
    katamari.arguments = base_arguments(glob=katamari.glob)
    katamari.expected = dict(source_glob=katamari.glob)
    return

#  When the user builds the GetPackets object


@then("the GetPackets object has the expected values")
def check_get_packets_values(katamari):
    for attribute, expected in katamari.expected.items():
        expect(getattr(katamari.getter, attribute)).to(equal(expected))
    return

# coding=utf-8
"""A packet retriever feature tests."""
# python standard library
from functools import partial

# testing
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

# test-help
from ..fixtures import katamari

# software under test
from packets.get import GetPackets

And = when
scenario = partial(pytest_bdd.scenario, '../../features/backend/get_packets.feature')

# ******************** constructor ******************** #
@scenario('The user builds a GetPackets object')
def test_the_user_builds_a_getpackets_object():
    return


@given('valid arguments')
def valid_arguments(katamari):
    katamari.arguments = dict(source="/tmp",
                              target="/tmp")
    return


@when('the user builds the GetPackets object')
def the_user_build_the_getpackets_object(katamari, faker, mocker):
    katamari.source = faker.unix_partition()
    katamari.target = faker.unix_partition()
    fake_os = mocker.MagicMock()
    mocker.patch("packets.get.os", fake_os)
    fake_os.path.exists.return_value = True
    fake_os.path.isdir.return_value = True
    
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
def call_get_packets(katamari):
    katamari.getter()
    return


@then("the GetPackets object performs the expected steps")
def check_call(katamari):
    return

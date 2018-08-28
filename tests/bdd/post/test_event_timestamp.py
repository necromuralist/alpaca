# coding=utf-8
"""A WiFi packet event timestamp extractor feature tests."""
# python standard library
from functools import partial
from unittest import mock

import copy
import random

# from pypi
from expects import (
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

# this testing

from ..fixtures import katamari  # noqa: F401

# software under test
from alpaca.post.packets import (
    ConfigurationError,
    EventTimestamp,
)

And = when
scenario = partial(pytest_bdd.scenario,
                   '../../features/event_timestamp.feature')
MANAGEMENT = 0
PROBE_REQUEST, PROBE_RESPONSE = 4, 5
AUTHENTICATION_REQUEST = AUTHENTICATION_RESPONSE = 11
ASSOCIATION_REQUEST, ASSOCIATION_RESPONSE = 0, 1
NOT_STARTED = 0

# ******************** Constructor ******************** #


@scenario('A Packet Event Timestamper is created')
def test_a_packet_event_timestamper_is_created():
    return


@given('a set of settings for the event timestamper')  # noqa: F811
@given("a group of settings with a non-existent log-file")
def a_set_of_settings_for_the_event_timestamper(katamari, faker):
    katamari.client_mac = faker.mac_address()
    katamari.ap_mac = faker.mac_address()
    katamari.ssid = faker.word()
    # the constructor checks that the log is a real file so don't fake it here
    katamari.log = "/bin/ls"
    katamari.last = faker.pybool()
    return


@when('the timestamper is built')  # noqa: F811
def the_timestamper_is_built(katamari):
    katamari.timestamper = EventTimestamp(client_mac=katamari.client_mac,
                                          ap_mac=katamari.ap_mac,
                                          ssid=katamari.ssid,
                                          log=katamari.log,
                                          last=katamari.last)
    return


@then('the timestamper has the expected settings')  # noqa: F811
def the_timestamper_has_the_expected_settings(katamari):
    expect(katamari.timestamper.client_mac).to(equal(katamari.client_mac))
    expect(katamari.timestamper.ap_mac).to(equal(katamari.ap_mac))
    expect(katamari.timestamper.ssid).to(equal(katamari.ssid))
    expect(katamari.timestamper.last).to(equal(katamari.last))
    expect(katamari.timestamper.log).to(equal(katamari.log))
    expect(katamari.timestamper.handshake_step).to(equal(NOT_STARTED))
    return

# ******************** Bad log-file ******************** #


@scenario("The user gives a non-existent log-path")
def test_bad_log_file():
    return


# @given("a group of settings with a non-existent log-file")  # noqa: F811


@when("the Timestamper is built with the bad settings")  # noqa: F811
def setup_bad_call(katamari, mocker):
    os_mock = mocker.MagicMock()
    os_mock.path.isfile.return_value = False
    mocker.patch("alpaca.post.packets.os", os_mock)

    def bad_call():
        EventTimestamp(client_mac=katamari.client_mac,
                       ap_mac=katamari.ap_mac,
                       ssid=katamari.ssid,
                       log=katamari.log,
                       last=katamari.last)
    katamari.bad_call = bad_call
    return


@then("a Configuration Error is raised")  # noqa: F811
def check_bad_call(katamari):
    expect(katamari.bad_call).to(raise_error(ConfigurationError))
    return

# ******************** check packets ******************** #


@scenario("The packets are checked by the user")
def test_packets():
    return

#  Given a set of settings for the event timestamper
#  When the timestamper is built


@And("the packets are retrieved by the user")  # noqa: F811
def get_packets(katamari, mocker):
    katamari.sniff_mock = mocker.MagicMock()
    mocker.patch("alpaca.post.packets.sniff", katamari.sniff_mock)
    katamari.packets = katamari.timestamper.packets
    return


@then("scapy.sniff is called")  # noqa: F811
def check_scapy_call(katamari):
    katamari.sniff_mock.assert_called_once_with(
        offline=katamari.log)
    return

# ******************** Probe Request ******************** #


@scenario("The Client sends a probe request to the AP")
def test_probe_request():
    return

#  Given a set of settings for the event timestamper
#  When the timestamper is built


def build_mock_packet(sender, receiver, frame_type, sub_type, previous_time):
    """Builds up the mock scapy packet

    This will increment the time a random amount from the previous time

    Args:
     sender: MAC address of the interface that sent the packet
     receiver: MAC address of the interface that the packet was sent to
     frame_type: 802.11 frame type
     sub_type: 802.11 frame sub-type
     previous_time: ctime for the previous packet

    Returns:
     MagicMock: mocked packet
    """
    packet = mock.MagicMock()
    packet.addr2 = sender
    packet.addr1 = receiver
    packet.type = frame_type
    packet.subtype = sub_type
    packet.time = previous_time + random.uniform(1, 10)
    return packet


@And("the packets are set up")  # noqa: F811
def setup_packets(katamari, mocker):
    katamari.probe_request = build_mock_packet(
        katamari.client_mac,
        None,
        MANAGEMENT,
        PROBE_REQUEST,
        0)
    katamari.probe_request.info = katamari.ssid

    katamari.probe_request2 = copy.copy(katamari.probe_request)
    katamari.probe_request2.time += random.uniform(1, 10)

    katamari.probe_response = build_mock_packet(
        katamari.ap_mac,
        katamari.client_mac,
        MANAGEMENT,
        PROBE_RESPONSE,
        katamari.probe_request2.time)

    katamari.authentication_request = build_mock_packet(
        katamari.client_mac,
        katamari.ap_mac,
        MANAGEMENT,
        AUTHENTICATION_REQUEST,
        katamari.probe_request2.time)

    katamari.authentication_response = build_mock_packet(
        katamari.ap_mac,
        katamari.client_mac,
        MANAGEMENT,
        AUTHENTICATION_RESPONSE,
        katamari.authentication_request.time,
    )

    katamari.association_request = build_mock_packet(
        katamari.client_mac,
        katamari.ap_mac,
        MANAGEMENT,
        ASSOCIATION_REQUEST,
        katamari.authentication_response.time,
    )

    katamari.association_response = build_mock_packet(
        katamari.ap_mac,
        katamari.client_mac,
        MANAGEMENT,
        ASSOCIATION_RESPONSE,
        katamari.association_request.time,
    )

    katamari.timestamper._packets = [katamari.probe_request,
                                     katamari.probe_request2,
                                     katamari.probe_response,
                                     katamari.authentication_request,
                                     katamari.authentication_response,
                                     katamari.association_request,
                                     katamari.association_response]
    return


@And("the last probe request is retrieved")  # noqa: F811
def get_the_probe_request(katamari):
    katamari.timestamper.last = True
    katamari.actual = katamari.timestamper.probe_request.time
    katamari.expected = katamari.probe_request2.time
    return


@then("it has the expected timestamp")  # noqa: F811
def check_timestamp(katamari):
    expect(katamari.actual).to(equal(katamari.expected))
    return

# ******************** Probe Response ******************** #


@scenario("The AP sends a probe response to the Client")
def test_get_probe_response():
    return

#  Given a set of settings for the event timestamper
#  When the timestamper is built
#  And the packets are set up


@And("the probe response is retrieved")  # noqa: F811
def get_probe_response(katamari):
    katamari.actual = katamari.timestamper.probe_response.time
    katamari.expected = katamari.probe_response.time
    return

#  Then it has the expected timestamp

# ******************** Authentication Request ******************** #


@scenario("The client sends an authentication request to the AP")
def test_authentication_request():
    return

#  Given a set of settings for the event timestamper
#  When the timestamper is built
#  And the packets are set up


@And("the authentication request is retrieved")  # noqa: F811
def check_authentication_request(katamari):
    katamari.expected = katamari.authentication_request.time
    katamari.actual = katamari.timestamper.authentication_request.time
    return


#  Then it has the expected timestamp


# ******************** Authentication Response ******************** #


@scenario("The AP sends an authentication response to the client")
def test_authentication_response():
    return

#  Given a set of settings for the event timestamper
#  When the timestamper is built
#  And the packets are set up


@And("the authentication response is retrieved")  # noqa: F811
def get_authentication_response(katamari):
    katamari.expected = katamari.authentication_response.time
    katamari.actual = katamari.timestamper.authentication_response.time
    return

#  Then it has the expected timestamp

# ******************** Association Request ******************** #


@scenario("The Client sends an association request to the AP")
def test_association_request():
    return

#  Given a set of settings for the event timestamper
#  When the timestamper is built
#  And the packets are set up


@And("the association request is retrieved")  # noqa: F811
def get_association_response(katamari):
    katamari.expected = katamari.association_request.time
    katamari.actual = katamari.timestamper.association_request.time
    return

#  Then it has the expected timestamp

# ******************** Association Response ******************* #


@scenario("The AP sends an association response to the Client")
def test_association_response():
    return

#  Given a set of settings for the event timestamper
#  When the timestamp is built
#  And the packets are set up


@And("the association response is retrieved")  # noqa: F811
def get_association_response(katamari):
    katamari.actual = katamari.timestamper.association_response.time
    katamari.expected = katamari.association_response.time
    return

#    Then it has the expected timestamp

# ******************** Four-Way WPA Handshake ******************** #

# ********** step one ********** #


@scenario("The AP starts the four-way handshake")
def test_start_of_handshake():
    return

#  Given a set of settings for the event timestamper
#  When the timestamper is built
#  And the packets are set up


@And("the start of the handshake is in the packets")
def add_anonce_packet(katamari):
    return


@And("the authentication nonce is retrieved")
def get_anonce(katamari):
    katamari.actual = katamari.timestamper.authentication_nonce
    return

#  Then it has the expected timestamp
#  And the timestamper's step attribute is correct

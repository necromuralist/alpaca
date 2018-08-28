# coding=utf-8
"""A Root ``packets`` command feature tests."""
# python standard library
from functools import partial

# from pypi
from click.testing import CliRunner
from expects import (
    equal,
    expect,
    start_with,
    )

from pytest_bdd import (
    given,
    then,
    when,
)
import pytest_bdd

# testing help
from ..fixtures import katamari
from .common import (
    ExitCode,
    Option,
    )

# software under test
from alpaca.main import main

scenario = partial(pytest_bdd.scenario, '../../features/cli/root_packets_command.feature')

# ******************** no arguments ******************** #

@scenario('The user calls the ``packets`` command with no arguments')
def test_the_user_calls_the_packets_command_with_no_arguments():
    return


@given('a click runner')
def a_click_runner(katamari):
    katamari.runner = CliRunner()
    return


@when('the user calls ``packets`` with no arguments')
def the_user_calls_packets_with_no_arguments(katamari):
    katamari.result = katamari.runner.invoke(main)
    return


@then('the packets command outputs a help string')
def the_packets_command_outputs_a_help_string(katamari):
    expect(katamari.result.exit_code).to(equal(ExitCode.okay))
    expect(katamari.result.output).to(start_with("Usage:"))
    return

# ******************** help ******************** #

@scenario("The user calls the ``packets`` command with the short help argument")
def test_short_help():
    return

#  Given a click runner


@when("the user calls the ``packets`` with ``-h``")
def call_short_help(katamari):
    katamari.result = katamari.runner.invoke(main, [Option.short_help])
    return

#  Then the packets command outputs a help string

# ********** long help ********** #


@scenario("The user calls the ``packets`` command with the long help argument")
def test_long_help():
    return

#  Given a click runner


@when("the user calls the ``packets`` with ``--help``")
def call_long_help(katamari):
    katamari.result = katamari.runner.invoke(main, [Option.long_help])
    return

#  Then the packets command outputs a help string

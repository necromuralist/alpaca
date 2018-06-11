# coding=utf-8
"""The get sub-command feature tests."""
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

# Test help
from ..fixtures import katamari
from .common import (
    ExitCode,
    Option,
    )

# software under test
from packets.main import main

and_also = then
scenario = partial(pytest_bdd.scenario,
                   '../../features/get_subcommand.feature')


class GetOption:
    """Something to keep all the strings together"""
    subcommand="get"

# ******************** Help ******************** #
# ********** short help ********** #


@scenario('The user calls the get subcommand with the short help option')
def test_the_user_calls_the_get_subcommand_with_the_short_help_option():
    return


@given('a cli runner')
def a_cli_runner(katamari):
    katamari.runner = CliRunner()
    return


@when('the user calls the get subcommand with the short help option')
def the_user_calls_the_get_subcommand_with_the_short_help_option(katamari):
    katamari.result = katamari.runner.invoke(main,
                                             [GetOption.subcommand,
                                              Option.short_help])
    return


@then('it returns an okay status')
def it_returns_an_okay_status(katamari):
    expect(katamari.result.exit_code).to(equal(ExitCode.okay))
    return

@and_also('it outputs the help message')
def it_outputs_the_help_message(katamari):
    expect(katamari.result.output).to(start_with("Usage"))
    return

# ********** long ********** #


@scenario("The user calls the get subcommand with the long help option")
def test_long_help():
    return

#  Given a cli runner


@when("the user calls the get subcommand with the long help option")
def long_help(katamari):
    katamari.result = katamari.runner.invoke(main, [GetOption.subcommand,
                                                    Option.long_help])
    return

#  Then it returns an okay status
#  And it outputs the help message

# ******************** no arguments ******************** #


@scenario("The user calls the get subcommand with no options")
def test_no_arguments():
    return

#  Given a cli runner


@when("the user calls the get subcommand with no options")
def no_options(katamari, mocker):
    return


@then("the GetPackets object is built with the defaults")
def check_get_packets_built_without_arguments(katamari):
    return


@and_also("the GetPackets object is run")
def check_get_packets_called(katamari):
    return

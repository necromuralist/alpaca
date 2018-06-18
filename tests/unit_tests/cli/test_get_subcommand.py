# coding=utf-8
"""The get sub-command feature tests."""
# python standard library
from functools import partial
import random

# from pypi
from click.testing import CliRunner
from expects import (
    contain,
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
from packets.get import (
    GetDefaults,
    GetPackets,
    )

and_also = then
scenario = partial(pytest_bdd.scenario,
                   '../../features/cli/get_subcommand.feature')


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

# ******************** Only Source and Target ******************** #


@scenario("The user calls the get subcommand with only the source and target")
def test_source_and_target_given():
    return

#  Given a cli runner


@when("the user calls the get subcommand with the source and target")
def call_with_source_and_target(katamari, mocker, faker):
    katamari.getter_instance = mocker.MagicMock()
    katamari.getter = mocker.MagicMock(spec=GetPackets,
                                       return_value=katamari.getter_instance)
    mocker.patch("packets.main.GetPackets", katamari.getter)
    katamari.source = "/tmp"
    katamari.target = faker.unix_partition()
    katamari.result = katamari.runner.invoke(main, [GetOption.subcommand,
                                                    katamari.source,
                                                    katamari.target])
    expect(katamari.result.exit_code).to(equal(ExitCode.okay))
    katamari.arguments = dict(source=katamari.source,
                              target=katamari.target,
                              source_glob=GetDefaults.glob,
                              start=GetDefaults.start,
                              end=GetDefaults.end)
    return


@then("the GetPackets object is built with the expected arguments")
def check_arguments(katamari):
    katamari.getter.assert_called_once_with(**katamari.arguments)
    return


@and_also("the GetPackets object is run")
def check_call(katamari):
    katamari.getter_instance.assert_called_once_with()
    return

# ******************** non-existent source ******************** #


@scenario("The user calls the get subcommand with a non-existent source")
def test_bad_source():
    return

#  Given a cli runner


@when("the user calls the get subcommand with a non-existent source")
def call_bad_source(katamari, faker):
    source = faker.file_path()
    target = faker.unix_partition()
    katamari.error_message = 'Path "{}" does not exist.'.format(source)
    katamari.result = katamari.runner.invoke(main,
                                             [GetOption.subcommand,
                                              source, target])
    return


@then("it returns an error status")
def check_error_status(katamari):
    expect(katamari.result.exit_code).to(equal(ExitCode.error))
    return


@and_also("it outputs an error message")
def check_error_message(katamari):
    expect(katamari.result.output).to(contain(katamari.error_message))
    return

# ******************** no arguments ******************** #


@scenario("The user calls the get subcommand with no options")
def test_no_arguments():
    return

#  Given a cli runner


@when("the user calls the get subcommand with no options")
def no_options(katamari, mocker):
    katamari.getter = mocker.MagicMock(spec=GetPackets)
    mocker.patch("packets.main.GetPackets", katamari.getter)
    katamari.result = katamari.runner.invoke(main, [GetOption.subcommand])
    katamari.error_message = 'Error: Missing argument "source"'    
    return

# Then it returns an error status
# And it outputs an error message

# ******************** all the arguments ******************** #


@scenario("The user calls the subcommand with start, end, and compression")
def test_all_arguments():
    return

#  Given a cli runner


@when("the user calls the get subcommand with all the options")
def all_the_options(katamari, mocker, faker):
    katamari.getter_instance = mocker.MagicMock()
    katamari.getter = mocker.MagicMock(spec=GetPackets,
                                       return_value=katamari.getter_instance)
    
    mocker.patch("packets.main.GetPackets", katamari.getter)
    katamari.source = "/tmp"
    katamari.target = faker.unix_partition()
    katamari.source_glob = "channel_6*"
    katamari.start = faker.time(pattern="%H:%M:%S")
    katamari.end = faker.time(pattern="%H:%M:%S")
    katamari.compression = random.choice("gzip bz2".split())
    
    katamari.result = katamari.runner.invoke(main, [GetOption.subcommand,
                                                    katamari.source,
                                                    katamari.target,
                                                    "--glob", katamari.source_glob,
                                                    "--start", katamari.start,
                                                    "--end", katamari.end,
                                                    "--compression", katamari.compression])
    katamari.arguments = dict(source=katamari.source,
                              target=katamari.target,
                              source_glob=katamari.source_glob,
                              start=katamari.start,
                              end=katamari.end)
    return

#  Then it returns an okay status
#  And the GetPackets object is built with the expected arguments
#  And the GetPackets object is run

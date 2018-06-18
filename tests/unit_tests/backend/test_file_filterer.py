# coding=utf-8
"""A packet-file filterer feature tests."""
# python standard library
from functools import partial
from pathlib import Path
import random

# pypi
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

# testing help
from ..fixtures import katamari

# software under test
from packets.get import FileFilterer
from packets.errors import ConfigurationError

and_also = then
And = when 

scenario = partial(pytest_bdd.scenario,
                   '../../features/backend/file_filterer.feature')

def setup_path(katamari, mocker):
    """Sets up a mock to replace Path

    sets katamari.path_definition to the mock to use when patching
    'Path' and katamari.path to the mock object returned by Path constructor

    Args:
     katamari: object to stick objects in
     mocker: fixture with Mock definition
    Returns:
     katamari: object with .path, .path_mock
    """
    katamari.path = mocker.MagicMock(spec=Path)
    katamari.path_mock = mocker.MagicMock(spec=Path)
    katamari.path_mock.return_value = katamari.path
    katamari.path.exists.return_value = True
    katamari.path.is_dir.return_value = True
    return katamari


def build_arguments(path='.', glob='*', start=None, end=None):
    """Builds the arguments for the FileFilterer

    Returns:
     dict: arguments to construct the filterer
    """
    return dict(path=path, glob=glob, start=start, end=end)

# ******************** all Files ******************** #


@scenario('No start or end time is given')
def test_no_start_or_end_time_is_given():
    return


@given('arguments with no start or end time')
def a_packetfile_filterer(katamari, mocker):
    katamari.path_mock = mocker.MagicMock(spec=Path)
    katamari.arguments = build_arguments()
    katamari.expected_attributes = katamari.arguments.copy()
    katamari.expected_attributes["path"] = katamari.path_mock
    katamari.expected = ["apple", "banana"]
    return


@when('the file filterer is built')
def it_is_built_with_no_start_or_end_time(katamari, mocker):
    katamari.filterer = FileFilterer(**katamari.arguments)
    katamari.filterer._path = katamari.path_mock
    katamari.filterer.path.glob.return_value = katamari.expected
    return


@And('the file-names are retrieved')
def it_is_called(katamari):
    katamari.actual = katamari.filterer.file_names
    return


@then("it has the expected attributes")
def check_attributes(katamari):
    for attribute, expected in katamari.expected_attributes.items():
        expect(getattr(katamari.filterer, attribute)).to(equal(expected))
    return

@and_also('it returns the expected value')
def it_returns_all_the_files(katamari):
    expect(katamari.actual).to(equal(katamari.expected))
    return


# ********** non-existent ********** #

@scenario("The user passes in a non-existent source directory")
def test_non_existent_source(katamari):
    return


@given("arguments with a non-existent source directory")
def setup_non_existent_source(katamari, faker, mocker):
    katamari = setup_path(katamari, mocker)
    katamari.path.exists.return_value = False
    katamari.arguments = build_arguments(path=faker.word())
    return


@when("the user builds the bad FileFilterer object")
def build_bad_filterer(katamari, mocker):
    mocker.patch("packets.get.Path", katamari.path_mock)
    def bad_call():
        FileFilterer(**katamari.arguments)
        return

    katamari.bad_call = bad_call
    return


@then("a ConfigurationError is raised")
def expect_error(katamari):
    expect(katamari.bad_call).to(raise_error(ConfigurationError))
    return

# ********** Non-Folder ********** #

@scenario("The user passes in a non-directory source")
def test_non_directory_source():
    return


@given("arguments with a source that isn't a directory")
def setup_non_directory_source(katamari, mocker):
    katamari = setup_path(katamari, mocker)
    katamari.path.is_dir.return_value = False
    katamari.arguments = build_arguments()
    return


# when("the user builds the bad GetPackets object")

#  Then a ConfigurationError is raised

# ********** non-string ********** #


@scenario("The user passes in a non-string source")
def test_non_string_source():
    return


@given("arguments with a source that isn't a string")
def setup_non_string_source(katamari, mocker):
    setup_path(katamari, mocker)

    def side_effect(path):
        raise TypeError("TypeError: expected str, bytes or os.PathLike object, not int")
    katamari.path_mock.side_effect = side_effect
    katamari.arguments = build_arguments(path=random.randrange(11))
    return

#  When the user builds the bad GetPackets object
#  Then a ConfigurationError is raised

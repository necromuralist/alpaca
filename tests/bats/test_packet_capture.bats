#! /usr/bin/env bats

# our helpers
# `load_helpers`
# `link_executable`
# `TEST_COMMAND`
# `CAPTURE_COMMAND`
load helpers/load

# this uses bats-assert (which requires bats-support)
load_helpers bats-support
load_helpers bats-assert

# create a symlink to test (so you don't have to install it to run it)
link_executable

REQUIRED="The following arguments are required:"

# ******************** installed ******************** #


@test "Scenario: The packet-capture command is runnable" {
    # Given the packet-capture command is on the path
    
    # When the user checks its location
    run which ${CAPTURE_COMMAND}
    
    # Then the shell finds it
    expect_status_to_be_okay

    # And it is executable
    expect_file_to_be_executable ${CAPTURE_COMMAND}
}

# ******************** Help ******************** #

@test "Scenario: The user asks for help with -h" {
    # Given the packet-capture command is on the path
    
    # When the user asks it for help
    options=-h
    
    # Then it exits okay
    # And it has the usage message
    expected="Usage:"
    expect_okay_output $options $expected
}

@test "Scenario: The user asks for help with --help" {
    # Given the packet-capture command

    # When the user asks it for help with --help
    options=--help

    # Then it exits okay
    # And it has the usage message
    expect_okay_output $options $expected
}

# ******************** Errors ******************** #
# ********** No arguments ********** #

@test "Scenario: The user doesn't pass in any arguments" {
    # Given the packet-capture command is on the path
    # When the user runs it without passing in any arguments
    run ${CAPTURE_COMMAND}

    # Then it returns an error
    expect_status_to_be_an_error

    # And it displays the usage message
    expect_output_to_have_a_line_with "Usage:"

    # And it displays the required message
    expect_output_to_have_a_line_with $REQUIRED
}

# ********** no channel ********** #

@test "Scenario: The user doesn't pass in the channel" {
    # Given the packet-capture command is on the path

    # When the user doesn't pass in the channel
    run ${TEST_COMMAND} -i wlp2s0

    # Then it returns an error
    expect_status_to_be_an_error

    # And it displays the required message
    expect_output_to_have_a_line_with $REQUIRED
}

# ********** No interface ********** #

@test "Scenario: The user doesn't pass in the interface" {
    # Given the packet-capture command is on the path

    # When the user doesn't pass in the interface
    run ${TEST_COMMAND} --channel 5

    # Then it returns an error
    expect_status_to_be_an_error

    # And it displays the required message
    expect_output_to_have_a_line_with $REQUIRED
}

# ******************** Defaults ******************** #
# ***** Output Path ***** #


@test "Scenario: The user doesn't pass in the output path" {
    # Given the packet-capture command is on the path
    # When the user doesn't pass in the output path

    # Then it exits okay
    # And the output is the expected
    expected="Storing Packets In the Directory: ${DEFAULT_DIRECTORY}"
    expect_okay_with_random_channel_and_interface '' $expected
}

# ***** Output File ***** #


@test "Scenario: The user doesn't pass in the output file" {
    # Given the packet-capture command is on the path

    # When the user doesn't pass in the output file
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    run ${TEST_COMMAND} -i ${interface} -c ${channel}

    # Then it exits okay
    expect_status_to_be_okay

    # And the output is the expected
    expect_output_to_have_a_line_with "Storing Packets In: ${DEFAULT_DIRECTORY}channel_${channel}${SUFFIX}"
}


# ******************** Options ******************** #

# ********** Channel and Interface ********** #

@test "Scenario: The user passes in the channel and interface" {
    # Given the packet-capture command is on the path

    # When the user passes in the channel and interface
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    run ${TEST_COMMAND} -i ${interface} -c ${channel}

    # Then it exits okay
    expect_status_to_be_okay

    # And the output is the expected
    expect_output_to_have_a_line_with "Using Wireless Interface: ${interface}"
    expect_output_to_have_a_line_with "Using Channel: ${channel}"
}

@test "Scenario: The user passes in the channel and interface with long options" {
    # Given the packet-capture command is on the path

    # When the user passes in the channel and interface with long options
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    run ${TEST_COMMAND} --interface ${interface} -c ${channel}
    
    # Then it exits okay
    expect_status_to_be_okay

    # And the output is the expected
    expect_output_to_have_a_line_with "Using Wireless Interface: ${interface}"
    expect_output_to_have_a_line_with "Using Channel: ${channel}"
}

# ********** Output Path ********** #
# ***** short

@test "Scenario: The user passes in the output path" {
    # Given the packet-capture command is on the path

    # When the user passes in the output path
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local path=$(random_alphanumeric 12)
    run ${TEST_COMMAND} --interface ${interface} -c ${channel} -p $path

    # Then it exits okay
    expect_status_to_be_okay

    # And the output is the expected
    expect_output_to_have_a_line_with "Storing Packets In the Directory: ${path}"
}

# ***** long with trailing slash

@test "Scenario: The user passes in the output path with a long option and trailing slash" {
    # Given the packet-capture command is on the path

    # When the user passes in the output path with a trailing slash
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local path=$(random_alphanumeric 12)/
    run ${TEST_COMMAND} --interface ${interface} -c ${channel} --path $path

    # Then it exits okay
    expect_status_to_be_okay

    # And the output is the expected
    expect_output_to_have_a_line_with "Storing Packets In the Directory: ${path}"
}

# ***** Long missing trailing slash

@test "Scenario: The user passes in the output path with a long option and no trailing slash" {
    # Given the packet-capture command is on the path

    # When the user passes in the output path with a trailing slash
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local path=$(random_alphanumeric 12)
    run ${TEST_COMMAND} --interface ${interface} -c ${channel} --path $path

    # Then it exits okay
    expect_status_to_be_okay

    # And the output is the expected
    expect_output_to_have_a_line_with "Storing Packets In the Directory: ${path}/"
}

# ********** Output file ********** #
# ***** short

@test "Scenario: The user passes in the output file name" {
    # Given the packet-capture command is on the path

    # When the user passes in the output file name
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local output_file=$(random_alphanumeric 12)
    run ${TEST_COMMAND} --interface ${interface} -c ${channel} -f $output_file

    # Then it exits okay
    expect_status_to_be_okay

    # And the output is the expected
    expect_output_to_have_a_line_with "Storing Packets In: ${DEFAULT_DIRECTORY}${output_file}${SUFFIX}"
}

# ***** Long

@test "Scenario: The user passes in the output file name with the long option" {
    # Given the packet-capture command is on the path

    # When the user passes in the output file name
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local output_file=$(random_alphanumeric 12)
    run ${TEST_COMMAND} --interface ${interface} -c ${channel} --output ${output_file}

    # Then it exits okay
    expect_status_to_be_okay

    # And the output is the expected
    expect_output_to_have_a_line_with "Storing Packets In: ${DEFAULT_DIRECTORY}${output_file}${SUFFIX}"
}

# ******************** Debug ******************** #


@test "Scenario: The user passes in the debug flag." {
    # Given the packet-capture command is on the path

    # When the user passes in the debug flag
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    run ${TEST_COMMAND} -c $channel -i $interface
    # Then it exits okay
    expect_status_to_be_okay

    # And airmon-ng wasn't called
    
}
# ******************** Unknown ******************** #

@test "Scenario: The user passes in an unknown flag" {
    # Given the packet-capture command is on the path

    # When the user passes in an unknown flag
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local unknown=${random_alphanumeric 10}
    run ${TEST_COMMAND} -c $channel -i $interface --${unknown}
    
    # The it returns an error code
    expect_status_to_be_an_error
    # And shows an error message
}
# ******************** maximum files ******************** #

@test "Scenario: The user passes in the maximum number of log files." {
    # Given the packet-capture command is on the path

    # When the user passes in the maximum files flag

    # Then it exits okay

    # And the output is the expected
}
# ******************** maximum file size ******************** #

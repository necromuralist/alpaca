#! /usr/bin/env bats

# this uses `bats <https://github.com/sstephenson/bats>`__

# our helpers
# `load_helpers`
# `link_executable`
# `TEST_COMMAND`
# `CAPTURE_COMMAND`
# and many more... if you see something not defined look in helpers/load.bats
load helpers/load

# this uses bats-assert (which requires bats-support)
load_helpers bats-support
load_helpers bats-assert

# create a symlink to test (so you don't have to install it to run it)
link_executable

REQUIRED="The following arguments are required:"

# ******************** In Progress ******************** #
# Put the in-progress stuff first since BATS doesn't let you run just one test


# ******************** installed ******************** #


@test "Scenario: The packet-capture command is runnable" {
    # Given the packet-capture command is on the path

    # When the user checks its location
    run which ${CAPTURE_COMMAND}

    # Then the shell finds it
    expect_status_to_be_okay

    # And it is executable
    expect_file_to_be_executable "${CAPTURE_COMMAND}"
}

# ******************** Help ******************** #

@test "Scenario: The user asks for help with -h" {
    # Given the packet-capture command is on the path

    # When the user asks it for help
    options=-h

    # Then it exits okay
    # And it has the usage message
    expected="Usage:"
    expect_okay_output "$options" "$expected"
}

@test "Scenario: The user asks for help with --help" {
    # Given the packet-capture command

    # When the user asks it for help with --help
    options=--help

    # Then it exits okay
    # And it has the usage message
    expect_okay_output "$options" "$expected"
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
    expect_output_to_have_a_line_with "$REQUIRED"
}

# ********** no channel ********** #

@test "Scenario: The user doesn't pass in the channel" {
    # Given the packet-capture command is on the path

    # When the user doesn't pass in the channel
    run ${TEST_COMMAND} -i wlp2s0

    # Then it returns an error
    expect_status_to_be_an_error

    # And it displays the required message
    expect_output_to_have_a_line_with "$REQUIRED"
}

# ********** No interface ********** #

@test "Scenario: The user doesn't pass in the interface" {
    # Given the packet-capture command is on the path

    # When the user doesn't pass in the interface
    run ${TEST_COMMAND} --channel 5

    # Then it returns an error
    expect_status_to_be_an_error

    # And it displays the required message
    expect_output_to_have_a_line_with "$REQUIRED"
}

# ******************** Defaults ******************** #
# ***** Output Path ***** #


@test "Scenario: The user doesn't pass in the output path" {
    # Given the packet-capture command is on the path
    # When the user doesn't pass in the output path
    local expected="Storing Packets In the Directory: ${DEFAULT_DIRECTORY}"
    expect_okay_with_random_channel_and_interface '' "$expected"

    # Then it makes the directory (if needed)
    expect_output_to_have_a_line_with "mkdir called with: -p ${DEFAULT_DIRECTORY}"
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-w ${DEFAULT_DIRECTORY}" "regex"
}

# ***** Output File ***** #


@test "Scenario: The user doesn't pass in the output file" {
    # Given the packet-capture command is on the path

    # When the user doesn't pass in the output file
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local options="-i ${interface} -c ${channel} ${1}"
    local name="${DEFAULT_DIRECTORY}channel_${channel}${SUFFIX}"
    local expected_output="Storing Packets In: ${name}"
    expect_okay_output "${options}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-w ${name}" "regex"
}

# ********** Max Files ********** #

@test "Scenario: The user doesn't pass in the maximum number of files" {
    # Given the packet-capture command is on the path
    # When the user doesn't pass in the maximum number of files to create
    local expected_output="Maximum Number of Files: ${DEFAULT_MAX_FILES}"
    expect_okay_with_random_channel_and_interface '' "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-W ${DEFAULT_MAX_FILES}" "regex"
}

# ********** Max File Size ********** #
@test "Scenario: The user doesn't pass in the maximum file size" {
    # Given the packet-capture command is on the path
    # When the user doesn't pass in the maximum file size
    local expected_output="Maximum File Size: ${DEFAULT_MAX_SIZE}"
    expect_okay_with_random_channel_and_interface '' "${expected_output}"

    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-C ${DEFAULT_MAX_SIZE}" "regex"
}

# ********** post-rotate command ********** #
@test "Scenario: The user doesn't pass in the post rotate command" {
    # Given the packet-capture command is on the path
    # When the user doesn't pass in the post-rotate command
    local expected_output="Post-Rotate Command: ${DEFAULT_POSTROTATE}"
    expect_okay_with_random_channel_and_interface '' "${expected_output}"

    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-C ${DEFAULT_MAX_SIZE}" "regex"
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

    # And ip and iwconfig are called correctly
    expect_output_to_have_a_line_with "ip called with: link set ${interface} down"
    expect_output_to_have_a_line_with "iwconfig called with: ${interface} mode monitor"
    expect_output_to_have_a_line_with "ip called with: link set ${interface} up"
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

    # And ip and iwconfig are called correctly
    expect_output_to_have_a_line_with "ip called with: link set ${interface} down"
    expect_output_to_have_a_line_with "iwconfig called with: ${interface} mode monitor"
    expect_output_to_have_a_line_with "ip called with: link set ${interface} up"    
}

# ********** Output Path ********** #
# ***** short

@test "Scenario: The user passes in the output path" {
    # Given the packet-capture command is on the path

    # When the user passes in the output path
    local path=$(random_alphanumeric 12)
    local expected_output="Storing Packets In the Directory: ${path}"
    expect_okay_with_random_channel_and_interface "--path ${path}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-w ${path}" "regex"
}

# ***** long with trailing slash

@test "Scenario: The user passes in the output path with a long option and trailing slash" {
    # Given the packet-capture command is on the path

    # When the user passes in the output path with a trailing slash
    local path=$(random_alphanumeric 12)/
    local expected_output="Storing Packets In the Directory: ${path}"
    expect_okay_with_random_channel_and_interface "--path ${path}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-w ${path}" "regex"
}

# ***** Long missing trailing slash

@test "Scenario: The user passes in the output path with a long option and no trailing slash" {
    # Given the packet-capture command is on the path

    # When the user passes in the output path with a trailing slash
    local path=$(random_alphanumeric 12)
    local expected_output="Storing Packets In the Directory: ${path}/"
    expect_okay_with_random_channel_and_interface "--path ${path}" "${expected_output}"

    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-w ${path}/" "regex"
}

# ********** Output file ********** #
# ***** short

@test "Scenario: The user passes in the output file name" {
    # Given the packet-capture command is on the path

    # When the user passes in the output file name
    local output_file=$(random_alphanumeric 12)
    local name="${DEFAULT_DIRECTORY}${output_file}${SUFFIX}"
    local expected_output="Storing Packets In: ${name}"
    expect_okay_with_random_channel_and_interface "-f ${output_file}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-w ${name}" "regex"
}

# ***** Long

@test "Scenario: The user passes in the output file name with the long option" {
    # Given the packet-capture command is on the path

    # When the user passes in the output file name
    local output_file=$(random_alphanumeric 12)
    local name="${DEFAULT_DIRECTORY}${output_file}${SUFFIX}"
    local expected_output="Storing Packets In: ${name}"
    expect_okay_with_random_channel_and_interface "--output ${output_file}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-w ${name}" "regex"
}

# ******************** Debug ******************** #


@test "Scenario: The user passes in the debug flag." {
    # Given the packet-capture command is on the path

    # When the user passes in the debug flag
    local expected_output="DEBUG"
    expect_okay_with_random_channel_and_interface "-d" "${expected_output}"
    # And airmon-ng wasn't called
    # need to mock this
}

@test "Scenario: The user passes in the long debug flag." {
    # Given the packet-capture command is on the path

    # When the user passes in the debug flag
    local expected_output="DEBUG"
    expect_okay_with_random_channel_and_interface "--debug" "${expected_output}"
    # And airmon-ng wasn't called
    # need a mock
}
# ******************** Unknown ******************** #

@test "Scenario: The user passes in an unknown flag" {
    # Given the packet-capture command is on the path

    # When the user passes in an unknown flag
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local unknown=$(random_alphanumeric 10)
    run ${TEST_COMMAND} -c $channel -i $interface --${unknown}

    # Then it returns an error code
    expect_status_to_be_an_error

    # And shows an error message
    expect_output_to_have_a_line_with ".*Error: Unknown Argument.* '--${unknown}'" "regex"

    # And it shows the usage message
    expect_output_to_have_a_line_with "Usage:"
}
# ******************** maximum files ******************** #

@test "Scenario: The user passes in the maximum number of log files." {
    # Given the packet-capture command is on the path

    # When the user passes in the maximum files flag
    local maximum=$(random_integer 1 1000)
    local expected="Maximum Number of Files: ${maximum}"
    expect_okay_with_random_channel_and_interface "-n ${maximum}" "${expected}"

    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-W ${maximum}" "regex"
}

@test "Scenario: The user passes in the long maximum files" {
    # Given the packet-capture command is on the path

    # When the user passes in the --maximum-files flag
    local maximum=$(random_integer 1 1000)
    local expected="Maximum Number of Files: ${maximum}"
    expect_okay_with_random_channel_and_interface "--max-files ${maximum}" "${expected}"
    # Then it exits okay

    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-W ${maximum}" "regex"
}
# ******************** maximum file size ******************** #

@test "Scenario: The user passes in the maximum file size" {
    # Given the packet-capture command is on the path
    # When the user passes in the maximum file size
    local maximum=$(random_integer 1 1000)
    local expected_output="Maximum File Size: ${maximum} million bytes"
    expect_okay_with_random_channel_and_interface "-s ${maximum}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-C ${maximum}" "regex"
}

@test "Scenario: The user passes in the long maximum file size flag" {
    # Given the packet-capture command is on the path
    # When the user passes in the long maximum file size flag
    local maximum=$(random_integer 1 1000)
    local expected_output="Maximum File Size: ${maximum} million bytes"
    expect_okay_with_random_channel_and_interface "--max-size ${maximum}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-C ${maximum}" "regex"
}


# ******************** post-rotate ******************** #
@test "Scenario: The user passes in the post-rotation command" {
    # Given the packet-capture command is on the path
    # When the user passes in the post-rotate command
    local post_rotation=$(random_alphanumeric 5)
    local expected_output="Post-Rotate Command: ${post_rotation}"
    expect_okay_with_random_channel_and_interface "-r ${post_rotation}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-z ${post_rotation}" "regex"
}

@test "Scenario: The user passes in the long post-rotation command" {
    # Given the packet-capture command is on the path
    # When the user passes in the long post-rotate command
    local post_rotation=$(random_alphanumeric 5)
    local expected_output="Post-Rotate Command: ${post_rotation}"
    expect_okay_with_random_channel_and_interface "--post-rotate ${post_rotation}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
    expect_output_to_have_a_line_with "tcpdump.*-z ${post_rotation}" "regex"
}

# ******************** packet snaphshot length ******************** #
@test "Scenario: The user passes in the packet snapshot length" {
    # Given the packet-capture command is on the path
    # When the user passes in the post-rotate command
    local packet_length=$(random_integer 0 999999999)
    local expected_output="Packet Snapshot Length: ${packet_length} bytes"
    expect_okay_with_random_channel_and_interface "-l ${packet_length}" "${expected_output}"
    # Then it exits okay
    # And the tcpdump command has the option
    expect_output_to_have_a_line_with "tcpdump.*--snapshot-length ${packet_length}" "regex"
}

@test "Scenario: The user passes in the long packet snapshot length flag" {
    # Given the packet-capture command is on the path
    # When the user passes in the post-rotate command
    local packet_length=$(random_integer 0 999999999)
    local expected_output="Maximum Packet Snapshot Length: ${packet_length} bytes"
    # Then it exits okay
    # And it has the expected output
    expect_okay_with_random_channel_and_interface "--packet-length ${packet_length}" "${expected_output}"
    expect_output_to_have_a_line_with "tcpdump.*--snapshot-length ${packet_length}" "regex"

}

# ******************** User ******************** #

@test "Scenario: The user passes in a user name to own the files" {
    # Given the packet-capture command is on the path
    # When the user passes in the name of the user to own the files
    local username=$(random_alphanumeric 10)
    local expected_output="User to own the files: ${username}"
    local other_expected_output=" --relinquish-privileges ${username}"

    # Then it tells the user that it's using the username
    expect_okay_with_random_channel_and_interface "-u ${username}" "${expected_output}"

    # And it sets the permissions for the directory
    expect_output_to_have_a_line_with "chmod called with: -R ${DEFAULT_PERMISSIONS} ${DEFAULT_DIRECTORY}"

    # And it changes the owner of the directory
    expect_output_to_have_a_line_with "chown called with: -R ${username}:${MOCK_GROUP} ${DEFAULT_DIRECTORY}"

    # and it gives the options to tcpdump
    expect_output_to_have_a_line_with "tcpdump.*${other_expected_output}" "regex"
}

@test "Scenario: The user passes in a long user name to own the files" {
    # Given the packet-capture command is on the path
    # When the user passes in the name of the user to own the files with the long user flag
    local username=$(random_alphanumeric 10)
    local expected_output="User to own the files: ${username}"
    local other_expected_output=" --relinquish-privileges ${username}"
    
    # Then it tells the user that it's using the username
    expect_okay_with_random_channel_and_interface "--username ${username}" "${expected_output}"

    # And it sets the permissions for the directory
    expect_output_to_have_a_line_with "chmod called with: -R ${DEFAULT_PERMISSIONS} ${DEFAULT_DIRECTORY}"

    # And it changes the owner of the directory
    expect_output_to_have_a_line_with "chown called with: -R ${username}:${MOCK_GROUP} ${DEFAULT_DIRECTORY}"
    
    # And the correct option is given to tcpdump
    expect_output_to_have_a_line_with "${other_expected_output}"
}

# ******************** buffer size ******************** #

@test "Scenario: The user passes in the buffer size" {
    # Given the packet-capture command is on the path
    # When the user passes in the buffer-size option
    local size=$(random_integer 100 1000000)
    local expected_output="Packet Buffer Size: ${size}"
    local expected_option=" --buffer-size ${size}"
    # Then it has the expected output
    expect_okay_with_random_channel_and_interface "-b ${size}" "${expected_output}"
    # And the correct option is given to tcpdump
    expect_output_to_have_a_line_with "${expected_option}"
}

@test "Scenario: The user passes in the long buffer-size flag" {
    # Given the packet-capture command is on the path
    # When the user passes in the buffer-size option
    local size=$(random_integer 100 1000000)
    local expected_output="Packet Buffer Size: ${size}"
    local expected_option=" --buffer-size ${size}"
    # Then it has the expected output
    expect_okay_with_random_channel_and_interface "--buffer-size ${size}" "${expected_output}"
    # And the correct option is given to tcpdump
    expect_output_to_have_a_line_with "${expected_option}"
}

# ******************** don't verify checksums ******************** #

@test "Scenario: The user asks to not verify checksums" {
    # Given the packet-capture command is on the path
    # When the user asks to not verify checksums
    local expected_output="Turning off checksum verification"
    local expected_option=" --dont-verify-checksums"
    # Then it has the expected output
    expect_okay_with_random_channel_and_interface "-k" "${expected_output}"
    # And the correct option is given to tcpdump
    expect_output_to_have_a_line_with "${expected_option}"
}

@test "Scenario: The user asks to not verify checksums with the long flag" {
    # Given the packet-capture command is on the path
    # When the user asks to not verify checksums
    local expected_output="Turning off checksum verification"
    local expected_option=" --dont-verify-checksums"
    # Then it has the expected output
    expect_okay_with_random_channel_and_interface "--no-checksum-verification" "${expected_output}"
    # And the correct option is given to tcpdump
    expect_output_to_have_a_line_with "${expected_option}"
}

# ******************** Verbosity ******************** #

@test "Scenario: The user passes in the verbosity level" {
    # Given the packet-capture command is on the path
    # When the user passes in the verbosity
    local verbosity=$(random_integer 1 3)
    local expected_output="Verbosity Level: ${verbosity}"
    local vs
    eval printf -v vs '%.0sv' {1..${verbosity}}
    vs="-${vs}"
    local expected_option=" ${vs}"
    # Then it has the expected output
    expect_okay_with_random_channel_and_interface "-v ${verbosity}" "${expected_output}"
    # And the correct option is given to tcpdump
    expect_output_to_have_a_line_with "${expected_option}"
}

@test "Scenario: The user passes in the verbosity level with the long flag" {
    # Given the packet-capture command is on the path
    # When the user passes in the verbosity with the long flag
    local verbosity=$(random_integer 1 3)
    local expected_output="Verbosity Level: ${verbosity}"
    local vs
    eval printf -v vs '%.0sv' {1..${verbosity}}
    vs="-${vs}"
    local expected_option=" ${vs}"
    # Then it has the expected output
    expect_okay_with_random_channel_and_interface "--verbosity ${verbosity}" "${expected_output}"
    # And the correct option is given to tcpdump
    expect_output_to_have_a_line_with "${expected_option}"
}

# ******************** Version ******************** #

@test "Scenario: The user asks for the version" {
      # Given the packet-capture command is on the path
      # When the user passes in the version flag
      local expected_output="Version:[[:space:]]+[[:digit:]]{2,4}\.[[:digit:]]{1,2}\.[[:digit:]]{1,2}"
      run ${TEST_COMMAND} "--version"
      # Then it exits okay
      expect_status_to_be_okay

      # And it has the expected output
      expect_output_to_have_a_line_with "${expected_output}" "regex"
}

# ******************** tcp dump options ******************** #

@test "Scenario: The command string for tcpdump is constructed" {
    # Given the packet-capture command is on the path
    # When the user passes in the channel and interface
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local options="-i ${interface} -c ${channel} ${1}"
    local expected_output="tcpdump -n -w ${DEFAULT_DIRECTORY}channel_${channel}.pcap -C ${DEFAULT_MAX_SIZE} -W ${DEFAULT_MAX_FILES} --snapshot-length ${DEFAULT_PACKET_LENGTH} --interface ${interface}mon -z ${DEFAULT_POSTROTATE}"
    expect_okay_output "${options}" "${expected_output}"
    # Then it exits okay
    # And the output is the expected
}

# - for each, check that the user actually passed in a command? {}
# - and for numbers, check that they are numbers

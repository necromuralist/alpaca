# use the bats `load` function to load these into the test-environments
# right now this is setup only for the packet_capture.sh testing

# some constants
OKAY=0
ERROR=2
CAPTURE_COMMAND="packet-capture"
TEST_COMMAND="${CAPTURE_COMMAND} --debug "
DEFAULT_DIRECTORY="/tmp/packets/"
SUFFIX="_%Y-%m-%d_%H:%M:%S.pcap"

# Runs the command and checks the message, expecting the status code to be okay
#
# GLobals:
#  None
# Arguments:
#  $1 - command options
#  $2 - Expected output string
# Returns:
#  0 - on success
#  1 - otherwise
expect_okay_output() {
    echo "options: ${1}"
    run ${TEST_COMMAND} $1
    expect_status_to_be_okay
    expect_output_to_have_a_line_with $2
}

# Sets up the symbolic link for the packet-capture command
# This will create a symbolic link (if needed) to the software under test
# Into the /tmp folder so that we can test it without (semi-)permanently
# installing it
#
# Globals:
#  CAPTURE_COMMAND
# Arguments:
#  None
# Returns:
#  0 - on success
#  1 - otherwise
link_executable() {
    local extra_path="/tmp/bats/bin"
    local target=${extra_path}/${CAPTURE_COMMAND}

    # I don't know why but my machines at home act differently than brunhilde does
    local above_source="system_setup/bin/packet_capture.sh"
    local helper_source="../../../system_setup/bin/packet_capture.sh"
    local local_source=""
    if [ -f {$above_source} ]; then
        local_source=$above_source
    elif [ -f {$helper_source} ]; then
        local_source=$helper_source
    else
        target=$(which $CAPTURE_COMMAND)
        if [ $? -ne 0 ]; then
            echo "Error: Unable to find '$CAPTURE_COMMAND'"
            exit 1
        fi
    fi
    mkdir -p ${extra_path}
    if [ ! -f ${target} ]; then
        ln -rs ${local_source} ${target}
    fi
    export PATH=${extra_path}:$PATH
}

# Checks that the output had a sub-string
#
# Globals:
#  None
# Arguments:
#  $1 - sub-string to match is the output
# Returns:
#  0 - output had sub-string
#  1 - otherwise
expect_output_to_have_a_line_with() {
    assert_line --partial "${1}"
}

# Checks that the status was okay
#
# Globals:
#  None
# Arguments:
#  none
# Returns:
#  0 - status returned okay
#  1 - otherwise
expect_status_to_be_okay() {
    assert_success
}

# Checks the status was an error code
#
#
# Globals:
#  ERROR
# Arguments:
#  None
# Returns:
#  0 - output had sub-string
#  1 - otherwise
expect_status_to_be_an_error() {
    assert_failure ${ERROR}
}

# Check that a file is executable
#
# Globals:
#   none
# Arguments:
#   $1 - name of executable
# Returns:
#   0 - on success
#   1 - otherwise
expect_file_to_be_executable() {
    local name="$1"
    path="$(which $name)"
    assert [ -x "${path}" ]
}

# Load a library from the `${BATS_TEST_DIRNAME}/test_helper' directory.
#
# Globals:
#   none
# Arguments:
#   $1 - name of library to load
# Returns:
#   0 - on success
#   1 - otherwise
load_helpers() {
    local name="$1"
    load helpers/${name}/load
}

# Makes a random integer
#
# This returns the value to the user as stdout so you need to evaluate it
#
# Example:
#  channel=$(random_integer 1 10)
#
# Globals:
#  None
# Arguments:
#  $1 - lower limit for the range
#  $2 - upper limit for the range
# Returns:
#  0 - parameters okay
#  2 - otherwise
random_integer() {
    lower=$1
    upper=$2
    if [ $lower -ge $upper ]; then
        echo "Invalid Range: ${lower} - ${upper}"
        exit 2
    fi
    echo $(shuf -i ${lower}-${upper} -n 1)
}

# Makes a random alphanumeric string
#
# This returns the value to the user as stdout so evaluate it
#
# Example:
#  interface=$(random_alphanumeric)
#
# Globals:
#  None
# Arguments:
#  $1 - number of characters (default: 10)
# Returns:
#  0 - output had sub-string
#  2 - otherwise
random_alphanumeric() {
    length=${1:-10}
    if [ $length -le 1 ]; then
        echo "Invalid string length: ${length}"
    fi
    echo $(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w $length | head -n 1)
}

# Sets the channel and interface before running
#
# Globals:
#  None
# Arguments:
#  $1 - options
#  $2 - expected output string
# Returns:
#  0 - on success
#  1 - otherwise
expect_okay_with_random_channel_and_interface() {
    local channel=$(random_integer 1 100)
    local interface=$(random_alphanumeric 5)
    local options="-i ${interface} -c ${channel} ${1}"
    expected=$2
    expect_okay_output "${options}" "${expected}"
}

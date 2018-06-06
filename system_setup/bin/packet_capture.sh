#! /usr/bin/env bash
# this is meant to be run in systemd so it doesn't do any validity checking
# so make sure you get it right
# or at least check the output
# if you want to test it you're going to have to run it as root
# or set the permissions for all the commands
# (tcpdump and iwconfig)
# this assumes you want to use tcpdump

VERSION="2018.05.30"

OKAY=0
ERROR=2
SUFFIX=".pcap"
RED="$(tput setaf 1)"
BLUE="$(tput setaf 4)"
BOLD="$(tput bold)"
RESET="$(tput sgr0)"

MAX_FILES=10
MAX_FILE_SIZE=100
POST_ROTATE="gzip"
PACKET_LENGTH="0"
DIRECTORY_PERMISSIONS=770

# ** Prints the usage screen to stdout
# **
# ** Globals
# **  BLUE: ASCII escape code to color the text blue
# **  RED: ASCII escape code to color the text red
# **  BOLD: ASCII escape code to make the text bold
# **  RESET: ASCII escape code to make the text plain
# ** Arguments:
# **  optional status code to exit with (if not given won't exit)
usage() {
    echo
    echo "${BOLD}Puts the interface into monitor mode and then starts tcpdump${RESET}"
    echo
    echo "${BOLD}Usage:${RESET}"
    echo
    echo "  bash packet_capture.sh -i <interface> -c <channel> [-p <log-file-directory> -f <log file-name> -n <max-log-files> -s <max-log-file-size>]"
    echo
    echo "${BOLD}Options:${RESET}"
    echo
    echo "  ${BLUE}-h, --help${RESET}: Output this message"
    echo
    echo "  ${BLUE}-b, --buffer-size${RESET} <size>: Size of the packet-buffer in KiB (1024 bytes)"
    echo "  ${BLUE}-c, --channel${RESET} <channel>: Number of the wireless channel to monitor"
    echo "  ${BLUE}-d, --debug${RESET}: Output the string that would run but don't execute it"
    echo "  ${BLUE}-f, --output${RESET} <name>: Base name of the log files (without extensions)"
    echo "  ${BLUE}-i, --interface${RESET} <interface>: Name of the network interface to monitor"
    echo "  ${BLUE}-k, --no-checksum-verification${RESET}: Turn off packet verification"
    echo "  ${BLUE}-l, --packet-length${RESET} <length>: Maximum bytes of each packet (small will truncate, big might miss packets)"
    echo "  ${BLUE}-n, --max-files${RESET} <count>: Number of log files to keep in rotation"
    echo "  ${BLUE}-p, --path${RESET} <path>: Directory to use to store logs"
    echo "  ${BLUE}-r, --post-rotate${RESET} <command>: command to apply to each file after it is saved"
    echo "  ${BLUE}-s, --max-size${RESET} <size>: Maximum size for each file (in millions of bytes)"
    echo "  ${BLUE}-u, --username${RESET} <name>: Name of the user to own the files (otherwise it is 'root')"
    echo "  ${BLUE}-v, --verbosity${RESET} <level>: Increase verbosity level for the packet output (by 1, 2, or 3)"
    echo "  ${BLUE}    --version${RESET}: Output the current version of this command"

    echo
    echo "${BOLD}Defaults:${RESET}"
    echo "  Buffer Size: What your Operating System is set to"
    echo "  Number of log files: 10"
    echo "  Maximum file size: 100 million bytes"
    echo "  Log File Directory: '/tmp/packets/'"
    echo "  Log File Name: 'channel_<channel argument>.pcap'"
    echo "  Packet Length: 262144 bytes"
    echo "  Post-Rotate Command: 'gzip'"
    echo "  Verbosity: 0 (normal verbosity, no added levels)"
    echo
    echo "This will add a  .pcap suffix to the log file-name so don't put a file extension"
    if [ ! -z ${1} ]; then
        exit ${1}
    fi
}

# ** Cleanup function to handle the script being killed
# ** This is primarily meant to take the interface back outof monitor mode
# **
# ** Globals:
# **  interface: the name of the interface to take out of monitor mode
# ** Arguments:
# **  None
# ** Returns:
# **  0 on success
# **  1 otherwise
cleanup() {
    echo "${BOLD}Turning off monitor mode for ${interface}${RESET}"
    ip link set ${interface} down
    iwconfig ${interface} mode managed
    ip link set ${interface} up
    # airmon-ng stop ${interface}mon
    exit $?
}

# ** Displays the required arguments
required() {
    echo "The following arguments are required:"
    echo "  -i <wireless interface>"
    echo "  -c <channel>"
    exit ${ERROR}
}

check_version() {
    if [ ! -z ${version} ]; then
        echo "Version: ${VERSION}"
        exit ${OKAY}
    fi
}

check_required() {
    if [[ -z $i_set || -z $c_set ]]; then
        required
    fi
}

setup_output_directory() {
    if [ -z $output_path ]; then
        output_path=/tmp/packets/
    elif [[ ! "${output_path}" =~ ".*/$" ]]; then
        output_path=${output_path}/
    fi

    echo "Storing Packets In the Directory: $output_path"
    mkdir -p $output_path

    if [ ! -z $username ]; then
        chmod -R ${DIRECTORY_PERMISSIONS} ${output_path}
        group=$(id -gn ${username})
        chown -R ${username}:${group} ${output_path}
    fi
}

setup_output_file() {
    if [ -z ${output_file} ]; then
        output_file=channel_${channel}
    fi
    output_file=${output_path}${output_file}${SUFFIX}
    echo "Storing Packets In: ${output_file}"
}

# ** Checks if any values aren't set that we give default values of
# **
# ** Globals
# **  MAX_FILES: Default maximum number of files to create
# **  max_files: Maximum number of files passed in b
# **  MAX_FILE_SIZE: Default max size for each file
# **  max_file_size: User's max size for each file
# **  TIMESTAMP: Timestamp for the file-names
# **  timestamp: User's timestamp
# **  POST_ROTATE: Command to execute on rotated files
# *** post_rotation: User's post-rotate command
check_defaults() {
    max_files=${max_files:-${MAX_FILES}}
    echo "Maximum Number of Files: ${max_files}"
    max_file_size=${max_file_size:-${MAX_FILE_SIZE}}
    echo "Maximum File Size: ${max_file_size} million bytes"
    post_rotation=${post_rotation:-${POST_ROTATE}}
    echo "Post-Rotate Command: ${post_rotation}"
    packet_length=${packet_length:-${PACKET_LENGTH}}
    echo "Maximum Packet Snapshot Length: ${packet_length} bytes"
}

# ** Parses the arguments from the user
# **
# ** Global:
# **  $# - the array of arguments
# ** Status:
# **  0 - all the arguments were recognized and all required arguments given
# **  2 - An unknown argument was given or missing argument(s)
setup_arguments() {
    # we know we need at least one option
    if [ $# -eq 0 ]; then
        usage
        required
    fi

    while (( $# > 0 )); do
        case "$1" in
            -b|--buffer-size)
                shift
                buffer_size="$1"
                echo "Packet Buffer Size: ${buffer_size} KiB"
                buffer_size=" --buffer-size ${buffer_size}"
                shift
                ;;
            -c|--channel)
                shift
                channel="$1"
                c_set=true
                echo "Using Channel: ${channel}"
                shift
                ;;
            -d|--debug) debug=true; shift;;
            -f|--output)
                shift
                output_file="$1"
                shift
                ;;
            -h|--help) usage 0; shift ;;
            -i|--interface)
                shift
                interface="$1"
                i_set=true
                echo "Using Wireless Interface: ${interface}"
                shift
                ;;
            -k|--no-checksum-verification)
                echo "Turning off checksum verification"
                disable_verification=" --dont-verify-checksums"
                shift
                ;;
            -l|--packet-length)
                shift
                packet_length="$1"
                shift
                ;;
            -n|--max-files)
                shift
                max_files="$1"
                shift
                ;;
            -p|--path)
                shift
                output_path="$1"
                shift
                ;;
            -r|--post-rotate)
                shift
                post_rotation="$1"
                shift
                ;;
            -s|--max-size)
                shift
                max_file_size="$1"
                shift
                ;;
            -u|--username)
                shift
                username="$1"
                echo "User to own the files: ${username}"
                username_argument=" --relinquish-privileges ${username}"
                shift
                ;;
            -v|--verbosity)
                shift
                verbosity="$1"
                echo "Verbosity Level: ${verbosity}"
                if [ ${verbosity} -eq 1 ]; then
                    verbosity=" -v"
                elif [ ${verbosity} -eq 2 ]; then
                    verbosity=" -vv"
                elif [ ${verbosity} == 3 ]; then
                    verbosity=" -vvv"
                else
                    echo "${BOLD}${RED}ERROR:${RESET} Verbosity must be from 1 to 3, not ${verbosity}"
                fi
                shift
                ;;
            --version) version=true; shift;;
            *)
                usage
                echo "${BOLD}${RED}Error: Unknown Argument${RESET} '${1}'"
                exit ${ERROR}
                ;;
        esac
    done

    check_version
    check_required
    check_defaults
    setup_output_directory
    setup_output_file
}

setup_arguments "$@"

echo "Each file will be a maximum of $max_file_size million bytes"

# The tcpdump options
# -n: don't translate addresses to names (improves performance)
# -w: The base-name for the rotating files
# -C: Maximum number of rotating files to keep
# -W: Maximum size each file can reach before rotating
# --snapshot-length: maximum packet size in bytes (if it's too big you might miss packets)
#    0 length means use the default of 262144 bytes
# --interface: The network interface to monitor
# --buffer-size: OS capture buffer size
# --dont-verify-checksums: Some hardware will cause it to flag outgoing TCP packets as bad if not set

options="-n -w $output_file -C $max_file_size -W $max_files --snapshot-length ${packet_length} "\
"--interface ${interface} -z ${post_rotation}${username_argument}${buffer_size}${disable_verification}${verbosity}"
echo "tcpdump ${options}"


if [ ! -z $debug ]; then
    # don't run the actual commands
    echo "${BOLD}DEBUG:${RESET} Exiting without running the commands"
    exit ${OKAY=}
fi

echo "Putting interface ${interface} into monitor mode"
# airmon-ng start $interface $channel
# airmon-ng check kill

# Checks that the last command succeeded
#
# Arguments:
#  command-name: the name to display in the output
# Returns:
#  0 on succes
#  1 otherwise
check_ok() {
    if [ $? -ne 0 ]; then
        echo "$1 did not succeed, quitting"
        exit 1
    else
        echo "$1 suceeded, moving on"
    fi
}

# you don't always need to do this, but sometimes brining the interface
# down helps set monitor mode
ip link set ${interface} down
check_ok "ip link set ${interface} down"
iwconfig ${interface} mode monitor
check_ok "iwconfig ${interface} mode monitor"

# but it won't set the channel unless the interface is up
ip link set ${interface} up
check_ok "ip link set ${interface} up"
iwconfig ${interface} channel ${channel}
check_ok "iwconfig ${interface} channel ${channel}"

# catch ctrl-c and cleanup before quitting
trap cleanup SIGINT

tcpdump ${options}

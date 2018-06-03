#! /usr/bin/env bash
# this is meant to be run in systemd so it doesn't do any validity checking
# so make sure you get it right
# or at least check the output
# if you want to test it you're going to have to run it as root
# or set the permissions for all the commands (`airmon-ng` is a bash script that calls)
# other commands so it isn't just tcpdump that needs to be changed
# this assumes you want to use tcpdump

# ./packet_capture.sh <interface> <channel> <log file-directory> <log file-name> <max-log-files> <max-log-file-size>

OKAY=0
ERROR=2
SUFFIX="_%Y-%m-%d_%H:%M:%S.pcap"

usage() {
    echo "Puts the interface in monitor mode and then starts tcpdump"
    echo "Usage:"
    echo "  bash packet_capture.sh -i <interface> -c <channel> [-d <log-file-directory> -o <log file-name> -n <max-log-files> -s <max-log-file-size>]"
    echo
    echo "defaults:"
    echo "  Number of log files: 10"
    echo "  Maximum file size: 100 million bytes"
    echo "  Log File Directory: '/tmp/packets/"
    echo "  Log File Name: 'channel_<channel argument>'"
    echo
    echo "to get this output:"
    echo "  bash packet_capture.sh -h"
    echo
    echo "This will add a timestamp and .pcap suffix to the log file-name so don't put a file extension"
    if [ ! -z ${1} ]; then
        exit ${1}
    fi
}

required() {
    echo "The following arguments are required:"
    echo "  -i <wireless interface>"
    echo "  -c <channel>"
    exit 2
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
}

setup_output_file() {
    if [ -z ${output_file} ]; then
        output_file=channel_${channel}
    fi
    output_file=${output_path}${output_file}${SUFFIX}
    echo "Storing Packets In: ${output_file}"
}

setup_arguments() {
    # we know we need at least one option
    if [ $# -eq 0 ]; then
        usage
        required
    fi

    while (( $# > 0 )); do
        case "$1" in
            -h|--help) usage 0; shift ;;
            -d|--debug) debug=true; shift;;
            -i|--interface)
                shift                
                interface="$1"
                i_set=true
                echo "Using Wireless Interface: ${interface}"
                shift
                ;;
            -c|--channel)
                shift
                channel="$1"
                c_set=true
                echo "Using Channel: ${channel}"
                shift
                ;;
            -p|--path)
                shift
                output_path="$1"
                shift
                ;;
            -f|--output)
                shift
                output_file="$1"
                shift
                ;;
            *)
                break ;;
        esac
    done
    check_required
    setup_output_directory
    setup_output_file
}

setup_arguments "$@"

# while getopts ":c:i:d:o:n:s:h" option; do
#         n)
#             max_files=${OPTARG}
#             ;;
#         s)
#             max_file_size=${OPTARG}
#             ;;
#         :)
#             echo "Option -$OPTARG requires an argument" >&2
#             exit 2
#     esac
# done
# 
# 
# if [ -z $output_file ]; then
#     output_file="channel_${channel}"
# fi
# 
# output_file=${output_path}${output_file}_%Y-%m-%d_%H:%M:%S.pcap
# echo "Storing Packets in: ${output_file}"
# 
# if [ -z $max_files ]; then
#     max_files=10
# fi
# 
# if [ -z $max_file_size ]; then
#     max_file_size=100
# fi
echo "Will create a maximum of $max_files files."
echo "Each file will be a maximum of $max_file_size million bytes"
echo "tcpdump -n -w $output_file -C $max_files -W $max_file_size -s0 -i ${interface}mon"
if $debug; then
    # don't run the actual commands
    exit ${OKAY=}
fi
    
echo "Starting $interface in monitor mode"
airmon-ng start $interface $channel
airmon-ng check kill

if [ $? -ne 0 ]; then
    echo "airmon-ng did not succeed, not running tcpdump"
    exit 1
fi

tcpdump -n -w $output_file -C $max_files -W $max_file_size -s0 -i ${interface}mon

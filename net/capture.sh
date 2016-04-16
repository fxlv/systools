#!/bin/bash
#
# capture.sh - capture and analyze traffic 
#              on linux servers using tcpdump
#
# This is a wrapper script around tcpdump to make
# sysadmins life a bit easier when doing frequent 
# traffic captures to detect network attacks and their sources.
#
#
# kaspars@fx.lv
#
#

INTERFACE=eth1
PACKET_COUNT=10000
DEBUG=0
capture_file_provided=0
write_to_file=0

function die {
    echo "$@"
    exit 1

}

function timestamp {
    date +%d.%m.%y-%H:%M:%S
}

function get_capture_file_name {
    timestamp=$(timestamp)
    MY_IP=$(get_my_ip)
    echo "${HOME}/capture_${HOSTNAME}_${INTERFACE}_${MY_IP}_${PACKET_COUNT}_${timestamp}.pcap"
}

function capture {
    capture_file=$(get_capture_file_name)
    echo "Starting packet capture on interface $INTERFACE"
    echo "Capturing $PACKET_COUNT packets"
    sudo "$tcpdump" -i "$INTERFACE" -s0 -c "$PACKET_COUNT" -w "$capture_file"
    echo "Captured data saved to $capture_file"
}

function get_last_capture_file {
    ls -lasht capture_"$HOSTNAME"_*.pcap|head -1|cut -d " " -f 10
}

function get_my_ip {
    ip a s $INTERFACE|grep " inet "|awk '{ print $2 }'|cut -d "/" -f 1
}

function debugprint {
    (( DEBUG )) && echo "$@"
}

function top_sources {
    (( capture_file_provided )) && last_capture_file=$capture_file_name || last_capture_file=$(get_last_capture_file)
    if [ -e "$last_capture_file" ]; then
        capture_ip=$(echo $last_capture_file|cut -d "_" -f 4)
        debugprint "My ip: $(get_my_ip)"
        debugprint "Capture ip: $capture_ip"
        echo "Thses are the top 10 packet sources"
        sudo "$tcpdump" -tnr "$last_capture_file" 2> /dev/null | awk -F '.' '{print $1"."$2"."$3"."$4}' | sort | uniq -c | sort -n |grep -v $capture_ip | tail -n 10
    else
        die "Capture file $last_capture_file does not exist"
    fi
}

function capture_grep {
    (( capture_file_provided )) && last_capture_file=$capture_file_name || last_capture_file=$(get_last_capture_file)
    if [ -e "$last_capture_file" ]; then
        capture_ip=$(echo "$last_capture_file"|cut -d "_" -f 4)
        debugprint "My ip: $(get_my_ip)"
        debugprint "Capture ip: $capture_ip"
        echo "Grepping capture file $last_capture_file for host $grep_host"
        if (( write_to_file )); then 
	    result_file="${last_capture_file}_grepped_by_${grep_host}_${PACKET_COUNT}_packets.pcap"
            additional_arguments_to_tcpdump="-w $result_file"
        else
            additional_arguments_to_tcpdump=" "
        fi
        sudo "$tcpdump" -tnr "$last_capture_file" host "$grep_host" -c "$PACKET_COUNT" "$additional_arguments_to_tcpdump" 2> /dev/null
	(( write_to_file )) && echo "Rsults written to $result_file"
    else
        die "Capture file $last_capture_file does not exist"
    fi
}


function usage {
    cat << EOF
    USAGE: $0 [-c | -t | -l | -g grep_host ] [-n packet_count] [-i interface]
                
            Capturing traffic
                -c                          # capture 
                -i interface                # network interface to use
                -n packet_count             # how many packets to capture

            Working with capture files/displaying results
                -l                          # list capture files
                -t                          # find top10 packet sources from the last capture file
                -g grep_host                # display only packets that match 'grep_host'
                -w                          # write 'grepped' results to a file instead of STDOUT 
                -n packet_count             # how many packets to capture

            Other
                -d                          # print additional debugging information

    Example:
            $0 -c                   # capture default amount of traffic on default interface
            $0 -c -i eth1 -n 10000  # capture 10000 packets on interface eth1
            $0 -t                   # display top10 packet sources by packet count
            $0 -g 127.0.0.1         # display packets from last capture that match host '127.0.0.1'
            $0 -n 10 -g 127.0.0.1   # display 10 packets from last capture that match host '127.0.0.1'
EOF
    exit
}


function list_capture_files {
    ls -lasht capture_*.pcap
}

function install_tcpdump {
    sudo apt-get -y install tcpdump
}


if [ ! -x /sbin/ip ]; then
    die "/sbin/ip not available, unsupported system"
fi


if [ -x /usr/sbin/tcpdump ]; then
    tcpdump=/usr/sbin/tcpdump
else
    echo "Tcpdump is not installed"
    while true; do
        read -p "Do you want to install it now? (y/n)" answer
        case $answer in
        y) install_tcpdump; break ;;
        n) die "Tcpdump not installed";;
        esac
    done
fi

if [ -z "$1" ]; then
    usage
fi

while getopts i:n:f:g:cltwhd opt
do
    case $opt in
    i)      INTERFACE=$OPTARG ;;
    n)      PACKET_COUNT=$OPTARG ;;
    l)      list_capture_files ;;
    c)      capture ;;
    t)      top_sources ;;
    g)      grep_host=$OPTARG; capture_grep ;;
    d)      DEBUG=1 ;;
    w)      write_to_file=1 ;;
    f)      capture_file_provided=1; capture_file_name=$OPTARG ;;
    h|?)    usage ;;
    esac
done

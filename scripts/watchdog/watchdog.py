#!/usr/bin/env python
"""
A wrapper around linux ping command that can trigger
some actions if a host is down.
"""

import subprocess
import argparse
import random
import time
import os
import sys

# if enabled, prints out additional debugging info,
# can be enabled with '-d' argument as well
DEBUG = False


def die(msg="Something bad happened", exitcode=1):
    "Print an error message and exit"
    print msg
    sys.exit(exitcode)


def parse_args():
    "Parse arguments"
    parser = argparse.ArgumentParser(description="Watchdog")
    parser.add_argument("-t", required=True, action="append", help="Target")
    parser.add_argument("-a", action="store", choices=["print", "reboot"],
                        default="print", help="Action")
    parser.add_argument("-d", action="store_true", help="Debug mode")
    return parser.parse_args()


def isup(exitcode):
    "Return a boolean value based on ping exit code"
    if exitcode == 0:
        return True
    else:
        return False


def am_i_root():
    if os.geteuid() == 0:
        return True
    return False


def action_print():
    "Dummy action, can be used when setting up the script"
    print "All the targets are down."


def action_reboot():
    "Simple reboot action, no checking of success is done"
    if not am_i_root():
        die("You have to be root in order to restart the system.")
    print "Rebooting the system!"
    subprocess.Popen("/sbin/reboot")
    # good luck with that


def take_action(action):
    "Call one of the 'action' commands"
    if action == "print":
        action_print()
    elif action == "reboot":
        action_reboot()
    else:
        die("Undefined action")


def ping(target, count):
    """
    Wrapper around linux ping command that will return a boolean value
    as its result.
    """
    ping_binary = "/bin/ping"
    if not os.path.exists(ping_binary):
        die("Cannot find the ping binary")
    # construct the ping commandline, set timeout to 1 second
    command = "{binary} -W 1 -c {count} {target}".format(
        binary=ping_binary, count=count, target=target)
    if DEBUG:
        print "Executing the following ping command"
        print command
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    exitcode = process.wait()

    if DEBUG:
        print "Output from ping command:"
        for line in process.stdout.readlines():
            print "->", line.strip()

    if isup(exitcode):
        return True

    return False


def sleep():
    """ Sleep for 5 to 10 seconds and return """
    sleep_time = random.choice(range(5, 11))
    if DEBUG:
        print "Sleeping for {0} seconds".format(sleep_time)
    time.sleep(sleep_time)


def main():
    global DEBUG
    args = parse_args()
    targets = args.t
    action = args.a
    DEBUG = args.d
    max_retry_times = 2
    for i in range(max_retry_times):
        # in case multiple targets have been specified only trigger action
        # if all of them are failing
        for target in targets:
            if ping(target, count=2):
                if DEBUG:
                    print "Target {0} is up. Exiting the loop.".format(target)
                # exit the loop if at least one host is up
                sys.exit(0)
        else:
            # sleep if the max retry count has not been reached yet
            if not (i+1) == max_retry_times:
                sleep()
    else:
        # if all the pings have failed, take the action
        take_action(action)


if __name__ == "__main__":
    main()

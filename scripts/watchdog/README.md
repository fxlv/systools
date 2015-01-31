Watchdog

Ping specified targets and reboot the machine if all the targets failed to repond to ping.

Multiple targets can be specified as well as potentially other actions can be taken.

It does 2 retries by default for each target.

Usage:

Reboot the machine if IP 8.8.8.8 is not reachable.
```
watchdog.py -t 8.8.8.8 -a reboot
```

Reboot the machine if all 3 targets are down
```
watchdog.py -t 8.8.8.8 -t 8.8.4.4 -t 208.67.222.222 -a reboot
```

For testing, the 'print' action (default) as well as '-d' argument can be used.
```
watchdog.py -t 8.8.8.8 -t 8.8.4.4 -t 208.67.222.222 -a print -d
```

To be useful it should be executed by cron.
For example
```
# reboot if both local network and internet appears unreachable
*/5 *   * * *   root    /usr/local/scripts/watchdog/watchdog.py -t 192.168.1.1 -t 8.8.8.8 -a reboot >> /var/log/reboot.log
```


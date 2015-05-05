#!/usr/bin/env python

# get max orphans value
with open("/proc/sys/net/ipv4/tcp_max_orphans") as tcp_max_orphans:
    max_orphans = tcp_max_orphans.readline().strip()

#TCP: inuse 7 orphan 0 tw 0 alloc 11 mem 0
with open("/proc/net/sockstat") as sockstat:
    for line in sockstat:
        if line.startswith("TCP"):
            line = line.strip().split()
            # ['TCP:', 'inuse', '7', 'orphan', '0', 'tw', '0', 'alloc', '11', 'mem', '0']
            tcp_sockets_inuse = line[2]
            tcp_orphans = line[4]
            tcp_mem = line[10]
        elif line.startswith("UDP:"):
            # UDP: inuse 5 mem 1
            line = line.strip().split()
            udp_sockets_inuse = line[2]
            udp_mem = line[4]


print "tcp.orphans=%s" % tcp_orphans
print "tcp.sockets_in_use=%s" % tcp_sockets_inuse
print "tcp.mem=%s" % tcp_mem
print "tcp.max_orphans=%s" % max_orphans
print "udp.sockets_in_use=%s" % udp_sockets_inuse
print "udp.mem=%s" % udp_mem

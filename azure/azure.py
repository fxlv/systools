#!/usr/bin/env python
#
# Python wrapper around azure-cli tools.
# Yes, it would be better to use the Azure REST CLI directly, but this was
# faster :)
#
# kaspars@fx.lv
import os
import re
import sys
import time
from subprocess import Popen, PIPE

DEBUG=False

class VM():
    "VM object"
    def __init__(self, name, status=None):
        self.name = name
        self.status = status

    def __str__(self):
        return self.name

    def __repr__(self):
        return "VM: {0}".format(self.name)


class Azure():

    def __init__(self):
        self.test = "test"

    def vm_list(self):
        process = Popen("azure vm list".split(), stdout=PIPE)
        if DEBUG:
            print "Waiting for process to finish",
            while process.poll() is None:
                time.sleep(1)
                print ".",
                sys.stdout.flush()
            print "Done."

        process.wait()
        header_ended = False
        vm_list = []
        for line in process.stdout.readlines():
            # look for the end of header which looks like this
            # data:    ---------------  ------------------  ------------
            line = line.strip().split()
            if DEBUG: 
                print "DEBUG: ", line
            if line[0] == "data:" and line[1] == "---------------":
                header_ended = True
                continue  # move on to the next line
            if header_ended:
                if line[0] == "data:":
                    if DEBUG:
                        print "valid line:", line
                    name = line[1]
                    status = line[2]
                    vm = VM(name, status)
                    vm_list.append(vm)
        return vm_list

    def vm_details(self, vm_name):
        dns_name = None
        location = None
        size = None
        image = None
        ipaddress = None
        endpoints = {}
        vips = {}
        cmd = "azure vm show {0}".format(vm_name) 
        process = Popen(cmd.split(), stdout=PIPE)
        if DEBUG:
            print "Waiting for process to finish",
            while process.poll() is None:
                time.sleep(0.5)
                print ".",
                sys.stdout.flush()
            print "Done."
        process.wait()
        lines = process.stdout.readlines()
        if len(lines) > 6:
            # assuming success
            for line in lines:
                line = line.strip()
                if line.startswith("data:"):
                    data = line.split(":")[1].strip()
                    if data.startswith("DNSName"):
                        dns_name = data.split("\"")[1]
                    if data.startswith("Location"):
                        location = data.split("\"")[1]
                    if data.startswith("IPAddress"):
                        ipaddress = data.split("\"")[1]
                        if len(ipaddress)<1:
                            ipaddress = None
                    if data.startswith("InstanceStatus"):
                        status = data.split("\"")[1]
                    if data.startswith("Image"):
                        image = data.split("\"")[1]
                    if data.startswith("InstanceSize"):
                        size = data.split("\"")[1]
                    # parse VirtualIPAddresses
                    if data.startswith("VirtualIPAddresses"):
                        r = re.match("VirtualIPAddresses ([0-9]+) name \"([0-9a-zA-Z\s]+)\"",data)
                        if r:
                            (vip, name) = r.groups()
                            if vip not in vips:
                                vips[vip] = {}
                            vips[vip]['name'] = name
                        r = re.match("VirtualIPAddresses ([0-9]+) address \"([0-9a-zA-Z\s]+)\"",data)
                        if r:
                            (vip, address) = r.groups()
                            if vip not in vips:
                                vips[vip] = {}
                            vips[vip]['address'] = address

                    # parse network endpoints
                    if data.startswith("Network Endpoints"):
                        r = re.match("Network Endpoints ([0-9]+) port ([0-9]+)",data)
                        if r:
                            (endpoint, port) =  r.groups()
                            if not endpoint in endpoints:
                                endpoints[endpoint] = {}
                            endpoints[endpoint]['port'] = port
                        r = re.match("Network Endpoints ([0-9]+) localPort ([0-9]+)",data)
                        if r:
                            (endpoint, local_port) =  r.groups()
                            if not endpoint in endpoints:
                                endpoints[endpoint] = {}
                            endpoints[endpoint]['local_port'] = local_port
                        r = re.match("Network Endpoints ([0-9]+) name \"([0-9a-zA-Z\s]+)\"",data)
                        if r:
                            (endpoint, endpoint_name) =  r.groups()
                            if not endpoint in endpoints:
                                endpoints[endpoint] = {}
                            endpoints[endpoint]['endpoint_name'] = endpoint_name
                        r = re.match("Network Endpoints ([0-9]+) protocol \"([0-9a-zA-Z\s]+)\"",data)
                        if r:
                            (endpoint, protocol) =  r.groups()
                            if not endpoint in endpoints:
                                endpoints[endpoint] = {}
                            endpoints[endpoint]['protocol'] = protocol
                        r = re.match("Network Endpoints ([0-9]+) virtualIPAddress \"([0-9\.]+)\"",data)
                        if r:
                            (endpoint, vip) =  r.groups()
                            if not endpoint in endpoints:
                                endpoints[endpoint] = {}
                            endpoints[endpoint]['vip'] = vip



            # OSDisk operatingSystem
            # ReservedIPName
            # VirtualIPAddresses 0 address "191.239.2..."
            # Network Endpoints 0 name "SSH"
            # Network Endpoints 0 port 22
            # Network Endpoints 0 protocol "tcp"
            vm = VM(vm_name)
            vm.dns_name = dns_name
            vm.location = location
            vm.ipaddress = ipaddress
            vm.status = status
            vm.image = image
            vm.size = size
            vm.endpoints = endpoints
            vm.vips = vips
        return vm


if __name__ == "__main__":
    # Testing 
    azure = Azure()
    print "VM list"
    print "*"*80
    for vm in azure.vm_list():
        print vm, vm.status, vm.name
    print "*"*80
    print "TEST: get details for VM 'fxad1'"
    print "*"*80
    vm = azure.vm_details("fxad1")
    print vm 
    print "DNS name:",vm.dns_name
    print "Location:",vm.location
    print "IPaddress:",vm.ipaddress
    print "status:",vm.status
    print "size:",vm.size
    print "Image:",vm.image
    print "Endpoints:",vm.endpoints
    print "Virtual IP addresses:",vm.vips
    print "*"*80
    print "TEST: get details for VM 'fxbuntu'"
    print "*"*80
    vm = azure.vm_details("fxbuntu")
    print vm 
    print "DNS name:",vm.dns_name
    print "Location:",vm.location
    print "IPaddress:",vm.ipaddress
    print "status:",vm.status
    print "size:",vm.size
    print "Image:",vm.image
    print "Endpoints:",vm.endpoints
    print "Virtual IP addresses:",vm.vips

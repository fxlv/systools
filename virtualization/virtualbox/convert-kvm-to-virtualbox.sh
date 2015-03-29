#!/bin/bash
# convert kvm image to virtualbox one
source=$1
target=$2
sudo qemu-img convert -O vdi $source ${target} -p
sudo chown ${USER} $target

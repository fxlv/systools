#!/bin/bash
#
# quick and simple way to 
# extract and create basic debian packages
#
command=$1
package=$2

if [ -z "$command" ]; then
echo "dpkg builder"
echo "usage: $0 build|extract <package file name>"
exit 1
fi

if [ "$command" == 'extract' ]; then
	if [ -z "$package" ]; then
	echo "Please provide package file as an argument"
	exit 1
	fi
mkdir -p extract/DEBIAN
dpkg-deb -x "$package" extract/
dpkg-deb -e "$package" extract/DEBIAN
elif [ "$command" == 'build' ]; then
mkdir build
dpkg-deb -b extract/ build/
fi

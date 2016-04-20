#!/bin/bash
#
# Sometimes when exporting/importing/cloning VirtualBox VMs
# VirtualBox will complain about clashing UUIDs.
#
# It's not a difficult problem to fix, you change the
# UUID of the vmdk file and the update the vbox xml for your VM.
#
# And that is exactly what this script does.
#
# Drop it into a directory that contains the VM and run it.
# It will then check that there's a .vbox file present and if so i
# update all the .vmdk UUIDs and update the .vbox file accordingly.
#

if [ -e /Applications/VirtualBox.app/Contents/MacOS/VBoxManage ]; then
    vboxmanage="/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
else
    echo "Where's VBoxManage?"
    exit 1
fi

# check that there's only one .vbox file present in the current directory
# and check that at least one .vmdk file is present otherwise nothing we can do here
vbox_files_count=$(find . -name "*.vbox" | wc -l|tr -d " " )
vmdk_files_count=$(find . -name "*.vmdk" | wc -l|tr -d " " )

if [ $vmdk_files_count -lt 1 ]; then
    echo "There has to be at least one .vmdk file in the current directory"
    echo "Exiting, as there's nothing to be done here."
    exit 1
fi

if [ $vbox_files_count -eq 1 ]; then
    vbox_vm=$(find . -name "*.vbox")
    vbox_vm=$(basename $vbox_vm)
    echo "Will update $vbox_vm file"
else
    echo "Cannot find the .vbox file."
    echo "Please check the script for usage details."
    exit 1
fi

# prepare names for backup and temporary vbox files
vbox_vm_backup="${vbox_vm}.bak"
vbox_vm_tmp="${vbox_vm}.tmp"
cp -v $vbox_vm $vbox_vm_backup

echo "Will change UUIDs in vm: $vbox_vm"

# find all the .vhd files and update their UUIDs
# once UUID is changed, also update it accordingly in the .vbox file
for file in *.vmdk; do
    echo $file
    newuuid_result=$($vboxmanage internalcommands sethduuid $file)
    if echo $newuuid_result | grep -q changed; then
        echo "Change OK"
        newuuid=$(echo $newuuid_result | cut -d ":" -f 2|tr -d " ")
        echo "New UUID: $newuuid"
        # now, find the old UUID
        old_uuid=$(grep "HardDisk uuid" $vbox_vm | grep "$file" | cut -d "\"" -f 2|tr -d "{}")
        echo "Old UUID: $old_uuid"
        sed "s/$old_uuid/$newuuid/g" $vbox_vm > "$vbox_vm_tmp"
        mv -v $vbox_vm_tmp $vbox_vm
    fi
done




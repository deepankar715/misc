#!/bin/python

'''This code clones a virtual machine from virt-manager along with all of its
snapshots. That's it.
Minimal testing done, if you find something weird or missing or broken then lemme know.'''

# Import modules
import xml.etree.ElementTree as ET
import argparse
import subprocess as sp
import os
import string

def parse_argvs():
    '''Function to parse command line arguments, offer help messages and overall make the program more intuitive to use.'''

    help = """
    Copies the snapshots of the machine after it has been cloned in virt-manager.
    Run the program after the machine has been cloned.
    Make sure the machine is not in a running state.
    """
    parser = argparse.ArgumentParser(description=help)

    help = "Name of the original Virtual Machine"
    parser.add_argument("old_name", type=str, help=help, metavar="Old_VM")

    help = "Name of the cloned Virtual Machine"
    parser.add_argument("new_name", type=str, help=help, metavar="New_VM")

    args = parser.parse_args()

    return args;

def sanatize(args):
    '''Sanitary function to make sure that machine exists and to filter malicious inputs like "clone_name; rm -rf /" '''

    # Machine to clone should be present in the list of all the machines in our environment.
    machine_list = []
    virsh_list = sp.check_output("virsh list --all", shell=True).decode().split("\n")
    for i in range(2,len(virsh_list)-2):
        machine_list.append(virsh_list[i].split()[1])
    if args.old_name not in machine_list:
        print(f"{args.old_name} machine does not exist. Try something else. Exiting")
        exit(1)

    # Only allow certain characters while naming the clone.
    whitelist = string.ascii_letters + string.digits + "\t -_."
    for letter in args.new_name:
        if letter not in whitelist:
            print("Argument(s) contains illegal characters. Only numbers, letters, space, ., - and _ are allowed. Exiting")
            exit(1)

    else:
        pass

def get_from_xml(domain):
    '''Extracts certain necessary information from the xml definiton of the machine'''

    # Returns name, uuid, mac address and path of the inputted machine.
    # The information that is necessary to change in the snapshot definitons.
    xml = sp.check_output(f"virsh dumpxml {domain}", shell=True).decode()
    root = ET.fromstring(xml)
    values = {
        "name": root[0].text,
        "uuid": root[1].text,
        "mac": root[13][9][0].attrib['address'],
        "path": root[13][1][1].attrib['file'] }
    return values

def vm_clone(old_name, new_name):
    '''Function to clone a machine'''

    vm_path = "/".join(get_from_xml(old_name)["path"].split("/")[:-1]) # path of the machine to be cloned.
    virt_clone = f'virt-clone --original {old_name} --name {new_name} --file {vm_path}/{new_name}.qcow2'
    os.system(virt_clone)


def restore_snapshot(old_domain, new_domain):
    '''Copies the snapshots of first machine, replace the necessary fields from the xml and redefines it for the newly cloned machine'''

    # It is assumed that we're using qemu, that's why the path of snapshots is hardcoded.
    # This path will be different for different hypervisors, for example /var/lib/libvirt/xen/snapshot.
    # But well I have only included qemu because
    snapshot_path = "/var/lib/libvirt/qemu/snapshot"
    snapshots = []
    old_snapshot_xmls = []
    new_snapshot_xmls = []

    # List the snapshots.
    virsh_snapshot_list = sp.check_output(f"virsh snapshot-list {old_domain}", shell=True).decode().split("\n")
    for i in range(2,len(virsh_snapshot_list)-2):
        snapshots.append(virsh_snapshot_list[i].split()[0])

    old_snapshot_dir = f"{snapshot_path}/{old_domain}/"
    if not os.path.exists(old_snapshot_dir):
        os.makedirs(old_snapshot_dir)
    for snapshot in snapshots:
        with open(f"{old_snapshot_dir}/{snapshot}.xml", "r") as file:
            old_snapshot_xmls.append(file.read()) # array for xmls of all the snapshots.

    old_parameters = get_from_xml(old_domain)
    new_parameters = get_from_xml(new_domain)

    # Replace the information.
    for xmls in old_snapshot_xmls:
        temp_xml = xmls.replace(old_parameters["name"], new_parameters["name"])
        temp_xml = temp_xml.replace(old_parameters["uuid"], new_parameters["uuid"])
        temp_xml = temp_xml.replace(old_parameters["mac"], new_parameters["mac"])
        temp_xml = temp_xml.replace(old_parameters["path"], new_parameters["path"])
        new_snapshot_xmls.append(temp_xml)

    # Write the information.
    new_snapshot_dir = f"{snapshot_path}/{new_domain}"
    if not os.path.exists(new_snapshot_dir):
        os.makedirs(new_snapshot_dir)
    for n in range(len(new_snapshot_xmls)):
        with open(f"{new_snapshot_dir}/{snapshots[n]}.xml", "w+") as file:
            file.write(new_snapshot_xmls[n])

    # Redefine the snapshots for the new clone.
    for snapshot in snapshots:
        os.system(f"virsh snapshot-create {new_domain} {new_snapshot_dir}/{snapshot}.xml --redefine")

def main():
    '''Main function that calls all the other functions'''

    args = parse_argvs()
    sanatize(args)
    print("Input sanity check passed, inputs accepted")

    vm_clone(args.old_name, args.new_name)
    restore_snapshot(args.old_name, args.new_name)

if __name__ == '__main__':
    main()

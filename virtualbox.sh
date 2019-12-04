#!/bin/bash

# script for installing virtualbox on centos
# rport errors and improvements and bugs and everything else to 'dep1943008@sicsr.ac.in'
# run as sudo or root

yum install -y kernel-devel kernel-headers gcc make perl wget dnf 'dnf-command(config-manager)' elfutils-libelf-devel
rpm --import https://www.virtualbox.org/download/oracle_vbox.asc
dnf config-manager --add-repo=https://download.virtualbox.org/virtualbox/rpm/el/virtualbox.repo
dnf install -y VirtualBox-6.0
virtualbox

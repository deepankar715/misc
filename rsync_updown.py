#!/bin/python

"""
Script for uploading - downloading files from one directory on my phone to one on my laptop.
I'm using an app called sshelper which creates sftp connection from phone to laptop using ssh, and it supports rsync.
Need to establish a connection first before running the script.
"""

import os, sys

def upload(ip):
    os.system(f"rsync -azv --no-perms --no-times --size-only /home/$USER/rsync/rsync/* /run/user/1000/gvfs/sftp:host={ip},port=2222/data/data/com.arachnoid.sshelper/home/SDCard/rsync")

def download(ip):
    os.system(f"rsync -azv --no-perms --no-times --size-only /run/user/1000/gvfs/sftp:host={ip},port=2222/data/data/com.arachnoid.sshelper/home/SDCard/rsync /home/$USER/rsync/ ")

def main():
    if sys.argv[1] == '--help':
        print("""
        Usage: ./rsync_updown.py [mode] [ip address]
        Modes:
        -d : for downloading
        -u : for uploading
            """)
    elif len(sys.argv) != 3:
        print("see usage --help")
    else:
        if sys.argv[1] == '-d':
            mode = "download"
        elif sys.argv[1] == '-u':
            mode = "upload"
        elif sys.argv[1] == '--help':
            print("""
            Usage: ./script.py [mode] [ip address]
            Modes:
            -d : for downloading
            -u : for uploading
                """)
        else:
            print("see usage --help")

        if mode == "upload":
            upload(sys.argv[2])
        if mode == "download":
            download(sys.argv[2])

if __name__ == '__main__':
    main()

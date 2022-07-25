#!/usr/bin/python

import os
import subprocess
import sys

if len(sys.argv) < 2:
    print('usage:\n   \033[1mbackup.py\033[22m /path/to/backup.sqfs\n')
    print('to backup archive (once), use\n  mksquashfs ~/archive /path/to/archive.sqfs -comp lz4 \n')
    exit()

subprocess.call([argument.replace('~', os.path.expanduser('~')) for argument in ("""mksquashfs
~/👣
~/audio
~/bin/tunnel_ipv6.sh
~/desktop
~/documentation
~/graphics
~/repo
~/setup
~/work
~/.bash_history
~/.config/vivaldi/
~/.ssh/
~/.thunderbird/
"""+sys.argv[1]+"""
-comp
lz4
-no-strip
-wildcards
-e
node_modules
""").split('\n')])

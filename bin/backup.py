#!/usr/bin/python

import os, subprocess, sys

if len(sys.argv) < 2:
    print('usage:\n   \033[1mbackup.py\033[22m /path/to/backup.sqfs')
    exit()

# ~/👣
# ~/audio
# ~/bin/tunnel_ipv6.sh
# ~/desktop
# ~/documentation
# ~/graphics
# ~/repo
# ~/setup
# ~/work
# ~/.bash_history
# ~/.config/vivaldi/
# ~/.ssh/
# ~/.thunderbird/

subprocess.call([argument.replace('~', os.path.expanduser('~')) for argument in ("""mksquashfs
~
"""+sys.argv[1]+"""
-comp
lz4
-wildcards
-e
... node_modules
!(👣|audio|desktop|documentation|graphics|repo|setup|work|.bash_history|.ssh|.thunderbird|bin|.config)
bin/!(tunnel_ipv6.sh)
.config/!(vivaldi)
""").split('\n')])





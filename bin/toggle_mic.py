#!/usr/bin/python

import subprocess

# amixer get Capture
output = subprocess.run('amixer set Capture toggle'.split(),
                        encoding='UTF-8', capture_output=True).stdout
subprocess.run(['notify-send', '-t', '400', 'mic %s' %
               ('off' if output.find('[off]') != -1 else 'on')])

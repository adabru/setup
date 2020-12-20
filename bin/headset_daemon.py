#!/usr/bin/env python

# add user to group 'input' to get access to /dev/input/event*
# sudo usermod -a -G input $USER

from re import compile
from os import geteuid
from subprocess import Popen, PIPE, call

if geteuid() == 0:
  print("Must be run as user to receive notifications. Add user to group 'input', `sudo usermod -a -G input $USER`.")
  exit()

# find out the event number with running `sudo evtest` and looking for "HDA Intel PCH Headphone"
# p = Popen(["evtest", '/dev/input/event14'], stdout=PIPE)

p = Popen(['evtest'], stdout=PIPE, stdin=PIPE, stderr=PIPE)

# select 'HDA Intel PCH Headphone'; loop will block forever if no match is found
eventmask = compile('/dev/input/event([\d]+).*HDA Intel PCH Headphone')
eventX = None
for line in p.stderr:
  match = eventmask.match(line.decode('utf-8'))
  if match != None:
    eventX = match.group(1)
    p.stdin.write((eventX + '\n').encode())
    p.stdin.flush()
    break
  # # following doesn't work as the line is not read because no line break
  # if line.decode('utf-8').startswith('Select the device event number'):
  #   break

if eventX == None:
  print('no device "HDA Intel PCH Headphone" found, checkout output of running `evtest`')
  exit()

# reading from process
# https://stackoverflow.com/a/28319191/6040478
mask = compile('SW_HEADPHONE_INSERT.*value 1')
for line in p.stdout:
  if mask.search(line.decode('utf-8')) != None:
    print('plugged in')
    call(['notify-send', '-t', '500', 'Headset'])
    call(['amixer', 'set', 'Internal Mic Boost', '70%'])



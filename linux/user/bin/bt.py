#!/usr/bin/python

import subprocess, re, sys, termios, tty

print('powering bluetooth (bluetoothctl power on)...')
if subprocess.run('bluetoothctl power on'.split(), encoding='UTF-8').returncode != 0:
  exit()

listdev = subprocess.run('bluetoothctl devices'.split(), encoding='UTF-8', capture_output=True)
devices = []
for line in listdev.stdout.strip().split('\n'):
  devices.append(re.compile('Device ([\S]+) (.+)').search(line).groups())

def getch():
  fd = sys.stdin.fileno()
  old_settings = termios.tcgetattr(fd)
  try:
      tty.setraw(fd)
      ch = sys.stdin.read(1)
  finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
  return ch

if len(devices) > 0:
  print('Choose device (press key):')
  for i, dev in enumerate(devices):
    print('   \033[35m{:}\033[39m) {:} \033[33m{:}\033[39m'.format(i, dev[1].ljust(20), dev[0]))
  print('   \033[35m{:}\033[39m) \033[33m{:}\033[39m'.format(len(devices), 'scan'))
  c = getch()
  try:
    if int(c) >= 0 and int(c) < len(devices):
      print(devices[int(c)][1])
      poweron = subprocess.run('bluetoothctl connect {:}'.format(devices[int(c)][0]).split(), encoding='UTF-8')
    elif int(c) == len(devices):
      print("""\nuse
      \033[1mbluetoothctl scan on\033[22m
      \033[1mbluetoothctl connect\033[22m <UUID>
      """)
      # https://stackoverflow.com/questions/36607626
      # rescan already scanned devices via `bluetoothctl → menu scan → clear / duplicate-data on`
  except ValueError:
    pass


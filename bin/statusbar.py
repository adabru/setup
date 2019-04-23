#!/usr/bin/python

import time, datetime, sys, re, subprocess, asyncio

def cat(file):
  f = open(file,"r")
  res = f.read()
  f.close()
  return res

lastCpu = None
ping = '∞'
def status():
  global lastCpu, ping
  # see https://i3wm.org/docs/i3bar-protocol.html
  print('[')

  # wireless network
  network = subprocess.run('iwgetid --raw'.split(), encoding='UTF-8', capture_output=True).stdout.strip()
  print('{{"color":"#8888ff", "full_text":"{:}"}},'.format(network))

  # ping
  print('{{"color":"#8888ff", "full_text":"{:}ms"}},'.format(ping))

  # free memory
  regex = re.compile('MemAvailable: *([0-9]+).*SwapFree: *([0-9]+)', re.S)
  m = regex.search(cat('/proc/meminfo'))
  mem, swap = int(m.group(1)), int(m.group(2))
  color = mem < 1e6 and '#ff5555' or '#bbbbbb'
  print('{{"color":"{:}", "full_text":"{:.1f} {:.1f}"}},'.format(color, mem/1e6, swap/1e6))

  # cpu load
  def cpu():
    def sum(line):
      x = line.split()
      return ( int(x[1]) + int(x[2]) + int(x[3]) + int(x[6]) + int(x[7]) + int(x[8]) + int(x[9]) + int(x[10]),
              int(x[4]) + int(x[5]) )
    return [sum(line) for line in cat('/proc/stat').split('\n')[1:5]]
  def cpuload(curr, last):
    return '{:3.0%}'.format( float(curr[0]-last[0]) / (curr[0]-last[0]+curr[1]-last[1]+1) )
  currCpu = cpu()
  if lastCpu == None:
    lastCpu = currCpu
  print('{{"color":"#bbbbbb88", "full_text":"{:}"}},'.format(
    ' '.join( [cpuload(curr, last) for curr, last in zip(currCpu, lastCpu)] ) ))
  lastCpu = currCpu

  # battery status
  battery = ( float(cat('/sys/class/power_supply/BAT1/energy_now'))
    / float(cat('/sys/class/power_supply/BAT1/energy_full')) )
  color = ( int(cat('/sys/class/power_supply/ACAD/online')) and '#bbbbbb'
    or  battery > .3 and '#77bb77' or battery > .15 and '#dddd88' or '#ff5555' )
  print('{{"color":"{:}", "full_text":"{:.1f}"}},'.format(color, 100*battery))

  # date and time
  print('{{"color":"#bbbbbb", "full_text":"{:}"}}'.format(datetime.datetime.now().strftime("%Y-%m-%d W%V   %H:%M:%S")))

  print('],')
  sys.stdout.flush()


# start ping
async def getping():
  global ping
  while True:
    await asyncio.sleep(1)
    proc = await asyncio.create_subprocess_exec(*'ping -nc 1 -W 2 adabru.de'.split(), stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    m = re.compile('time=([0-9]+)').search(stdout.decode())
    if m:
      ping = m.group(1)
    else:
      ping = '>2000'

async def printstatus():
  print('{"version":1}')
  print('[')
  while True:
    status()
    await asyncio.sleep(.5)

async def main():
  await asyncio.gather(getping(), printstatus())
asyncio.run(main())


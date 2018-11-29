#!/usr/bin/env python

import sys, subprocess

print(sys.argv)
if len(sys.argv) == 1:
  # copy stdin to clipboard and clipboard primary
  copy1 = subprocess.Popen(["wl-copy"], stdin = subprocess.PIPE)
  copy2 = subprocess.Popen(["wl-copy", "-p"], stdin = subprocess.PIPE)

  while True:
    input = sys.stdin.buffer.read(1024)
    if input:
      copy1.stdin.write(input)
      copy2.stdin.write(input)
    else:
      break

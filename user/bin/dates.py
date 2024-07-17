#!/usr/bin/env python

# sources:
# https://techoverflow.net/2019/05/16/how-to-iterate-all-days-of-year-using-python/
# https://stackoverflow.com/a/9847269/6040478

from collections import namedtuple
from calendar import monthrange
import datetime
import sys

if len(sys.argv) != 2:
  print('usage:\n\n  dates.py 2018')
  exit()

year = int(sys.argv[1])

for month in range(1, 13): # Month is always 1..12
  for day in range(1, monthrange(year, month)[1] + 1):
    weekday = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'][datetime.datetime(year, month, day).weekday()]
    print('::\n {:} {:02}-{:02}'.format(weekday, month, day))

#!/usr/bin/python

# https://github.com/rg3/youtube-dl/issues/622

import sys
import subprocess
import re
import os

if len(sys.argv) == 1:
    print(
        """
  usage

  \033[1myt\033[22m url                                    show available formats
  \033[1myt\033[22m url format name                        download full
  \033[1myt\033[22m format 00:12:00 00:13:00 name url      download portion
  """
    )


if len(sys.argv) == 2:
    if sys.argv[1] == "-f":
        print("jolo")
    else:
        subprocess.run("yt-dlp -F {:}".format(sys.argv[1]).split(), encoding="UTF-8")
elif len(sys.argv) == 4:
    subprocess.run(
        "yt-dlp -f {:} -o _tmp_%(id)s.%(ext)s {:}".format(
            sys.argv[2], sys.argv[1]
        ).split(),
        encoding="UTF-8",
    )
    vfile = [x for x in os.listdir() if x.startswith("_tmp_")][0]
    os.rename(vfile, sys.argv[3] + os.path.splitext(vfile)[1])
#   else
#     ffmpeg -ss $2 -i $(youtube-dl -f $1 -g "$5") -t $3 -c copy $4.mp4
#   fi
# }

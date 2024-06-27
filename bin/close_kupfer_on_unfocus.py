#!/usr/bin/env python

# written after: https://gist.github.com/ckafi/0a5b79105c8301466cc324a08200aad7

import subprocess
import json

# swaymsg -t subscribe '["window"]' -m
process = subprocess.Popen(
    ["swaymsg", "-t", "subscribe", "['window']", "-m"],
    stdout=subprocess.PIPE,
)
print("Listening for window events...")

while True:
    # each event is formatted as a json object in a single line
    line = process.stdout.readline()
    if line == "":
        # EOF
        break
    else:
        deserialized = json.loads(line)
        if (
            deserialized["change"] == "focus"
            and deserialized["container"]["app_id"] != "kupfer.py"
        ):
            # swaymsg "[app_id=kupfer.py]" kill
            print("kill kupfer window")
            subprocess.Popen(["swaymsg", "-q", "[app_id=kupfer.py]", "kill"])

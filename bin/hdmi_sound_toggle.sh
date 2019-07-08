#!/bin/bash

# see https://wiki.archlinux.org/index.php/PulseAudio/Examples#Automatically_switch_audio_to_HDMI

# see `pactl list cards`
if [ /sys/class/drm/card0/card0-HDMI-A-1/status == connected ] ; then
  echo "hdmi"
  pactl --server "unix:/run/user/1000/pulse/native" set-card-profile 0 output:hdmi-stereo+input:analog-stereo
else
  echo "analog"
  pactl --server "unix:/run/user/1000/pulse/native" set-card-profile 0 output:analog-stereo+input:analog-stereo
fi

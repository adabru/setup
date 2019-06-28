#!/usr/bin/sh

mkdir -p "$HOME/mnt/${1##*/}" && squashfuse "$1" "$HOME/mnt/${1##*/}"

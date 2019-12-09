#!/usr/bin/sh

if [ -z "$1" ]
  then echo "first parameter must be path to squashfs archive"
  exit
fi
mkdir -p "$HOME/mnt/${1##*/}" && squashfuse "$1" "$HOME/mnt/${1##*/}" \
  && echo "mounted at $HOME/mnt/${1##*/}"


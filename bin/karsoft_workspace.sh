#!/bin/bash

# sudo -E visudo
# add line `Defaults !tty_tickets`
# https://unix.stackexchange.com/a/93459/218172
sudo -v

sudo grep "^Defaults \!tty_tickets" /etc/sudoers
if [[ $? != 0 ]]; then
  echo "Please add line 'Defaults !tty_tickets' to /etc/sudoers with 'sudo -E visudo'"
fi

tmux new-window -n dock "bash --rcfile <(echo '. ~/.bashrc;sudo dockerd')"
tmux new-window -n desk "bash --rcfile <(echo '. ~/.bashrc;cd ~/work/armin;. config.sh ; cd local/Kar-Soft_Desktop')"
tmux new-window -n back "bash --rcfile <(echo '. ~/.bashrc ; cd ~/work/armin ; . config.sh ; cd local/Kar-Soft_Backend')"
tmux new-window -n andr "bash --rcfile <(echo '. ~/.bashrc ; cd ~/work/armin ; . config.sh ; cd local/Kar-Soft_Android')"
tmux new-window -n k "bash --rcfile <(echo '. ~/.bashrc ; cd ~/work/armin ; . config.sh')"

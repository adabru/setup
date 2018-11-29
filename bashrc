

if [ $(tty) = "/dev/tty1" ]; then
  export XKB_DEFAULT_LAYOUT=ab
  export XKB_DEFAULT_OPTIONS=compose:menu
  export PATH=~/bin:$PATH
  # export QT_QPA_PLATFORM=wayland-egl
  sway
	exit 0
fi

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if [ -f /usr/share/bash-completion/bash_completion ]; then
  . /usr/share/bash-completion/bash_completion
elif [ -f /etc/bash_completion ]; then
  . /etc/bash_completion
fi

# history
HISTSIZE=10000
HISTFILESIZE=10000
HISTCONTROL=ignoreboth:erasedups
shopt -s histappend
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

# prompt
col() {
  printf "\[\e[48;2;%d;%d;%dm\]\[\e[38;2;%d;%d;%dm\]" 0x${1:0:1}0 0x${1:1:1}0 0x${1:2:1}0 0x${1:3:1}0 0x${1:4:1}0 0x${1:5:1}0
  # printf "\e[48;2;%d;%d;%dm\e[38;2;%d;%d;%dm" 0x${1:0:1}0 0x${1:1:1}0 0x${1:2:1}0 0x${1:3:1}0 0x${1:4:1}0 0x${1:5:1}0
}

_time=$(date "+%s%N")
time_=$(date "+%s%N")
prompt() {
  local error="$?"
  local c1a=$(col 600300)
  local c1b=$(col 600c00)
  local c2=$(col 630f90)
  local normal="\[\e[39m\]\[\e[49m\]\[\e[27m\]"

  time_=$(date "+%s%N")
  local time=$((${time_}-${_time}))
  time_="${_time}"
  local                                fmt="${c1a}%02dh%02dm%02ds${c1b}%03dms${c1a}"
  [[ "${time}" -gt 1000000000    ]] && fmt="${c1a}%02dh%02dm${c1b}%02ds${c1a}%03dms"
  [[ "${time}" -gt 60000000000   ]] && fmt="${c1a}%02dh${c1b}%02dm${c1a}%02ds%03dms"
  [[ "${time}" -gt 3600000000000 ]] && fmt="${c1a}${c1b}%02dh${c1a}%02dm%02ds%03dms"
  time="$(printf "${fmt}" $((time/3600000000000)) $((time/60000000000%60)) $((time/1000000000%60)) $((time/1000000%1000)))"
  _time=$(date "+%s%N")

  git_prompt_vars
  if [[ ${error} -ne 0 ]] ;then
    PS2="$(col 500f00)⋕ ${normal}"
  else
    PS2="${c2}${git_color}⊚ ${normal}"
  fi
  printf "\e]0;${PWD}\007"
  PS1="${time}${c2} \W ${git_color}${branch}${PS2}"
}
git_prompt_vars() {
  if [[ -f .git/HEAD ]] || \
    ( which git &> /dev/null && [[ -n "$(git rev-parse --is-inside-work-tree 2> /dev/null)" ]] ); then
    local ref=$(git symbolic-ref -q HEAD 2> /dev/null)
    if [[ -z "${ref}" ]]; then
      git_color=${red}
      branch="${red} HEAD:detached "
    else
      branch=" ${ref#refs/heads/} "
      local status=$(git status --porcelain -b)
      local ahead_re='.+ahead ([0-9]+).+'
      local behind_re='.+behind ([0-9]+).+'
      [[ "${status}" =~ ${ahead_re} ]] && branch+="↑${BASH_REMATCH[1]} "
      [[ "${status}" =~ ${behind_re} ]] && branch+="↓${BASH_REMATCH[1]} "
      if [[ $(echo "${status}" | wc -l) -gt 1 ]]; then
        git_color=$(col 534c0a)
      elif [[ $(echo "${status}" | wc -w) -gt 2 ]]; then
        git_color=$(col 633f08)
      else
        git_color=$(col 650fe0)
      fi
    fi
  else
    git_color=""
    branch=""
  fi
}
PROMPT_COMMAND=prompt

export EDITOR=vim

# aliases & vars
alias grep='grep --color=auto'
alias ls='ls --color=auto'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias apts='apt-cache search'
alias apti='sudo apt-get install -V'
alias aptu='sudo apt-get update'
alias aptrm='sudo apt-get remove'
alias less='less -r'
alias ..='cd ..'
alias ...='cd ../..'
alias chx='chmod +x'
alias tree2='tree -L 2'
alias mymount='sudo mount -o gid=users,fmask=113,dmask=002'

alias pacman='sudo pacman --color auto'
alias update='sudo pacman -Syyu'
# yay as aur helper - updates everything
alias pksyua="yay -Syu --noconfirm"

#get fastest mirrors in your neighborhood
alias mirror="sudo reflector --protocol https --latest 50 --number 20 --sort rate --save /etc/pacman.d/mirrorlist"
alias mirrors=mirror

# python
# python virutal env breaks many pacman-installed programs
. /home/adabru/.virtualenv/bin/activate
export PYTHONSTARTUP=$HOME/.pythonrc

# nodejs
export NVM_DIR="/home/adabru/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
[[ -r $NVM_DIR/bash_completion ]] && . $NVM_DIR/bash_completion
export PATH=./node_modules/.bin:$PATH

# java
# [ -s "/home/adabru/.jabba/jabba.sh" ] && source "/home/adabru/.jabba/jabba.sh"
# export SDKMAN_DIR="/home/adabru/.sdkman"
# [[ -s "/home/adabru/.sdkman/bin/sdkman-init.sh" ]] && source "/home/adabru/.sdkman/bin/sdkman-init.sh"


# rvm
[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm"
export PATH="$PATH:$HOME/.rvm/bin"

# git
alias ga='git add'
alias gall='git add -A'
alias gd='git diff --ws-error-highlight=all'
alias gus='git reset HEAD'
alias gs='git status'
alias gl='git pull'
alias gp='git push'
alias gc='git commit -v'
alias gb='git branch'
alias gco='git checkout'
alias gcb='git checkout -b'
alias glog="git log --pretty=format:'%C(bold)%h %C(cyan)%cr %C(reset)%C(yellow)%an %C(reset) %s %C(green)%d' --graph --decorate"


# long running commands
beep() { if [ $? == 0 ]; then paplay /usr/share/sounds/ubuntu/notifications/Positive.ogg
                         else paplay /usr/share/sounds/ubuntu/notifications/Blip.ogg      ;fi }
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'


alias pan+='xrandr --output LVDS1 -s 1366x768 --panning 1366x2048'
alias pan++='xrandr --output LVDS1 -s 1366x768 --panning 2048x2048'
alias pan-='xrandr --output LVDS1 --panning 0x0'
gamma() { xrandr --output LVDS1 --gamma $1:$1:$1; }
bright() { xrandr --output LVDS1 --brightness $1; }
gambri() { xrandr --output LVDS1 --gamma $1:$1:$1 --brightness $2; }
copy() { (if [ -f "$1" ]; then cat $1; else printf "$1"; fi;) | xclip -sel p -f | xclip -sel c; }

alias h='history'
alias doc='cd ~/repo/adabru-markup/ ; ./html/js/server.ls -d ~/portable/documentation --cache ~/.cache/adabru-markup'
alias nnn='export EDITOR=vim ; nnn'
c() {
for b in {40..47} {100..107} ; do
  for f in {30..37} {90..97} ; do
    for m in 1 22 2 ; do
      printf "\e[${b}m\e[${f}m\e[${m}ma\e[49m\e[39m\e[22m"
    done
  done
  printf "\n"
done
echo -n -e \
  '\\e \\033' \
  '\n\e[30m \\e[30m \e[31m \\e[31m \e[32m \\e[32m \e[33m \\e[33m \e[34m \\e[34m' \
  '\e[35m \\e[35m \e[36m \\e[36m \e[37m \\e[37m \e[39m \\e[39m' \
  '\n\e[90m \\e[90m \e[91m \\e[91m \e[92m \\e[92m \e[93m \\e[93m \e[94m \\e[94m' \
  '\e[95m \\e[95m \e[96m \\e[96m \e[97m \\e[97m \e[39m \\e[39m' \
  '\n\e[40m \\e[40m \e[41m \\e[41m \e[42m \\e[42m \e[43m \\e[43m \e[44m \\e[44m' \
  '\e[45m \\e[45m \e[46m \\e[46m \e[47m \\e[47m \e[49m \\e[49m' \
  '\n\e[100m \\e[100m \e[101m \\e[101m \e[102m \\e[102m \e[103m \\e[103m \e[104m \\e[104m' \
  '\e[105m \\e[105m \e[106m \\e[106m \e[107m \\e[107m \e[49m \\e[49m' \
  "\n\e[0m \\\\e[0m $test" \
  "\n\e[1m \\\\e[1m $test \e[22m \\\\e[22m" \
  "\n\e[2m \\\\e[2m $test \e[22m \\\\e[22m" \
  "\n\e[3m \\\\e[3m $test \e[23m \\\\e[23m" \
  "\n\e[4m \\\\e[4m $test \e[24m \\\\e[24m" \
  "\n\e[7m \\\\e[7m $test \e[27m \\\\e[27m" \
  "\n\e[8m \\\\e[8m $test \e[28m \\\\e[28m" \
  "\n\e[9m \\\\e[9m $test \e[29m \\\\e[29m" \
  "\n\e[?5h \\\\e[?5h flash " && sleep 0.1 && echo -e "\e[?5l \\\\e[?5l"
}
x() {
  (nohup >/dev/null $@ 2>&1 >/dev/null &)
}
complete -F _command x
gopen() {
  x geany $(f $@)
}
bench() {
  benchmark.py -r 5 "$@"
}

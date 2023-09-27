# ~/.zprofile

# shellcheck disable=SC1090  # Can't follow non-constant source


# Grow Sh Path

export PATH=$PATH:$HOME/bin


# Name the next Pwd:  -, .., ~

alias -- -='echo + cd - >&2 && cd -'
alias ..='echo + cd .. >&2 && cd .. && (dirs -p |head -1)'
alias ~='echo + cd "~" >&2 && cd ~ && (dirs -p |head -1)'

: setopt AUTO_CD  # Zsh  # lacks tab-completion
: shopt -s autocd 2>/dev/null  # Bash


# Make the Editing of Command-Line Input History less painful

setopt histverify  # Preview ! History Expansion  # a la Bash:  shopt -s histverify

stty -ixon  # let Sh ⌃S mean undo ⌃R  # don't take ⌃Q and ⌃S as XOn/ XOff


# Eagerly autocorrect some inputs
#
# Work well inside macOS Terminal
# Work like macOS > System Settings > Keyboard > Replace
# Work like iOS > Settings > General > Keyboard > Text Replacement
#


alias %%='echo -n "%%   ⌃ ⌥ ⇧ ⌘   # £   ← ↑ → ↓ ⎋ ⏎ ⇥ ⇤   ⋮ ·" |tee >(pbcopy) && echo'

function :scf: () { echo 'supercalifragilisticexpialidocious' |tee >(pbcopy); }
function :shrug: () { echo '¯\_(ツ)_/¯' |tee >(pbcopy); }


# Adopt the l, la, ll convention from Ubuntu

function l () {
    echo "+ alias l='ls -CF'" >&2
    alias l='ls -CF'
    return 1
}

function la () {
    echo "+ alias la='ls -A'" >&2
    alias la='ls -A'
    return 1
}

function ll () {
    echo "+ alias ll='ls -alF'" >&2
    alias ll='ls -alF'
    return 1
}


# Sandbox Python Extensions

function pips () {
    echo + source ~/.pyvenvs/pips/bin/activate >&2
    source ~/.pyvenvs/pips/bin/activate >&2
}


# Work the deep magic inside the Sh Process that Git SubProcesses can't reach,
# provided that $(which q) is a Sh File, not a Sh Func

# history -t '%b %d %H:%M:%S' 0
function zh () { d=$(which q); d=$(dirname "$d"); source "$d"/zh.source "$@"; }

# cd, popd
function qcd () { d=$(which q); d=$(dirname "$d"); source "$d"/qcd.source "$@"; }
function qp () { d=$(which q); d=$(dirname "$d"); source "$d"/qp.source "$@"; }

# "${ALTPWDS[@]}"
function eqol () { d=$(which q); d=$(dirname "$d"); source "$d"/eqol "$@"; }
function qo () { d=$(which q); d=$(dirname "$d"); source "$d"/qo "$@"; }
function qof () { d=$(which q); d=$(dirname "$d"); source "$d"/qof "$@"; }
function qoi () { d=$(which q); d=$(dirname "$d"); source "$d"/qoi "$@"; }
function qoil () { d=$(which q); d=$(dirname "$d"); source "$d"/qoil "$@"; }
function qol () { d=$(which q); d=$(dirname "$d"); source "$d"/qol "$@"; }
function qolf () { d=$(which q); d=$(dirname "$d"); source "$d"/qolf "$@"; }
function vqol () { d=$(which q); d=$(dirname "$d"); source "$d"/vqol "$@"; }


#
# Wrap up
#


# Mix in ZProfile Extensions like for Sh Path, PushD, AltPwdS, & Ssh Aliases

if [[ -e ~/.ssh/zprofile ]]; then source ~/.ssh/zprofile; fi


# Prompt how to Scp

date
echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."
echo


# Calm the Ls Light-Mode Colors

if dircolors >/dev/null 2>&1; then  # for Linux
    eval "$(dircolors <(dircolors -p |sed 's,1;,0;,g'))"  # 'no bold for light mode'
fi


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot-zprofile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

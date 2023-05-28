# ~/.zprofile


# Load Ssh Keys and grow Sh Path

ssh-add ~/.ssh/*id_rsa 2>/dev/null

export PATH=$PATH:$HOME/bin


# Name the next Pwd:  -, .., ~

alias -- -='echo + cd - >&2 && cd -'
alias ..='echo + cd .. >&2 && cd .. && (dirs -p |head -1)'
alias ~='echo + cd "~" >&2 && cd ~ && (dirs -p |head -1)'

: setopt AUTO_CD  # Zsh  # lacks tab-completion
: shopt -s autocd 2>/dev/null  # Bash


# Preview ! History Expansion in Zsh Input Lines

setopt histverify  # a la Bash:  shopt -s histverify

: stty -ixon  && : 'define ⌃S to undo ⌃R, not XOff'  # history-incremental-search'es


# Autocorrect some inputs
# Work inside the Terminal a la macOS > Preferences > Keyboard > Replace works outside

function :/ { echo ':/  ⌃ ⌥ ⇧ ⌘ # £ ← ↑ → ↓ ⎋ ⋮' |tee >(pbcopy); }
function :scf () { echo 'supercalifragilisticexpialidocious' |tee >(pbcopy); }
function :shrug () { echo '¯\_(ツ)_/¯' |tee >(pbcopy); }


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


# Work the deep magic inside the Sh Process that Git SubProcesses can't reach

function qcd () { source $(dirname $(which q))/qcd.source "$@"; }
function qp () { source $(dirname $(which q))/qp.source "$@"; }
function zh () { source $(dirname $(which q))/zh.source "$@"; }


#
# Wrap up
#


# Mix in ZProfile Extensions like for Sh Path, PushD, AltPwdS, & Ssh Aliases

if [[ -e ~/.ssh/zprofile ]]; then source ~/.ssh/zprofile; fi


# Prompt how to Scp

date
echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."
echo


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot-zprofile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

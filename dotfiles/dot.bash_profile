# ~/.bash_profile


# Load Ssh Keys and grow Sh Path

ssh-add ~/.ssh/*id_rsa 2>/dev/null

export PATH=$PATH:$HOME/bin  # Ubuntu often does this for you


# Name the next Pwd:  -, .., ~

alias -- -='echo + cd - >&2 && cd -'
alias ..='echo + cd .. >&2 && cd .. && (dirs -p |head -1)'
alias ~='echo + cd "~" >&2 && cd ~ && (dirs -p |head -1)'

: setopt AUTO_CD  # Zsh  # lacks tab-completion
: shopt -s autocd 2>/dev/null  # Bash


# Preview ! History Expansion in Zsh Input Lines

shopt -s histverify  # a la Zsh:  setopt histverify

: stty -ixon  && : 'define ⌃S to undo ⌃R, not XOff'  # history-incremental-search'es


# Keep copies of the Sh Input lines indefinitely, in the order given

function precmd () {  # a la Zsh 'function precmd'
    local xs=$?
    HISTTIMEFORMAT= history 1 |cut -c8- >>~/.stdin.log  # no Pwd, no Date/Time, no Exit
    return $xs
}

PROMPT_COMMAND="precmd;$PROMPT_COMMAND"


# Autocorrect some inputs
# Work inside the Terminal a la macOS > Preferences > Keyboard > Replace works outside

function :/ { echo ':/  ⌃ ⌥ ⇧ ⌘ # £ ← ↑ → ↓ ⎋ ⋮' |tee >(pbcopy); }
function :scf () { echo 'supercalifragilisticexpialidocious' |tee >(pbcopy); }
function :shrug () { echo '¯\_(ツ)_/¯' |tee >(pbcopy); }


# Sandbox Python Extensions

function pips () {
    echo + source ~/.pyvenvs/pips/bin/activate >&2
    source ~/.pyvenvs/pips/bin/activate >&2
}


# Work the deep magic inside the Sh Process that Git SubProcesses can't reach

function qcd () { source $(dirname $(which q))/qcd.source "$@"; }
function qp () { source $(dirname $(which q))/qp.source "$@"; }
function zh () { source $(dirname $(which q))/zh.source "$@"; }

function qo () { (source $(dirname $(which q))/qo "$@"); }
function qof () { (source $(dirname $(which q))/qof "$@"); }
function qoi () { (source $(dirname $(which q))/qoi "$@"); }
function qoil () { (source $(dirname $(which q))/qoil "$@"); }
function qol () { (source $(dirname $(which q))/qol "$@"); }


#
# Wrap up
#


# Mix in Bash Profile Extensions like for Cd, Ssh, etc

if [[ -e ~/.ssh/bash_profile ]]; then source ~/.ssh/bash_profile; fi


# Prompt how to Scp

date
echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."
echo

source ~/.bashrc


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.bash_profile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

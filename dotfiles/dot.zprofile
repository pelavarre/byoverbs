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


# Keep copies of the Sh Input lines indefinitely, in the order given

type -f precmd >/dev/null  # a la Bash $PROMPT_COMMAND
if [[ $? != 0 ]]; then
    function precmd () {
        fc -ln -1 >>~/.stdin.log  # no Pwd, no Date/Time Stamp, no Exit Code
    }
fi


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


# Mix in ZProfile Extensions like for Cd, Ssh, etc

if [[ -e ~/.ssh/zprofile ]]; then source ~/.ssh/zprofile; fi


# Prompt how to Scp

date
echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."
echo


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.zprofile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

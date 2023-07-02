# ~/.bash_profile

# shellcheck disable=SC1090  # Can't follow non-constant source


# Load Ssh Keys and grow Sh Path

ssh-add ~/.ssh/*id_rsa 2>/dev/null

export PATH=$PATH:$HOME/bin  # Ubuntu often does this for you


# Name the next Pwd:  -, .., ~

alias -- -='echo + cd - >&2 && cd -'
alias ..='echo + cd .. >&2 && cd .. && (dirs -p |head -1)'
alias ~='echo + cd "~" >&2 && cd ~ && (dirs -p |head -1)'

: setopt AUTO_CD  # Zsh  # lacks tab-completion
: shopt -s autocd 2>/dev/null  # Bash


# Make the Editing of Command-Line Input History less painful

shopt -s histverify  # Preview ! History Expansion  # a la Zsh:  setopt histverify

: stty -ixon  # 'define ⌃S to undo ⌃R, not XOff'  # history-incremental-search'es


# Autocorrect some inputs
# Work inside the Terminal a la macOS > Preferences > Keyboard > Replace works outside

function /: { echo ':/  ⌃ ⌥ ⇧ ⌘ # £ ← ↑ → ↓ ⎋ ⋮' |tee >(pbcopy); }
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


# Work the deep magic inside the Sh Process that Git SubProcesses can't reach,
# provided that $(which q) is a Sh File, not a Sh Func

bin=$(which q)
bin=$(basename "$bin")

function bh () { source "$bin"/bh.source "$@"; }  # HistTimeForm~ history
function fh () { cat ~/.*.log; }

function qcd () { source "$bin"/qcd.source "$@"; }  # cd
function qp () { source "$bin"/qp.source "$@"; }  # popd

function eqol () { source "$bin"/eqol "$@"; }  # "${ALTPWDS[@]}"
function qo () { source "$bin"/qo "$@"; }
function qof () { source "$bin"/qof "$@"; }
function qoi () { source "$bin"/qoi "$@"; }
function qoil () { source "$bin"/qoil "$@"; }
function qol () { source "$bin"/qol "$@"; }
function vqol () { source "$bin"/vqol "$@"; }


#
# Wrap up
#


# Mix in Bash_Profile Extensions like for Sh Path, PushD, AltPwdS, & Ssh Aliases

if [[ -e ~/.ssh/bash_profile ]]; then source ~/.ssh/bash_profile; fi


# Prompt how to Scp

date
echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."
echo


# Run Bash R C now, in case not before

source ~/.bashrc


# Calm the Ls Light-Mode Colors

if dircolors >/dev/null 2>&1; then  # for Linux
    eval "$(dircolors <(dircolors -p |sed 's,1;,0;,g'))"  # 'no bold for light mode'
fi


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.bash_profile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

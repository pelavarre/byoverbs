# ~/.zprofile

# shellcheck disable=SC1090  # Can't follow non-constant source
# shellcheck disable=SC1091  # Not following, Does not exist, No such file


# Revert enough Zsh back to the Classic Bash Design

# + : bracket; bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste
setopt interactive_comments
setopt no_no_match


# Grow Sh Path

export PATH=$PATH:$HOME/bin


# Name the next Pwd:  -, .., ~

alias -- -='echo + cd - >&2 && cd -'

function . { if [ $# -eq 0 ]; then open .; else source "$@"; fi; }
alias ..='echo + cd .. >&2 && cd .. && (dirs -p |head -1)'
alias ~='echo + cd "~" >&2 && cd ~ && (dirs -p |head -1)'

: setopt auto_cd  # Zsh  # lacks tab-completion
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


alias %%='echo -n "%% # £   ⎋ ⌃ ⌥ ⇧ ⌘ Fn   ← ↑ → ↓ ⇥ ⌫ ⏎   ; ⋮ ☰ ⬅️  ⬆️  ➡️  ⬇️  ·" |tee >(pbcopy) && echo'

function .exit() { echo + exit $? >&2; }  # most classic Sh rejects .exit as 'not a valid id'

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


# Lock Python Extensions inside a Py VEnv Sandbox

function pips () {
    echo + source ~/.pyvenvs/pips/bin/activate >&2
    source ~/.pyvenvs/pips/bin/activate >&2
}


# Work the deep magic inside the Sh Process that Child Subprocesses can't reach

function .bracket () {  # takes 1 Line of Paste at a time
    echo "+ : bracket; bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste"
    bind 'set enable-bracketed-paste off' 2>/dev/null  # at Bash
    unset zle_bracketed_paste  # at Zsh
}


#
# Wrap up
#


# Calm the Ls Light-Mode Colors

if dircolors >/dev/null 2>&1; then  # for Linux
    eval "$(dircolors <(dircolors -p |sed 's,1;,0;,g'))"  # 'no bold for light mode'
fi


# Mix in LocalHost ZProfile for Sh Path, PushD, AltPwdS, Ssh Aliases, Zsh BindKey, etc

if [[ -e ~/.ssh/zprofile ]]; then source ~/.ssh/zprofile; fi

bindkey '\e[1;3D' backward-word
bindkey '\e[1;3C' forward-word

: # export PATH=$PATH:$HOME/...
: # pushd ~/Desktop >/dev/null
: # if ! ssh-add -l >/dev/null; then ...
: # function ... () { set -x; date; caffeinate -s ssh -A ...; echo "+ exit $?"; ...

: # bindkey -s '^[OP' '^Abindkey |grep '\''".*".*".*"$'\'' ^J'


#
# Last of all
#


# Prompt how to Scp

date
echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."

if ! uptime |grep days, >/dev/null; then
    echo
    echo '+ uptime.py --pretty  # while less than a day'
    uptime.py --pretty
fi

echo


# Shrug off more Sourcelines added later

return


# Git-Track rejected Python install patches
#
#   PATH="/Library/Frameworks/Python.framework/Versions/3.14/bin:${PATH}"
#   export PATH
#


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot-zprofile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

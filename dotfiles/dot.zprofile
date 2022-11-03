# ~/.zprofile

_='''
usage: macOS Terminal > Shell > New Window > New Window With Profile

choose preferences for each new Zsh session
'''


# Fetch Keys and grow the Path

ssh-add ~/.ssh/*id_rsa 2>/dev/null

export PATH=$PATH:/Library/Frameworks/Python.framework/Versions/3.11/bin
export PATH=$PATH:$HOME/bin


# Abbreviate the next Pwd

alias -- -='echo + cd - >&2 && cd -'
alias ..='echo + cd .. >&2 && cd .. && (dirs -p |head -1)'
alias ~='echo + cd "~" >&2 && cd ~ && (dirs -p |head -1)'

: setopt AUTO_CD  # Zsh  # lacks tab-completion
: shopt -s autocd 2>/dev/null  # Bash


# Copy-edit Zsh Funcs from GitHub PELaVarre 'byoverbs/bin/'

function qcd () {
    echo + 'cd $(git rev-parse --show-toplevel && ...)' >&2
    git rev-parse --show-toplevel \
        && cd $(git rev-parse --show-toplevel) \
        && (dirs -p |head -1)
}

function qp () {
    echo '+ popd >/dev/null' >&2
    popd >/dev/null

    echo '+ (dirs -p |head -1)'
    (dirs -p |head -1)

    if [[ -e .git/ ]]; then
        echo '+ git rev-parse --abbrev-ref HEAD'
        git rev-parse --abbrev-ref HEAD
    fi
}

function zh() {  # for Zsh, not for Bash
    (
        set -xe
        HISTTIMEFORMAT='%b %d %H:%M:%S  ' history 0  # Bash takes no 0 here
    )
}


# Keep copies of the Sh Input lines indefinitely, in the order given

type -f precmd >/dev/null
if [[ $? != 0 ]]; then
    function precmd () {
        fc -ln -1 >>~/.zsh_precmd.log
    }
fi


# Sandbox Python Extensions

function pips () {
    echo + source ~/.pyvenvs/pips/bin/activate >&2
    source ~/.pyvenvs/pips/bin/activate >&2
}



# Authorize ZProfile Extensions

if [[ -e ~/.ssh/zprofile ]]; then
    source ~/.ssh/zprofile
fi


# Choose the first Pwd, and suggest Scp

: pushd ~ >/dev/null  # default at Mac
pushd ~/Desktop >/dev/null  # thus, at:  qp
pushd ~/Public/byoverbs >/dev/null  # thus, at:  ..

echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."
echo


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot-zprofile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

# ~/.zprofile

_='''
usage: macOS Terminal > Shell > New Window > New Window With Profile

choose preferences for each new Zsh session
'''


# Grow the Path, choose the first Pwd, and suggest Scp

export PATH=$PATH:/Library/Frameworks/Python.framework/Versions/3.11/bin
export PATH=$PATH:$HOME/bin

ssh-add ~/.ssh/*id_rsa 2>/dev/null

pushd ~/Public/byoverbs >/dev/null

echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."
echo


# Abbreviate the next Pwd

alias -- -='echo + cd - >&2 && cd -'
alias ..='echo + cd .. >&2 && cd .. && (dirs -p |head -1)'
alias ~='echo + cd "~" >&2 && cd ~ && (dirs -p |head -1)'

: setopt AUTO_CD  # Zsh  # lacks tab-completion
: shopt -s autocd 2>/dev/null  # Bash

function qcd () {
    echo + 'cd $(git rev-parse --show-toplevel)' >&2
    cd $(git rev-parse --show-toplevel)
    dirs -p |head -1
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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot-zprofile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

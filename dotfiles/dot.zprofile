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


# Keep copies of the Sh Input lines indefinitely, in the order given

type -f precmd >/dev/null
if [[ $? != 0 ]]; then
    function precmd () {
        fc -ln -1 >>~/.zsh_precmd.log
    }
fi


# Emulate the Autocorrections of macOS > System Preferences > Keyboard > Replace

function /: { echo '/: ⌃ ⌥ ⇧ ⌘ # £ ← ↑ → ↓ ⇧ ⋮ ⌃ ⌘ ⌥ ⎋' |tee >(pbcopy); }

function :shrug: () { echo '¯\_(ツ)_/¯' |tee >(pbcopy); }
function :scf: () { echo 'supercalifragilisticexpialidocious' |tee >(pbcopy); }


# Sandbox Python Extensions

function pips () {
    echo + source ~/.pyvenvs/pips/bin/activate >&2
    source ~/.pyvenvs/pips/bin/activate >&2
}


# Source Zsh Funcs from a LocalHost Clone of GitHub PELaVarre 'byoverbs/bin/zprofile'

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


# Authorize ZProfile Extensions

if [[ -e ~/.ssh/zprofile ]]; then
    source ~/.ssh/zprofile
fi


# Choose the first Pwd, and suggest Scp

: pushd ~ >/dev/null  # default at Mac
pushd ~/Desktop >/dev/null  # thus, at:  qp
pushd ~/Public/byoverbs >/dev/null  # thus, at:  ..

cd demos/  # choose my $OLDPWD
cd - >/dev/null

echo "$(id -un)@$(hostname):$(dirs -p |head -1)/."
echo


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot-zprofile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

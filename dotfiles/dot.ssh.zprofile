# ~/.ssh/zprofile


# Bind ⌃X ⌃E without ⌃X E

EDITOR='pq xeditline'  # often runs inside 'source ~/.zprofile'  # consciously not-export'ed

autoload -U edit-command-line
zle -N edit-command-line
bindkey '^x^e' edit-command-line


# Load some Ssh Private Keys and not others

if ! ssh-add -l >/dev/null; then
    echo '# Ssh Private Keys not found by:  ssh-add -l'
fi


# Bring some Dirs more into focus than others

pushd ~/Desktop >/dev/null
pushd ~/Public/pylitfun >/dev/null


# Bring some Hosts more into focus than others

function localhost () { myssh-color -t localhost "$@" 'bash -i'; }

function myssh-color () {
    local rc h tints lo=57568 hi=65535  # lo is White mixed 12% with Black, as 16-bit

    tints=(  # White mixed with Black, Red, Green, Yellow, Blue, Magenta, Teal, as R G B
        "$lo $lo $lo"
        "$hi $lo $lo"
        "$lo $hi $lo"
        "$hi $hi $lo"
        "$lo $lo $hi"
        "$hi $lo $hi"
        "$lo $hi $hi"
    )

    if [[ "$2" == [0-6] ]]; then  # a Hostname of 0 1 2 3 4 5 6 means just show that Tint
        .osascript draw-on-color "$2" ${=tints[$2 + 1]}
        return 0
    fi

    h=$(printf '%s' "$2" |cksum)
    h=${h%% *}
    .osascript draw-on-color "$2" ${=tints[h / 1729 % 7 + 1]}  # 1729 is a Divisor of the Hash picked to keep our Hosts from colliding

    myssh "$@"
    rc=$?

    .osascript draw-on-color localhost 65535 65535 65535
    return $rc
}

function myssh () {
    (
        local rc
        export PATH=/opt/homebrew/bin:$PATH
        set -x

        caffeinate -s ssh -A "$@"
        rc=$?
        echo "+ exit $rc"

        date
        return $rc
    )
}


# Give voice to the F Keys before they find meaning

bindkey -s '^[OP' '^Aecho F1 ^J'
bindkey -s '^[OQ' '^Aecho F2 ^J'
bindkey -s '^[OR' '^Aecho F3 ^J'
bindkey -s '^[OS' '^Aecho F4 ^J'
bindkey -s '^[[15~' '^Aecho F5 ^J'
bindkey -s '^[[17~' '^Aecho F6 ^J'
bindkey -s '^[[18~' '^Aecho F7 ^J'
bindkey -s '^[[19~' '^Aecho F8 ^J'
bindkey -s '^[[20~' '^Aecho F9 ^J'
bindkey -s '^[[21~' '^Aecho F10 ^J'
bindkey -s '^[[23~' '^Aecho F11 chorded as ⌥F6 ^J'
bindkey -s '^[[24~' '^Aecho F12 ^J'
bindkey -s '^[[25~' '^Aecho ⇧F5 ^J'
bindkey -s '^[[26~' '^Aecho ⇧F6 ^J'
bindkey -s '^[[28~' '^Aecho ⇧F7 ^J'
bindkey -s '^[[29~' '^Aecho ⇧F8 ^J'
bindkey -s '^[[31~' '^Aecho ⇧F9 ^J'
bindkey -s '^[[32~' '^Aecho ⇧F10 ^J'
bindkey -s '^[[33~' '^Aecho ⇧F11 ^J'
bindkey -s '^[[34~' '^Aecho ⇧F12 ^J'

bindkey -s '^[OP' '^Abindkey |grep '\''".*".*".*"$'\'' ^J'


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.ssh.zprofile
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

# ~/.zshrc


# Calm the Sh Prompt

OLDPS1=$PS1

if [[ "$SHLVL" == 1 ]]; then
    export PS1=$OLDPS1
    export PS1='%% '
elif [[ "$SHLVL" == 2 ]]; then
    if [[ "$PS1" == '\$ ' ]]; then
        export PS1=$OLDPS1
        export PS1='%% '
    fi
fi


# Bold the Sh Input

# if ! :; then
if [ -t 2 ]; then
    PS1="$PS1%B"
    POSTEDIT=$'\e[m'  # '%b' to turn off '%B' doesn't work here
fi


# Keep copies of the Sh Input lines indefinitely, in the order given

if ! type -f precmd >/dev/null; then  # a la Bash $PROMPT_COMMAND
    function precmd () {
        fc -ln -1 >>~/.stdin.log  # no Pwd, no Date/Time Stamp, no Exit Code
    }
fi


# ZModLoad in your '~/.zshrc' not your '~/.zprofile'
# to duck out of 'failed to load module' 'symbol not found in flat namespace'

zmodload zsh/deltochar  # not yet found in Bash
bindkey "\ez" zap-to-char  # ⌥Z for Zsh, like Emacs, but ignores case and keeps char


# Look out mainly here for Bots jumping in to edit the Dot Files in your Home

:


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot-zshrc
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

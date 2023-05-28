# ~/.zshrc


# Calm the Sh Prompt

if [[ "$SHLVL" == 1 ]]; then
    export PS1='%% '
elif [[ "$SHLVL" == 2 ]]; then
    if [[ "$PS1" == '\$ ' ]]; then
        export PS1='%% '
    fi
fi


# Keep copies of the Sh Input lines indefinitely, in the order given

type -f precmd >/dev/null  # a la Bash $PROMPT_COMMAND
if [[ $? != 0 ]]; then
    function precmd () {
        fc -ln -1 >>~/.stdin.log  # no Pwd, no Date/Time Stamp, no Exit Code
    }
fi


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot-zshrc
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

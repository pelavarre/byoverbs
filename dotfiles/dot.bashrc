# ~/.bashrc

# shellcheck disable=SC1090  # Can't follow non-constant source


# Run their code if they did shove it into your Home

if [[ -e ~/.bashrc-theirs ]]; then
    source ~/.bashrc-theirs
    unalias l la ll 2>/dev/null
fi


# Calm the Sh Prompt

if [[ "$SHLVL" == 1 ]]; then
    export PS1='\$ '
elif [[ "$SHLVL" == 2 ]]; then
    if [[ "$PS1" == '%% ' ]]; then
        export PS1='\$ '
    fi
fi


# Keep copies of the Sh Input lines indefinitely, in the order given

function precmd () {  # a la Zsh 'function precmd'
    local xs=$?
    HISTTIMEFORMAT='' history 1 |cut -c8- >>~/.stdin.log  # no Pwd, no Time, no Exit
    return $xs
}

PROMPT_COMMAND="precmd;$PROMPT_COMMAND"


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.bashrc
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

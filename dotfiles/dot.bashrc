# ~/.bashrc

# shellcheck disable=SC1090  # Can't follow non-constant source


# Run their code if they did shove it into your Home

if [[ -e ~/.bashrc-theirs ]]; then
    source ~/.bashrc-theirs
    unalias l la ll 2>/dev/null
fi


# Calm the Sh Prompt

OLDPS1=$PS1
_=$OLDPS1

if [[ "$SHLVL" == 1 ]]; then
    export PS1='\$ '
elif [[ "$SHLVL" == 2 ]]; then
    if [[ "$PS1" == '%% ' ]]; then
        export PS1='\$ '
    fi
fi


# Bold the Sh Input

# if ! :; then
if [ -t 2 ]; then
    export PS1="\[\e[m\]$PS1\[\e[1m\]"
    function preexec_style () { printf '\e[m'; }  # as if in Zsh preexec_functions
    trap - DEBUG
    trap -- 'preexec_style' DEBUG
    trap - EXIT
    trap -- 'preexec_style' EXIT
fi


# Keep copies of the Sh Input lines indefinitely, in the order given

function precmd () {  # a la Zsh 'function precmd', run before each "$PS1"
    local xs=$?
    HISTTIMEFORMAT='' history 1 |cut -c8- >>~/.stdin.log  # no Pwd, no Time, no Exit
    return $xs
}

PROMPT_COMMAND="precmd;$PROMPT_COMMAND"


# Look out mainly here for Bots jumping in to edit the Dot Files in your Home

:


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.bashrc
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

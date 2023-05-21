# ~/.bashrc

if [[ "$SHLVL" == 1 ]]; then
    export PS1='\$ '
elif [[ "$SHLVL" == 2 ]]; then
    if [[ "$PS1" == '%% ' ]]; then
        export PS1='\$ '
    fi
fi

# posted into:  https://github.com/pelavarre/byoverbs/blob/main/dotfiles/dot.bashrc
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

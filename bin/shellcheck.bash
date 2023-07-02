#!/bin/bash

mkdir -p tmp/

if ! which shellcheck; then
    ls /usr/bin/shellcheck ||:
    echo 'ok by you? or do you want:  sudo apt install shellcheck'

    exit

fi


echo "calling ShellCheck on $(echo bin/shellcheck.bash bin/* |wc -w) + 4 files"


shellcheck bin/shellcheck.bash


cd bin/ || exit 1

for SHFILE in *; do
    if [[ "$SHFILE" == "__pycache__" ]]; then
        :
    elif [[ "$SHFILE" == "sh" ]]; then
        :
    elif [[ "$SHFILE" =~ ^[^.]*$ ]]; then
        shellcheck --shell=bash "$SHFILE"
    elif [[ "$SHFILE" =~ [.]bash$ ]]; then
        shellcheck --shell=bash "$SHFILE"
    else
        :
    fi
done

cd ../ || exit 1


cd dotfiles/ || exit 1

shellcheck --shell=bash dot.bash_profile dot.bashrc
shellcheck --shell=bash dot.zprofile dot.zshrc

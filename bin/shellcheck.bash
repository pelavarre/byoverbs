#!/bin/bash

mkdir -p tmp/

if ! which shellcheck; then
    ls /usr/bin/shellcheck ||:
    echo 'ok by you? or do you want:  sudo apt install shellcheck'

    exit

fi


echo "calling ShellCheck on $(echo bin/shellcheck.bash bin/* |wc -w) files"

shellcheck bin/shellcheck.bash


function _shellcheck_bin_file () {

    T="../tmp/$SHFILE.bash"
    echo '#!/bin/bash' >"$T"
    cat "../bin/$SHFILE" >>"$T"

    shellcheck "$T"
}


cd bin/ || exit 1

for SHFILE in *; do
    if [[ "$SHFILE" == "__pycache__" ]]; then
        :
    elif [[ "$SHFILE" == "sh" ]]; then
        :
    elif [[ "$SHFILE" == "zprofile" ]]; then
        :
    elif [[ "$SHFILE" =~ ^[^.]*$ ]]; then
        _shellcheck_bin_file "$SHFILE"
    elif [[ "$SHFILE" =~ [.]bash$ ]]; then
        _shellcheck_bin_file "$SHFILE"
    else
        :
    fi
done

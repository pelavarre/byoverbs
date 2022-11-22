#!/bin/bash

mkdir -p tmp/

if ! which shellcheck; then
    ls /usr/bin/shellcheck ||:
    echo 'and now running ahead, anyhow'

    exit

fi

echo "calling ShellCheck on $(echo demos/shellcheck.bash bin/* |wc -w) files"

shellcheck demos/shellcheck.bash

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

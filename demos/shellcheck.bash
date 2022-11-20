#!/bin/bash

mkdir -p tmp/

if ! which shellcheck; then

    exit

fi

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

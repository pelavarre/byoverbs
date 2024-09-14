#!/bin/bash

set -e


# Focus on one Py File

last=$#

py=p.py  # defaults it no Args
if [[ $last != 0 ]]; then
    py=${!last}  # copies the last Arg
fi

index=1
while [[ $index -le $last ]]; do
    arg=${!index}
    if [[ $arg =~ [.]py$ ]]; then
        py=$arg  # replaces with the first Dot-Py Arg

        break

    fi
    index=$((index + 1))
done


# Run some PyPi·Org Code-Review Bots against the Py File

(   set -xe

    echo "+ echo |python3 -m pdb $py"
    echo |python3 -m pdb $py

    black.bash $py
    flake8.bash $py
    mypy.bash $py
)


# Forward the Args, or the one Py File, to run as Python 3

if [ $# -eq 0 ]; then
    set -xe
    python3 $py
else
    set -xe
    python3 "$@"
fi


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/python3.bash
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

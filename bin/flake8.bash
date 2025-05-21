#!/bin/bash

set -e

# shellcheck disable=SC2088  # Tilde does not expand in quotes, but $HOME does
echo + '~/.pyvenvs/flake8/bin/flake8' \
    --max-line-length=999 --max-complexity 10 --ignore=E203,E704,W503 "$@"

~/.pyvenvs/flake8/bin/flake8 \
    --max-line-length=999 --max-complexity 10 --ignore=E203,E704,W503 "$@"

# --max-line-length=999  # Black max line lengths over Flake8 max line lengths
# --max-complexity 10  # limit how much McCabe Cyclomatic Complexity we accept
# --ignore=E203  # Black '[ : ]' rules over E203 whitespace before ':'
# --ignore=E704  # Black of typing.Protocol rules over E704 multiple statements on one line (def)
# --ignore=W503  # 2017 Pep 8 and Black over W503 line break before bin op

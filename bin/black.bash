#!/bin/bash

set -e

# shellcheck disable=SC2088  # Tilde does not expand in quotes, but $HOME does

echo + '~/.pyvenvs/black/bin/black' --line-length=101 "$@" >&2
~/.pyvenvs/black/bin/black --line-length=101 "$@"

# --line-length=101  # my 2024 Window Width, over PyPi·Org Black Default of 89 != 80 != 71

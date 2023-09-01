set -e
# shellcheck disable=SC2088  # Tilde does not expand in quotes, but $HOME does
echo + '~/.pyvenvs/mypy/bin/mypy' "$@" >&2
~/.pyvenvs/mypy/bin/mypy "$@"

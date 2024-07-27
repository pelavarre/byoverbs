#!/bin/bash

set -e


#
# usage: spellcheck.bash [ADVERB...]
#
# call ShellCheck, on Well-Known Sourcefiles, with Well-Known Options
#
# quirks:
#   works from knowledge of 'man shellcheck' and 'shellcheck --norc'
#
# examples:
#   make shellcheck
#   bin/shellcheck.bash
#   bin/shellcheck.bash -o all
#   bin/shellcheck.bash -o all --exclude=SC2230,SC2244,SC2248,SC2250
#   bin/shellcheck.bash -o all --exclude=...  # more like four exclusions
#


#
# Spell out the Well-Known Options in detail,
# except i only developed these, i forgot to call them, so we're all conventional now
#


if [[ "$*" == "-o all --exclude=..." ]]; then
    "$0" -o all --exclude=SC2230,SC2244,SC2248,SC2250
    exit
fi


#
# SC2230: 'which' is non-standard ...
#   Use builtin 'command -v' instead
#
# SC2244: Prefer explicit -n to check non-empty string
#   (or use =/-ne to check boolean/integer)
#
# SC2248: Prefer double quoting
#   even when variables don't contain special characters
#
# SC2250: Prefer putting braces around variable references
#   even when not strictly required
#

#
# -x, --external-sources  Allow 'source' outside of FILES
#


#
# Suggest trying Linux with Apt Install ShellCheck, if missing
#

mkdir -p tmp/

if ! which shellcheck; then
    ls /usr/bin/shellcheck ||:
    echo 'ok by you? or do you want:  date && time  sudo apt install shellcheck'
    exit
fi


#
# Trace Sh Args if present
#


if [[ $# != 0 ]]; then
    echo "calling with Sh Args:  shellcheck" "$@"
fi


#
# Walk through categories of well-known Sourcefiles
#


echo "calling ShellCheck on $(echo bin/shellcheck.bash bin/* |wc -w) + 4 files"


(set -xe; shellcheck --norc bin/shellcheck.bash "$@")


cd bin/ || exit 1

for SHFILE in *; do
    if [[ -d "$SHFILE" ]]; then  # skips, if dir
        :
    elif [[ "$SHFILE" == bash_profile ]]; then
       (set -xe; shellcheck --norc --shell=bash "$@" -- "$SHFILE")
    elif [[ "$SHFILE" == zprofile ]]; then
       (set -xe; shellcheck --norc --shell=bash "$@" -- "$SHFILE")
    elif [[ "$SHFILE" =~ ^[^.]*$ ]]; then  # checks, if not hidden and no file ext
        (set -xe; shellcheck --norc --shell=bash "$@" -- "$SHFILE")
    elif [[ "$SHFILE" =~ [.]bash$ ]]; then  # checks, if explicitly Bash
        (set -xe; shellcheck --norc --shell=bash "$@" -- "$SHFILE")
    else
        :
    fi
done

cd ../ || exit 1


cd dotfiles/ || exit 1

(set -xe; shellcheck --norc --shell=bash dot.bash_profile dot.bashrc "$@")
# calls for Bash on Bash

(set -xe; shellcheck --norc --shell=bash dot.zprofile dot.zshrc "$@")
# calls for Bash while Zsh unknown

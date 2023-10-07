# shellcheck
# shellcheck --norc
# shellcheck -o all
# shellcheck -o all --exclude=SC2230,SC2244,SC2248,SC2250

#
# SC2230: which is non-standard ...
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


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/shellcheck.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

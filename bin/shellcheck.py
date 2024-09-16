# shellcheck
# shellcheck --norc
# shellcheck -o all
# shellcheck -o all --exclude=SC2230,SC2244,SC2248,SC2250


#
# SC2nnn: General shell script warnings and suggestions
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
# SC1nnn: Syntax errors and parsing issues
# SC2nnn: General shell script warnings and suggestions
# SC3nnn: POSIX shell-specific checks
# SC4nnn: Optional checks and special cases
# SC5nnn: Reserved for future use
# SC6nnn: Reserved for future use
# SC7nnn: Reserved for future use
#


#
# https://www.shellcheck.net/wiki/SC2025 etc
#
# SC1090:  # Can't follow non-constant source
# SC1091:  # Not following, Does not exist, No such file
#
# SC2002:  # Explicit Cat
# SC2012:  # Use Find instead of Ls to better handle non-alphanum...
# SC2016:  # Expressions don't expand in single quotes, use double ...
# SC2046:  # Quote this to prevent word splitting
# SC2086:  # Double quote to prevent globbing and word splitting
# SC2088:  # Tilde does not expand in quotes, but $HOME does
# SC2145:  # Argument mixes string and array. Use * or separate ...
# SC2154:  # [Environment Variable] is referenced but not assigned
#


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/shellcheck.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

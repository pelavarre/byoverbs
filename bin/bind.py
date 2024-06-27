#!/usr/bin/env python3

r"""

bind -p |grep C-x |grep C-e  # Bash
bindkey |grep '...M"'  # Zsh
stty -a |grep '\^'
: see also 'macOS > Terminal > Settings > Keyboard > Use Option as Meta Key'

if ! bind 2>/dev/null; then
    :
elif bind 2>&1 |grep 'bind: warning: line editing not enabled' >/dev/null; then
    :
else
    ... only call Bind With Args inside here to live inside Don't-Worry-Be-Happy ...
fi

see also:  bin/bash.py
"""

import byotools as byo


byo.sys_exit()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/bind.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

#!/usr/bin/env python3

r"""
bind -p |grep C-x |grep C-e  # Bash
bindkey |grep '...M"'  # Zsh
stty -a |grep '\^'
stty all |grep -B1 '\^'  # macOS only
stty -ixon  && : 'define Control+S to undo Control+R, not XOFF'
stty cbreak  # implies 'stty ixon' at macOS, but not at Linux
: see also 'macOS > Terminal > Settings > Keyboard > Use Option as Meta Key'
"""

import byotools as byo


byo.sys_exit()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/stty.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

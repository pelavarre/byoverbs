#!/usr/bin/env python3

r"""
bind -p |grep C-x |grep C-e  # Bash
bindkey |grep '...M"'  # Zsh
stty -a |grep '\^'
: see also 'macOS > Terminal > Settings > Keyboard > Use Option as Meta Key'
"""

import byotools as byo


byo.sys_exit()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/bind.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

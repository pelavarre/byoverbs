#!/usr/bin/env python3

r"""
zsh -f

alias
bindkey
declare -f
whence -a which
whence -a whence

bind 'set enable-bracketed-paste off' 2>/dev/null || unset zle_bracketed_paste
setopt InteractiveComments 2>/dev/null
"""

import byotools as byo


byo.sys_exit()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/zsh.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

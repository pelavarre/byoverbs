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

May/2022 Zsh 5.9  # minor release date  # seen in Oct/2023 Sonoma macOS 14, patched up to 14.6.1

"""

import byotools as byo


byo.sys_exit()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/zsh.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

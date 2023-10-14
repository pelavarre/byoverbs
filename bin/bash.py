#!/usr/bin/env python3

"""
bash --noprofile --norc

alias -p
bind -p
declare -f
which -a which

(set -x; set |grep ^.=; set |grep ^..=)  # shows a mostly empty namespace
diff -brpu <(export) <(set) |sort |grep -v '[ +]'  # shows Export's listed as Set's

bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste

echo a
echo b
echo c

export PS1="$PS1\n\\$ "

bash -c '( IFS=:; for P in $PATH; do ls -1 $P/python3* 2>/dev/null; done )'
"""

import byotools as byo


byo.sys_exit()


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/bash.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

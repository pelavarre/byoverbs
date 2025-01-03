#!/usr/bin/env python3

r"""
env -i bash --noprofile --norc

alias -p
bind -p
declare -f
which -a which

(set -x; set |grep ^.=; set |grep ^..=)  # shows a mostly empty namespace
diff -brpu <(export) <(set) |sort |grep -v '[ +]'  # shows Export's listed as Set's

bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste

echo \\\'\" \"\'\\n  # the \\ sometimes means \ and sometimes doesn't
V1=\"\'\\r; printf '%s\n' $V1

export PS1="$PS1\n\\$ "

bash -c '( IFS=:; for P in $PATH; do ls -1 $P/python3* 2>/dev/null; done )'

bash ~/.bash_profile  # screen for:  bind: warning: line editing not enabled
# see also:  bin/bind.py

: Aug/2004 Bash 2  # major release date
: Oct/2006 Bash 3.2  # minor release date
: : Nov/2014 Bash 3.2.57  # micro release date
: Jan/2019 Bash 5  # minor release date
: : Jan/2022 Bash 5.1.16  # micro release date

export HISTSIZE=-1  # Perplexity·Ai says these remove these limits?
export HISTFILESIZE=-1  # vs common defaults of =1000, =2000
# but that unlimiting HISTSIZE will raise your Bash Process Memory Size? significantly?

"""

import byotools as byo


byo.sys_exit()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/bash.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

# clear

#
# clear --above  # keep self on screen
# clear && read &&  # meanwhile
# cls && (set -xe; ...)
# clear |hexdump -C
# legacy of not clearing Scrollback
#

#
# ⌃L
# ⌘K
#
# reset
# clear
# tput clear
# stty sane
#

#
# $ setterm -reset |hexdump -C
# 00000000  1b 63 1b 5d 31 30 34 07  |.c.]104.|
# 00000008
# $
# $ uname
# Linux
# $
#


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/clear.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

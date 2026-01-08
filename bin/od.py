# od -A x -t x1 -v
# hexdump -C


# macOS
# % tput clear |hexdump -C |column -t
# 00000000  1b  5b  48  1b  5b  32  4a  |.[H.[2J|
# 00000007
# %

# Linux
# $ clear |od -A x -t x1z -v |column -t
# 000000  1b  5b  48  1b  5b  32  4a  1b  5b  33  4a  >.[H.[2J.[3J<
# 00000b
# $

# printf '\033[H''\033[2J'  # row-column-leap screen-erase
# printf '\033[3J''\033[H''\033[2J'  # scroll-erase but keep a scrolled copy of screen
# printf '\033[H''\033[2J''\033[3J'  # really do erase it all, like as ⌘K does


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/od.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

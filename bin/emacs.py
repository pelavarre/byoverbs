#!/usr/bin/env python3

"""
usage: emacs.py [-h] [-nw] [-Q] [--no-splash] [-q] [--script SCRIPT] [--eval COMMAND]
                [FILE ...]

read files, accept edits, write files, in the way of classical emacs

positional arguments:
  FILE                     a file to edit (default: None)

options:
  -h, --help               show this help message and exit
  -nw, --no-window-system  stay inside this terminal, don't open another terminal
  -Q, --quick              run as if --no-splash --no-init-file etc
  -q, --no-init-file       don't default to run '~/.emacs' after args
  --no-splash              start with an empty file, not a file of help
  --script SCRIPT          elisp commands to run after args (default: '/dev/null')
  --eval COMMAND           another elisp command to run after args and after --script

examples:

  emacs.py  # show these examples and exit
  emacs.py --h  # show help lines and exit (more available than -h)
  emacs.py --yolo  # do what's popular now

  emacs -nw --no-splash --eval '(menu-bar-mode -1)' ~/.emacs  # run and visit
  emacs -Q -nw --no-splash --eval '(menu-bar-mode -1)' ~/.emacs  # visit, don't run
"""

# todo: go for emacs -Q etc, when given args of just:  emacs.py --


import byotools as byo


byo.sys_exit()


# solve
#
#    % bash -c emacs </dev/null
#    Emacs: standard input is not a tty
#    Zsh: exit 1     bash -c emacs < /dev/null
#    %
#


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/emacs.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

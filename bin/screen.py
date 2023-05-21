#!/usr/bin/env python3

_ = r"""

T=Tag screen -S $T -L -Logfile $T.screen
T=Tag && screen -S $T -L -Logfile $T.screen script $T.script


#

cd ~/Downloads/
echo rm -fr Session.*
rm -fr Session.*

pwd
ls
screen -ls ||:  # perhaps No Sockets found

screen -S Session
screen -X logfile Session.screen
screen -X log on

: screen -S Session -L -Logfile Session.screen  # all in one line, at Linux (not Mac)

echo $SHELL $$  # see what Shell you got from Screen

script Session.script  # slower to flush

echo $SHELL $$  # see what Shell you got from Script

export PS1='\$ '

⌃A ⌃D  # to disconnect

"""


_ = """

some combo can tell you what state you're in:  Default, Copy Mode, & in-between's

⌃A ⌃A
⌃A Esc
Return

"""


# todo: call it in a way that blocks its TERM=screen default, for Vim Py Def Orange


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/screen.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

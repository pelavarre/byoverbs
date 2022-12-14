#!/usr/bin/env python3

_ = r"""

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

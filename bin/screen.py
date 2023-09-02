#!/usr/bin/env python3


# 'screen.py -ls' of 1 Screen =>  # or:  screen -r


# python3 -i $(which screen.py) --
# pdb.pm()


import os
import pdb  # pdb.pm(), etc
import re
import shlex
import subprocess
import sys

... == pdb


# Require Sh Args

assert sys.argv[1:]  # ["--"] etc


# Call and trace:  screen -ls

shline = "screen -ls"
sys.stderr.write("+ {}\n".format(shline))
run = subprocess.run(
    shlex.split(shline), stdout=subprocess.PIPE, stderr=subprocess.PIPE
)

stdout = run.stdout.decode()
os.write(sys.stdout.fileno(), run.stdout)

stderr = run.stderr.decode()
os.write(sys.stderr.fileno(), run.stderr)

sys.stderr.write("+ exit {}\n".format(run.returncode))

if run.returncode:  # 0 at Linux when 1 or more Screen's found
    assert run.returncode == 1, run.returncode  # always 1 at Mac

assert run.stderr == b"", run.stderr


# Scrape the Stdout

strip = stdout.strip()
lines = strip.splitlines()
assert lines, lines

line_0 = lines[0]
if len(lines) == 1:
    if line_0.startswith("No Sockets found in /"):  # 0 Screens
        sys.exit()

if line_0 != "There are several suitable screens on:":  # Mac
    if line_0 != "There is a screen on:":  # Linux at 1 Screen
        assert line_0 == "There are screens on:", repr(line_0)  # Linux at more Screens

line_n = lines[-1]
m0 = re.match(r"^[0-9]+ Sockets? in /var/folders/.*/T/[.]screen[.]$", string=line_n)
if not m0:
    m1 = re.match(r"^[0-9]+ Sockets? in /run/screen/S-.*[.]$", string=line_n)
    assert m1, repr(line_n)  # Linux

# "There is no screen to be resumed."  # 'screen -r' at 0 Screens
# 'Type "screen [-d] -r [pid.]tty.host" to resume one of them.'  # 'screen -r' at N > 1


print()
print("choose one, while sorted from most to least fresh:")
print()

for line in lines[1:-1]:
    splits = line.split("\t")
    assert len(splits) in (3, 4), (splits, line)

    assert splits[0] == "", repr(splits[0])
    assert splits[-1] == "(Detached)", repr(splits[-1])

    sessionpath = splits[1]
    print("screen -r {}".format(shlex.quote(sessionpath)))

print()


... == r"""

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


... == """

some combo can tell you what state you're in:  Default, Copy Mode, & in-between's

⌃A ⌃A
⌃A Esc
Return

"""


# todo: call it in a way that blocks its TERM=screen default, for Vim Py Def Orange


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/screen.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

#!/usr/bin/env python3

"""
usage: screen.py [-h]

reconnect with the only detached session, else with one detached session chosen at random

options:
  -h, --help     show this help message and exit

quirks same as classic:
  steals ⌃A away, burying the work of ⌃A at ⌃A A
  appends more lines into the -L -Logfile $T.screen, doesn't start over
  defaults to flush faster than 'script $T.screen' does

quirks better than classic:
  starts by showing the disconnected & connected Screen Sessions
  doesn't forward trailing Blank Lines from its call of 'screen -ls', when no Sessions found
  does exit zero when one or more Disconnected Screen Sessions found
  does exit nonzero when no Screen Sessions found, or no Disconnected Screen Sessions found
  doesn't explain that macOS '-ls' always exits 1 vs Linux exits 1 when no Disconnected Sessions

easter eggs, same as classic:
  echo $STY  # to say you're inside a Screen Session or not
  ⌃A D  # to disconnect
  ⌃A ⎋  # to enter 'Copy Mode' else say 'Must be on a window layer'
  ⌃A ⎋ ⎋  # to exit 'Copy Mode' and say 'Copy mode aborted'

more easter eggs, same as classic:
  ⌃A ⇧| to Add Pane > Insert Right
  ⌃A Tab to move Cursor between Panes
  ⌃A C to launch a Shell in a new Pane
  ⌃A ⇧X to Close Pane

examples:
  screen.py --  # for to call 'screen -r' for you on one Screen Session
  T=session-name && T=$T screen -S $T -L  # macOS Apple Screen can't -Logfile $T.screen
  T=session-name && T=$T screen -S $T -L -Logfile $T.screen  # Linux can -Logfile
  screen -X hardcopy -h ~/s1.screenlog
"""

# ⌃B D to disconnect Shell TMux, a la ⌃A D for Shell Screen
# $TMUX to find enclosing Shell TMux, a la $STY for enclosing Shell Screen
# tmux attach, a la screen -r for Shell Screen
# tmux capture-pane -S -
# tmux save-buffer ~/t.tmux

# todo: call 'screen' but don't give us TERM=screen like for Vim Py Def Orange

# code reviewed by people and by Black, Flake8, Mypy-Strict, & Pylance-Standard


from __future__ import annotations  # backports new Datatype Syntaxes into old Pythons

import __main__
import random
import re
import shlex
import subprocess
import sys
import textwrap


def main() -> None:
    """Run from the Shell Command Line"""

    doc = __main__.__doc__
    assert doc, (doc,)

    graf = doc[doc.index("examples:") :]
    testdoc = textwrap.dedent("\n".join(graf.splitlines()[1:])).strip()

    if not sys.argv[1:]:
        print()
        print(testdoc)
        print()
        sys.exit()

    if sys.argv[1:] != ["--"]:
        print(doc.strip())
        sys.exit()

    screen_reconnect()


def screen_reconnect() -> None:
    """Reconnect with the only Detached Session, else with one Detached Session chosen at random"""

    stdout = subprocess_run_screen_ls_loudly()

    strip = stdout.strip()
    lines = strip.splitlines()
    assert lines, lines

    scrape_frame(lines)
    shlines = scrape_reconnect_shlines_from_body(lines)

    if not shlines:  # if no Detached Sessions found
        sys.exit(1)  # exits 1 for no Detached Screen Sessions found
        return

    shline = random.choice(shlines)
    if shlines[1:]:
        print()
        print("one random choice is")

    print()
    print(f"+ {shline}")

    argv = shlex.split(shline)
    run = subprocess.run(argv)  # mutate Sys Std In/ Out/ Err

    if run.returncode:
        print(f"+ exit {run.returncode}")
        sys.exit(run.returncode)


def subprocess_run_screen_ls_loudly() -> str:
    """Call and trace:  screen -ls"""

    shline = "screen -ls"
    sys.stderr.write("+ {}\n".format(shline))

    run = subprocess.run(shlex.split(shline), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout = run.stdout.decode()
    stderr = run.stderr.decode()
    rstrip = (stdout + stderr).rstrip()

    print(rstrip)

    if not run.returncode:  # 0 at Linux when one or more Sessions found
        print("+")
    else:
        print(f"+ exit {run.returncode}")
        assert run.returncode == 1, run.returncode  # 1 at Mac no matter if Sessions found or not

    assert not stderr, (stderr,)

    return stdout

    # todo: stop delaying Stderr till after all Stdout


def scrape_frame(lines: list[str]) -> None:
    """Scrape the Head and Tail Lines"""

    # Scrape the Head Line

    line_0 = lines[0]
    if len(lines) == 1:
        if line_0.startswith("No Sockets found in /"):  # 0 Sessions found
            sys.exit(1)  # exits 1 for no Screen Sessions found

    if line_0 != "There are several suitable screens on:":  # old Mac
        if line_0 != "There is a screen on:":  # Linux at 1 Screen
            assert line_0 == "There are screens on:", repr(line_0)  # Linux at more Screens

    # Scrape the Tail Line

    line_n = lines[-1]
    m0 = re.match(r"^[0-9]+ Sockets? in /var/folders/.*/T/[.]screen[.]$", string=line_n)
    if not m0:
        m1 = re.match(r"^[0-9]+ Sockets? in /run/screen/S-.*[.]$", string=line_n)
        assert m1, repr(line_n)  # Linux

    # No Sockets found in /var/folders/6j/yj_0gg5d7dg02zhp0vwfx0580000gp/T/.screen.\n
    # 1 Socket in /var/folders/6j/yj_0gg5d7dg02zhp0vwfx0580000gp/T/.screen.
    # 2 Sockets in /var/folders/6j/yj_0gg5d7dg02zhp0vwfx0580000gp/T/.screen.

    # No Sockets found in /run/screen/S-triage.\n
    # 1 Socket in /run/screen/S-triage.
    # 2 Sockets in /run/screen/S-triage.


def scrape_reconnect_shlines_from_body(lines: list[str]) -> list[str]:
    """Scrape the Body Lines to form Alt Lines and print them"""

    shlines = list()
    body_lines = lines[1:-1]

    once = False
    for line in body_lines:
        splits = line.split("\t")
        assert len(splits) in (3, 4), (splits, line)

        assert splits[0] == "", repr(splits[0])

        if splits[-1] != "(Attached)":
            assert splits[-1] == "(Detached)", repr(splits[-1])

            if not once:
                once = True

                if body_lines[1:]:
                    print()
                    sys_platform = sys.platform
                    if sys_platform == "darwin":
                        print("sorted from least to most recently created is")
                    else:
                        print("sorted from least to most recently detached or attached is")

            sessionpath = splits[1]

            dent = 4 * " "
            shline = "screen -r {}".format(shlex.quote(sessionpath))

            if body_lines[1:]:
                print(dent + shline)

            shlines.append(shline)

    return shlines


#
# Run from the Shell Command Line, if not imported
#


if __name__ == "__main__":
    main()


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/screen.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

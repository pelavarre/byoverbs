# byoverbs/futures.md

What might should I make next for us soon?

That Question interests me lots, so this File collects Answers to that Question.
This File looks like English, but it's not very readable per se.
It lives up inside my Top Dir so it's easy for me to find and grow.
Its idea is more that you glance at it or search through it and then we talk it over.
Or more likely you say something and then I come here to find the relevant note I wrote before you spoke.

contents
+ Urgencies
+ Demos
+ Mobile Workflow
+ Notes
+ Python Workflow
+ Bash Verbs
+ + Grow Scope
+ + Pwnme
+ + Screen Bash
+ Py Verbs
+ + Cp Py
+ + Dd Py
+ + Emacs & Less & Vim Py
+ + Emacs Py
+ + Git Py
+ + Grep Py
+ + Head Py
+ + Less Py
+ + Ls Py
+ + Open Py
+ + Python Py
+ + Vim Py
+ + Whence Py
+ Read Me
+ Copied from

## Urgencies

bugs in their Code that i can't afford to fix, above nice-to-have features to add

## Demos

demos/buttonfiles/
demos/keycaps.py - add import msvcrt
demos/morse.py - take . - Space/Return as input to show all matches, then less matches
demos/rpn.py

test Paste at Windows
    does it all come through as single Keystrokes in the same millisecond?

list deffed by Py File and not mentioned by that same Py File

import the ByoTools, don't just copy-edit fragments?

## Mobile Workflow

G Cloud shopt -s histverify

## Notes

curl -i, --include Http Response Headers such as Date of Doc
diff -Bbw

## Python Workflow

lint - list deffed by Py File and not mentioned by that same Py File

Vim/Emacs cuts of a whole Def

## Bash Verbs

### Grow Scope

solve numeric v non-numeric args

    a /
    a 1
    qspno 1
    qspno HEAD~1

### Pwnme

also called by:  make pwnme
could more or less volunteer and authorize the destructive prep of:  qc

### Screen Bash

more test and comments

some bug near to

    $ screen.bash
    ++ screen -r 1 Socket in /run/screen/S-pelavarre
    There is no screen to be resumed matching 1.
    $ screen -ls
    There is a screen on:
            2615111.pts-0.ubuntu-pelavarre     (11/09/2022 06:18:56 PM)        (Detached)
    1 Socket in /run/screen/S-pelavarre.
    $ screen.bash 1


## Py Verbs

### Cp Py

kin to Mv Py
accept 0 or 1 args
cp -ipR with 'git config user.initials' and date-time last modified

### Dd Py

dd some large file, to keep it easy to raise free space quickly

### Emacs & Less & Vim Py

solve Bash C-x C-e first, editing inline in the way of Zsh
prompt with how to undo

pattern of search-replace that keeps lit the searches and the replaces
history of what was replaced, what was deleted
edit as bookmark, reached by Undo

### Emacs Py

syntax coloring without coloring trailing spaces past end-of-line

### Git Py

more abbreviation/ promotion of

    git log --no-decorate --pretty=format:'%h%x09%an%x09%cd%x20%x09%s' \
        --author=$(git config user.email) |grep May |grep '2021 -'

    git show :1:FILENAME # base
    git show :2:FILENAME # theirs
    git show :3:FILENAME # ours
    git reflog
    git reset HEAD~1
    git rm -f ...

wrong accident redefine Origin where? how about: git push origin HEAD:origin/feature/foo

### Grep Py

separate runs of hits in one bucket or another more elegantly than extremely ad hoc

    cv |g : |gv '0:00:0[0123]' |g http |column -t \
        |(sleep 0.1 && awk '''
            BEGIN{print ""}
            {o=d; h=0+substr($4, 1, 2); d=(h >= 6) && (h < 18)}
            (o != d){print ""}
            {print}
        ''' && echo)

### Head Py

Mac Tail & Linux Head/Tail
do Not resolve such contradictions as:  -1 -2

### Less Py

run a command piped in
default closer to -FIRX

### Ls Py

ls.py --full-time
but with --ext=.py to show the source

in sorting by version, the version is y.m.d when it's nothing else?

dreams of sharing Sh Terminal space more fairly

    diff -urp <(echo $LESSOPEN) <(echo '| /usr/bin/lesspipe %s')

### Open Py

print the last word by itself, such as 'ABC-12345' from http://jira/browse/ABC-12345
keep the session open till quit
strip trailing slash

### Python Py

give people

    rm -fr sandbox9/
    python3 -m venv --prompt SBOX9 sandbox9
    source sandbox9/bin/activate

### Vim Py

try loud insert mode that expires at arrows, when not fed, etc

solve evolving Vim vs

    :set listchars=tab:\\·,trail:·

solve Multi Buffer Vim, such as

    :nnoremap <space><space> :b <C-d>
    :nnoremap <BS> :b#<CR>
    :nnoremap <S-Tab> :bprevious<CR>
    :nnoremap <Tab> :bnext<CR>

### Whence Py

default to whence -a including Aliases & Funcs of Bash & Zsh

## Read Me

it's got an early index of source code in it, i might should catch that up

## Later Now
### 1 - Quickly Now

i gather notes here when they reach me, then later i spread them out above

+ the non-x Py at 'apt find git screen script ssh sudo' should go live
+ + as easily as already at:  bin/touch.py

+ mv.py should toggle itself off?
+ mv.py should stop freaking over trailing '/'
+ cp.py should work like mv.py

+ cal.py should give me 'cal && cal -m 1 2023' on 20/Dec
+ + but did give me 'cal && cal -m 12 2022'

+ mv.py should trace its calls of 'date +' and of 'ls -1rt'

+ tty stdin g should mean qo, else g -R $PWD

+ open.py of a thin decimal number should put that number into a recent web address
+ open.py session should stay open till Tty Eof, and log its work

+ give me a 'time.sleep' that invites me to quit it, like by pressing Return

+ 3 qp should work like qp && qp && qp

+ make remote 'cv' work - like push/pull 'scp.py --' from last Host found by Ssh

+ repeat 'mv.py --' to undo it, not to deepen it
+ loosen up 'ls.py' - look across last few days, and across top few of 'dir -p'

+ bin/md5sum vs bin/md5sum.bash

+ o=$OLDPWD  # for the sake of $o in command lines
+ compositional - o for run it in or on the $OLDPWD

+ cache requests get/post & subprocess run
+ dump & py grep & delete chosen sets of cache keys
+ grep cache keys by key or by value or by date/time stamp
+ grep.py for classic regex vs pygrep.py for py regex

+ keep more Terminal Windows in synch across input histories
+ stop losing timestamps on the first input lines of the morning

+ 'def unicode\_name' should find "EM" in place of "EOM"
+ eqgol qgiol qgol vqgol -> eol qoil vol, but only 'qoil' exists as yet
+ '|t 3' could mean '|tail -3'
+ 'dotfiles/bash\_profile'
+ screen for SyntaxErrors, and auto-repair needs 1 trailing ':' or a few '))'

### 2 - More

Git Commit Messages drafted, not pushed

    open.py: Auto-correct Paste Buffer if it's holding 1 over-precise Web Address

    ls.py: Ship usage: ls.py [-F]  # add '/' at 'd', '*' at 'x', '@' at '->', etc

    ls.py: Ship usage: ls.py [-R]  # walk deep down to show dirs in dirs

    .: Link the Tracked Files to Posted-Into/ Copied-From

    find.py: Ship usage: find.py [TOP ...]
    find.py: Ship usage: find.py [TOP ...] [-prune]

    echo.py: Ship usage: bash.py -c 'echo *.md' --py  # show how Sh calls Glob

Transcripts

    % cal.py --
    + cal
         March 2023
    Su Mo Tu We Th Fr Sa
              1  2  3  4
     5  6  7  8  9 10 11
    12 13 14 15 16 17 18
    19 20 21 22 23 24 25
    26 27 28 29 30 31

    no default trace of: cal -m 3
    and also its end-of-line spaces

Cal Py for 2022-10-19, 2022-11-07 looked wrong to me
    cal.py 2022-10-19  # should work, and offer min equivalent 'cal' lines
    cal.py 20221019  # should work, and offer min equivalent 'cal' lines

### 3 - Still more

demos/vi.py --  # X x ZZ etc
screenlog.0, typescript are both precedents - replaced, not appended
printf '\e[33m''yellow''\e[m\n'; printf '\e[38;5;130m''orange''\e[m\n'

>>> now
could expand itself to
>>> # now
>>> now = dt.datetime.now()
>>> print(now)
>>> print(repr(now))

likewise 'fromtimestamp(1685142348)' could mean the 'dt.datetime.' of that

don't fix it by default, make it easy to fix by hand as needed
    such as 'stty -ixon' for turning Control+S undo of Control+R on

do make infinite Sh Input history
    how about the Redis Query syntax
        for the extras of Stamp, Pwd, ReturnCode etc

do make a Vi Color mode that squeezes the punctuation to nothing
    bold could mean coined
    bold could also mean break/ continue/ return

much too much is wildly way too difficult in
    Sh Bash Vi Emacs Less Watch Script Screen TMux

### 4 - Yet more

curate a tracked history of |pq to say if 'len' means '-b', '-c', '-w', 'l' of '|wc'

catch the nonzero exit from qcaa to make extra backup of .git/COMMIT_EDITMSG

develop pqext.py, then fold it in
    --e short for --ext=.py to print the Py Code but don't run it

    chars = sys.stdin.read()
    words = chars.split()
    int_ = len(words)
    print(int_)

    chars = sys.stdin.read()
    bytes_ = chars.encode()
    int_ = len(bytes_)
    print(int_)

    chars = sys.stdin.read()
    lines = chars.splitlines()
    int_ = len(lines)
    print(int_)

    chars = sys.stdin.read()
    lines = chars.splitlines()
    items = list()
    for line in lines:
        items.append(line)
    chars_ = "\n".join(items) + "\n"
    sys.stdout.write(chars_)

    chars = sys.stdin.read()
    chars_ = chars
    if chars:
        chars_ = textwrap.dedent(chars) + "\n"
    sys.stdout.write(chars_)


write the 2nd half of the Sh History in LogFmt style
    x=0 t=2023-06-13T17:29:47.038436-07:00 p=jqdoe@linux-jqdoe-1:~/Public/byoverbs$


bh, fh, zh, qlf - take Sh Args as meaning pipe out through 'grep -i -e'


figure out where U+2028 Line-Separator marks enter the Os Copy-Paste Buffer


credit Vi Py for ⌃F ⌃B inside Insert/ Replace


breakpoint well inside a Stdin/ Stdout Sh Pipe Py Filter ??


### 5 - Fifth traunch

repeat count for I/R/A etc should be record/ replay macro

add an 'eqol' for 'vqol', as we have 'eqgl' for 'vqgl'

add shellcheck, and solve its complaints

    shellcheck dot.bash_profile dot.bashrc dot.zprofile dot.zshrc

back up my c*nfidential ~/.ssh/zprofile and ~/.ssh/bash_profile Files


### 6 - Sixth traunch

write up bugs/zsh.md
C-x C-e can't run ahead
advice for restoring the Bash experience in Zsh, e.g.,
    echo https://google.com/search?q=hello,+World%21

backport Typing | to G Cloud Shell Feb/2021 Python 3.9.2 of Oct/2020 Python 3.9
patch up the source as needed - git apply a diff

make regular breakpoints work inside pq.py
    for the case of Stdin Stdout both being PBuffer
        as well as they work inside examplecom.py

write examples & help for examplecom.py
add '|pq deslack' to convert the Slack Emoji Markup to Unicode
better help at:  bin/pq.py --

qcm, qcam near to:  git commit -m "wip - "$(qdno |awk -F/ "{print $NF}")
qla could drop the detail past the '@'


### 7 - Seventh traunch

reinvent this wheel

    qiksys.suspend_globals()
    qiksys.resume_globals()

like extend json.JSONEncoder to cover:  dt.datetime, dt.timedelta, set, tuple, ...

:

maybe maybe 'pwd.py' and 'py.py' and 'time.py' are no longer trouble?
https://pypi.org/project/py/ might always only be a Python 2 thing?

:

trace today's:  cal
more like:  cal -H 2023-01-18 -m 1 2023  # cal.py -H 2023018  # cal
so no matter day of month we always get the -H/-m/etc syntax template form

:

localhost macOS uptime.py --pretty

:

qo somefuncname |awk.py --
qo somefuncname |pq1 gather
qo somefuncname |pq1 spread  # OSError: [Errno 8] Exec format error: 'pbcopy'

getting Spread/ Gather backwards doesn't cue its own repair well

mv.py $F
cp.py $F
these should work - and they don't, not when i test:  mv.py p.py
especially:  mv.py p.py, mv.py cv

:

get our restart at 'pq' working as well as 'pq1'

get 'optionee' working well as an ⌃X⌃E Bash/Zsh Command-Line Editor

:

lsa - this comes in flavours, eg `lsa ~` often wants only not-hidden Files

the '-h' silently ignored by 'ls' in the absence of '-l'
we could drop it and mention we've dropped it

-A -rt rejected by ls.py
the '-d' ignored at:  ls.py -a -d -lh byoverbs/.git byoverbs/docs
ls.py could accept, especially with Arg, the choices of: ls -AdhlF -rt

-F rejected by ls.py

explain Linux Bash History splits Multiline Input by Line

:

VsCode + Black on """...""" too often triggers Flake8:  W291 trailing whitespace

calling Black needs preface of:  echo |python3 -m pdb
else the SyntaxError's aren't clickable inside VsCode

:

pandas, matplotlib, etc inside bin/p
demos/vi2.py could prompt for its ⇧Z⇧Q more like in lower right corner

:

each V should have its own File, so close out-of-order sequences Paste Buffer
demo for friends

fix 'cal.py --' at Mac to begin weeks on Mondays
fix 'cal.py --' to surface editable Y M D
    + cal -H 2024-01-16 -m 1 2024  # cal
    + ncal -b -M -H 2024-01-16 -m 1 2024  # ncal -b -M
add 'cal.py -v' to print reminder defs of -H YYYY-MM-DD, -m, -b, -M
    -H YYYMMDD place highlight, -M week from Monday, -b classic layout, -m MM month
teach 'cal.py -H ...' to reject such as '20240116'

:

ZZ from demos/vi2.py -q

grep out the Def that lack ' -> ' MyPy Auth

:

choking lately

    % date
    Thu Feb 15 19:05:34 PST 2024
    % ./demos/byoverbs.py
    Traceback (most recent call last):
      File "/Users/plavarre/Public/byoverbs/./demos/byoverbs.py", line 47, in <module>
        main()
      File "/Users/plavarre/Public/byoverbs/./demos/byoverbs.py", line 38, in main
        import byoverbs.bin.byotools as byo
      File "/Users/plavarre/Public/byoverbs/demos/byoverbs.py", line 85, in <module>
        import byoverbs
      File "/Users/plavarre/Public/byoverbs/demos/byoverbs.py", line 64, in <module>
        assert DIR_INDEX != (len(ABS_DIRS) - 1), (DIR_INDEX, DIR, len(sys.path), sys.path)
    AssertionError: (5, '/Users/plavarre/Public/byoverbs/demos', 6, ['/Library/Frameworks/Python.framework/Versions/3.12/lib/python312.zip', '/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12', '/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/lib-dynload', '/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages', '/Users/plavarre/Public', '/Users/plavarre/Public/byoverbs/demos'])
    %

Mac Terminal

    ⌘ R --> Toggle “Allow Mouse Reporting” option
    ⌥ ⌘ R --> Toggle “Use Option as Meta Key” option

Mac Terminal

    $ F=__pycache__/ && echo mv -i $F{,~$(date -r $F +%m%djqd%H%M)~} |tee /dev/tty |bash
    mv -i __pycache__/ __pycache__/~0312jqd1348~
    mv: cannot move '__pycache__/' to a subdirectory of itself, '__pycache__/~0312jqd1348~'
    $ F=__pycache__ && echo mv -i $F{,~$(date -r $F +%m%djqd%H%M)~} |tee /dev/tty |bash
    mv -i __pycache__ __pycache__~0312jqd1348~
    $ lsa

Mac Terminal

    qspno "" v $'' for Unicode such as:  $'demos/replit\302\267com'

    also do the Posted-Into/ Copied-From Stamps for those Tracked Files


### 8 - Eighth traunch

demos/script{1,2}.py echo ^M at each Return, etc

pass fresh make shellcheck
by calling for all source files together
and asking to presume --shell=bash
plus a bit of giving in to peer pressure as needed

PyLance Standard vs Py

    apt.py
    awk.py
    byotools.py
    date.py
    ls.py
    lsb_release.py
    open.py
    pbuffer.py
    pq.py
    pq1.py
    pq2.py
    pq3.py
    pwd..py
    time..py
    vi.py

PyLance Standard vs Sh

macOS Terminal Sh inadequate

    cat -n  # default of 6+2 Columns vs Vi 5+1 for 10_000 .. 99_0000 Lines
    cat -tv: wrong for \xA0 Nbsp

    cd old new  # works in Zsh, not Bash

    grep .  # in macOS Terminal when wider than the screen
    grep -n .  # same Issue

    sort: -k -1,-1: Invalid argument
        LC_ALL=C not the default at Linux, e.g.:  b1.bash, b2.bash, b.bash

    % echo "'" |xargs -n 1
    xargs: unterminated quote
    %

    sleep --until 18:04

    vim: +'set numberwidth=0'
    E487: Argument must be positive
    :g/ to show the line is a way to copy out line-number + wrapped text


### 9 - Ninth traunch - focused on PQ

pq

    pq tty  # Press ⌃C to quit, ⌃D to save & quit
        don't mention ⌃\ to quit faster, ⌃Z to pause

    pq for  # |awk 'length($0)<2000{print $0}'

    pq emoji hear

    pq --py  # could give pbpaste/ pbcopy context for obytes/ ibytes
        reduced to otext/ itext context whenever possible

    pq large number - could be quote timestamp around the world

    pq small number - could be like Awk to fetch that field
        tabs unless none found, then split

    pq filename could copy the filename into the Clipboard

    pq 'dict(enumerate(words))' is close to # grep -n .

    pq emoji lock
        runs as if emoji.py
        looks up "lock" inside UnicodeData Names

    pq --yolo chill of cv = jqdoe@example.com

    pq 'otext = itext.strip() + "\n"'  # removes blank Rows above and below
    pq 'oline = iwords[3] if iwords[3:] else ""  # |awk '{print $3}''

    block git-push till after work-for-hire Domain-Name deleted from Source Files
        fqdn = socket.getfqdn()
        dn = fqdn.partition(".")[-1]  # Domain Name of HostName

    pq # |ts, but with aware time and elapsed time, into dt.datetime.fromisoformat

    2 Args in pq '... #' '...' should run as 2 Lines, auto-completed
    etc for N Args at N >= 1

next Pq traunch

    pq wc
    … lines, words, chars, bytes
    with 'pq ht' or 'pq info' or not ...



    pq ls
    pq find
    pq find dot

    pathlib Path’s
    stat not hidden


    pq ls -AhlF



    nonnegative ints as iwords[n]
    negative ints as iwords[-n]
    x.y for y split() inside of x split("\t")


    pq dao
    insert into the tail -n +3 cat -n
    ordered better than muddled
    copied better than aliased


    pq easter
    import this # tail -n +3 cat -n
    future import braces

    pq .
    mmm, pq --py . does pick a most favoured, mmm

    debug pq emo .
    vs 143107 check count of:  pq --py emoji . 2>&1 |grep unicodedata |wc -l

    pq y

    pq tty
    pq cat

    #! env pq.py

pq

    rpn
        and how to rpn with Spaces in the Source vs
            ls |pq 'olines = olines if olines else [""]' 'oline = iline + "\n"' |c
            etc

    toggle between "... ..." and fussy ["...", "...""]

    compress Py Tracebacks

    ts abs, ts rel, ts z, & default to dedupe the ts rel
        ts to file, without ts to screen

    why do the costs of s s s s and a a a keep rising?
    explicit weights on hits:  4X 2X 1X for str-split, py-split, str-in
    8X for found in Comments vs not

pq vim tty

    test printf '\e]8;;http://example.com\e\\This is a link\e]8;;\e\\\n'


### 10 - Tenth traunch

Y@ lazy imports - np plt psycopg2 <= jupyterlab, psycopg2-binary, matplotlib

auto-format for Py, for Json, for Jql/Sql

why doesn't Tab completion work in Zsh when i write a new .py file into my Sh Path?
what does 'rehash' mean in Zsh?

unreadable Linux sym links when not found

poll often to back up fresh revisions of the Clipboard

run the Paste Buffer back through Black/ Flake8/ Python at each save?

screen.py vs mac

git show 55558ec  # rewrite Pq to show, and often run, whole brief python -c '''

choose from many popular forms of Tabular Markdown

    || ... || ... ||
    | ... | ... |
    ... | ...
    ... - ...
    \t
    '  '
    r'  *'

build my confidence in cp.py/ mv.py, stop falling back to

    F=t.txt && echo cp -ip $F{,~$(date -r $F +%m%djqd%H%M)~} |tee /dev/tty |bash
    F=t.txt && echo mv -i $F{,~$(date -r $F +%m%djqd%H%M)~} |tee /dev/tty |bash

screen  # FIXME: tell me again is it Screen or Script for low-latency no-wrap
https://github.com/pelavarre/pybashish/blob/main/.local/share/grep/files/tmux.bash
tmux => set -g 99999
Control B Right-Bracket [
toggle pane sync
set -w sync
Control B %  horizontal split and focus bottom  # a la Terminal > View > Split Lane
Control B "  vertical split - maybe two small then big, or big then two smalls
Control B Z  toggles occupy whole window
Control B 0  move focus
Control B 1  move focus
Control B 2  move focus
Control B W  interactive
these B Z are not ⇧B ⇧Z

do come fix:  cd ~/Public/byoverbs && b $(qdno |grep [.]py$)
with a more complete workaround of

    % rm -f __init__.py
    % ~/.pyvenvs/mypy/bin/mypy bin/bind.py
    Success: no issues found in 1 source file
    %
    % qcoh __init__.py
    + git checkout HEAD __init__.py
    Updated 1 path from 1738b75
    % ~/.pyvenvs/mypy/bin/mypy bin/bind.py
    bin/bind.py:21: error: Cannot find implementation or library stub for module named "byotools"  [import-not-found]
    bin/bind.py:21: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
    Found 1 error in 1 file (checked 1 source file)
    %

histogram of McCabe Complexity - weirdly piled up against 11 - 1, maybe?

cal.py option to call for more than two months, such as three!


## Copied from

Posted into:  https://github.com/pelavarre/byoverbs/blob/main/futures.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git

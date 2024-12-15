# byoverbs

Your workflow inside you Sh Terminal can run more smoothly, after you pour this kind of oil into it.
We give you Sh Scripts and Py Scripts to download, or to copy-edit, so they start helping you work.

## Show, not tell

Go ahead, add these Sh Verbs into your Sh Path,
out past the end where they don't disrupt any Sh Verbs you already have installed:

    mkdir ~/Public/
    cd ~/Public/

    rm -fr byoverbs/
    git clone https://github.com/pelavarre/byoverbs.git

    export PATH="${PATH:+$PATH:}$HOME/Public/byoverbs/bin"

Add them in, try them out, and you'll like them.

## Sh Scripts to fork

You can correct the wrong defaults of Sh Verbs.
They don't have to stay poorly thought out, unadapted to your workflow.

One example is the Sh Verb:  ls

Choose Args well,
when no Args given,
here '-hlaF -rt':

<pre>
% <strong>lsa</strong>
+ ls -hlAF -rt
total 0
drwxr-xr-x  13 jqdoe  staff   416B Dec 18 15:56 byoverbs/
%
</pre>

Choose Args well,
when 1 Arg given by typing 1 Arg Pattern,
here again '-hlaF -rt':

<pre>
% <strong>lsa *</strong>
+ ls -hlAF -rt byoverbs
total 72
-rw-r--r--    1 jqdoe  staff   4.3K Dec 18 15:56 Makefile
-rw-r--r--    1 jqdoe  staff   2.2K Dec 18 15:56 README.md
-rw-r--r--    1 jqdoe  staff   9.9K Dec 18 15:56 ReadmeSlowly.md
drwxr-xr-x  188 jqdoe  staff   5.9K Dec 18 15:56 bin/
drwxr-xr-x    7 jqdoe  staff   224B Dec 18 15:56 bugs/
drwxr-xr-x   29 jqdoe  staff   928B Dec 18 15:56 demos/
drwxr-xr-x    5 jqdoe  staff   160B Dec 18 15:56 docs/
drwxr-xr-x   10 jqdoe  staff   320B Dec 18 15:56 dotfiles/
-rw-r--r--    1 jqdoe  staff    11K Dec 18 15:56 futures.md
drwxr-xr-x    3 jqdoe  staff    96B Dec 18 15:56 pwnme/
drwxr-xr-x   12 jqdoe  staff   384B Dec 18 15:56 .git/
%
</pre>

Choose Args well,
when More Args given by typing out 2 Args in full,
here now '-dhlaF -rt':

<pre>
% <strong>lsa byoverbs/.git byoverbs/docs</strong>
+ ls -AdhlF -rt ...
drwxr-xr-x   5 plavarre  staff   160B Dec 18 15:56 byoverbs/docs/
drwxr-xr-x  12 plavarre  staff   384B Dec 18 15:56 byoverbs/.git/
%
</pre>
<=

Our examples above come from inside a setup for test, specifically running after

    mkdir dir/
    cd dir/
    git clone https://github.com/pelavarre/byoverbs.git

We keep the [code inside](bin/lsa) brutally simple on purpose.
The Sh Syntax is the Sh Syntax, but its thinking is reliably simple.
Add in '-hlAF -rt' as your defaults for 0 or 1 Args given.
Add in '-dhlAF -rt' as your default for More Args given.
And every time tell you what happened:
don't make you reread the Code,
not until you need to remember why it does what it does.

## Py Scripts to fork

Put your Examples, your Notes, and your Defaults for a Sh Verb
just one Choice away from you inside of a corresponding Py File.

Show your Examples for 'ls' when you call 'ls.py' with no Args,
as L S Dot Tab Return:

<pre>
% <strong>ls.py</strong>

ls.py -- |cat -  # runs the Code for:  ls -1
ls.py --py |cat -  # shows the Code for:  ls -1

ls.py -al  # runs the Code for:  ls -al
...
</pre>

Show your Notes, a heavier Man Page apart from Examples,
when you call 'ls.py' with the conventional '--h' Python Arg:

<pre>
% <strong>ls.py --h</strong>
usage: ls.py [--help] [-a] [-d] [-1 | -C | -m | -l | -lh | --full-time] [--py]
            [TOP ...]

show the files and dirs inside of dirs

positional arguments:
TOP          the name of a dir or file to show

options:
--help       show this help message and exit
-a           show '.*' hidden files and dirs too
-d           show the top dirs as items of a higher dir, not their insides
-1           show as one column of file or dir names (default for Stdout Pipe)
-C           show as columns of names (default for Stdout Tty)
-m           show as lines of comma separated names
-l           show as many columns of one file or dir per line
-lh          like -l but round off byte (B) counts to k M G T P E Z Y R Q etc
--full-time  like -l but detail date/time as "%Y-%m-%d %H:%M:%S.%f %z"
--py         show the code without running it
</pre>

Show your chosen Defaults,
when you call 'ls.py'
with the explicit conventional '--' Sh Arg that means no more Option Switches

<pre>
% <strong>ls.py -- |cat -</strong>
+ ls.py -1 --
byoverbs
%
</pre>


## Help us please

Please give us words to help more people start to get it

LinkedIn
> https://www.linkedin.com/in/pelavarre

Mastodon
> https://social.vivaldi.net/@pelavarre

Twitter
> https://twitter.com/intent/tweet?text=/@PELaVarre

## Copied from

Posted as:  https://github.com/pelavarre/byoverbs/blob/main/README.md
<br>
Copied from:  git clone https://github.com/pelavarre/byoverbs.git

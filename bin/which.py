_ = """

(PIPS) % which pip |sed "s,^$HOME/,~/,"
~/.pyvenvs/pips/bin/pip
(PIPS) %

$ which bh
$ declare -f bh
bh ()
{
    ( set -xe;
    HISTTIMEFORMAT='%b %d %H:%M:%S  ' history )
}
$

"""


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/which.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

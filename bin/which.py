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

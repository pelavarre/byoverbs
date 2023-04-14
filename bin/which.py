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

for P in $(echo $PATH |tr ': ' ' :'); do
  (cd $P/ && for F in $(echo .* *); do [ -x $F ] && echo $F; done);
done 2>/dev/null |grep boot |sort -u |cat -n |expand

# Zsh has to work the Echo to drop its notice of:  zsh: no matches found: .* (edited)

"""


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/which.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

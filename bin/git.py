_ = """

(
FF=bin/git.py
for F in $FF; do
    git blame --show-email $F |cut -d'(' -f2- |cut -d')' -f1 |cut -d'-' -f1-2 \
        |awk '{print $NF" "$0}' |awk '{$NF="";print}'
    done |sort -r |uniq -c |head
)


    "lgg": "git log --oneline --no-decorate -G {}",  # touches, aka Grep Source

    "lgs": "git log --oneline --no-decorate -S {}",  # changes, aka Pickaxe

$ git clean --help

       -e <pattern>, --exclude=<pattern>
           Use the given exclude pattern in addition to the standard ignore
           rules (see gitignore(5)).

       -n, --dry-run
           Don't actually remove anything, just show what would be done.

$

git clean -fdx -e /env

for X in 2022.11.22^{{tag,commit,tree}}; do
    it show --name-only $X
done |grep TaggerDate

git tag -l --format='%(taggerdate)  %(refname:short)'  2022.11.22

"""


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/git.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git

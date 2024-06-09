#!/bin/bash

set -x


#
# Try Auto-Completion's of revisions of the Os Copy-Paste Clipboard Buffer
#
# todo: Bash Filters race to reach 'set -x' inside a Sh Pipe
# todo: Msft GitHub $$ Copilot feels Zsh fixes this
#


:

# def iline_address_toggle_else
T=$(echo http://example.com |bin/pq.py --yolo)
T=$(echo http :// example . com |bin/pq.py --yolo)

:

# def iline_codereviews_to_diff_else
A=https://codereviews.purestorage.com/r/123456
T=$(echo $A/ |bin/pq.py --yolo)

:

# def iline_gdrive_to_share_else
A=https://docs.google.com/document/d/1YfkPxiJjVJXvf4G1-Ql6-IgxE7J22eEG2JzueNjl2T4
T=$(echo $A/edit#heading=h.xedwnjmaewr |bin/pq.py --yolo)

:

# def iline_jenkins_toggle_else
A=https://ourjenkins.dev.example.com
T=$(echo $A/ |bin/pq.py --yolo) # 1
A=http://ourJenkins/
T=$(echo $A/ |bin/pq.py --yolo) # 2  # only works for me onsite in work-for-hire

:

# def iline_jira_toggle_else
A=https://jira.example.com/browse/PROJ-123456
T=$(echo $A |bin/pq.py --yolo) # 1
A=PROJ-123456
T=$(echo $A |bin/pq.py --yolo) # 2  # only works for me onsite in work-for-hire

:

# json.dumps of json.loads  # j or jq
T=$(echo '{"//":[""]}' |bin/pq.py --py j)
T=$(echo '{"//":[""]}' |bin/pq.py jq |cat -)

:

echo "$T" >/dev/null  # shut up ShellCheck 'T appears unused'

:


#
# Try Auto-Completion's of tiny Py Fragements
#


function func() {
    (set -xe; bin/pq.py --py "$@") || echo + exit $?
}

echo +

func bytes len
func text len
func lines len
func words len

func join
func set
func split

func close
func dedent
func dent
func frame
func end
func lstrip
func reverse
func rstrip
func shuffle
func sort
func strip
func undent

func closed
func dedented
func dented
func ended
func framed
func lstripped
func rstripped
func reversed
func sorted
func shuffled
func stripped
func undented

# func jq  # nope, tested separately
func tac
# func tee  # |pq tee| could mean |tee /dev/tty |
func tail r
func uniq
func wc c
func wc l
func wc m
func wc w
func xargs

func a  # |pq a ...| could mean not |awk '{print $NF}' |
# func c  # bin/c did relate to:  pbpaste, cat -, cat - >/dev/null
# func d  # bin/d did relate to:  diff -brpu a b
# func e  # bin/e did relate to:  emacs -nw --no-splash --eval '(menu-bar-mode -1)'
# func f  # bin/f did relate to:  find .
# func g  # bin/g did relate to:  grep -e -h -i -n
# func h  # bin/h did relate to:  pbpaste, stty size, head
# func j  # nope, tested separately
# func p  # bin/p did relate to:  python3 -m pdb
# func q  # bin/q did relate to:  git
func s
# func t  # bin/t did relate to:  pbpaste, stty size, tail
func u
func x

# bin/:h did relate to:  short wide Landscape Terminal Sh
# bin/:v did relate to:  tall thin Portrait Terminal Sh
# bin/cv did relate to:  pbpaste, pbcopy
# bin/dt did relate to:  date stamp, measure time interval
# bin/fh did relate to:  cat ~/.*.log
# bin/mo did relate to:  less -FIRX
# bin/pq did relate to:  pq.py --yolo
# bin/sh did relate to:  /bin/shs
# bin/vp did relate to creating ./p.py more rapidly, fluidly
# bin/xd did relate to:  hexdump -C

# bin/cls did relate to the 'printf '\e[H\e[2J\e[3J' kind of:  clear
# bin/lsa did relate to:  ls -dhlAF -rt
func wcl
func xn1

echo +

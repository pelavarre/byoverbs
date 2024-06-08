#!/bin/bash

set -x


#
# Try Auto-Completion's of revisions of the Os Copy-Paste Clipboard Buffer
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

# # json.dumps of json.loads
T=$(echo '{"//":[""]}' |bin/pq.py --py jq)
T=$(echo '{"//":[""]}' |bin/pq.py jq |cat -)

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

func set

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
func tail r
func uniq
func wc c
func wc l
func wc m
func wc w
func xargs

func s
func u
func x
func xn1

echo +
